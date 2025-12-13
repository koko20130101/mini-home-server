import json
import base64
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Topic, Dialog, Agent, AIModels
from apps.users.models import Account
from .serializers import TopicSerializer
from common.ai_llm import call_deepseek
from common.ai_tts import text_to_audio
from common.utils import remove_emojis_and_special_chars


class AIConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.talkId = None
        self.topic = None
        self.agent = None
        self.llm = None
        self.tts = None

    @database_sync_to_async
    def get_topic(self, talkId, user):
        # 获取会话
        return Topic.objects.filter(talkId=talkId, user=user).first()

    @database_sync_to_async
    def add_message(self, role: str, content: str):
        return Dialog.objects.create(
            user=self.scope['user'],
            topic=self.topic,
            role=role,
            content=content,
        )

    @database_sync_to_async
    def history_message(self, user):
        # 获取最后10条对话记录
        try:
            return list(Dialog.objects.filter(user=user, topic=self.topic).values('role', 'content'))[-20:]
        except Exception as e:
            return []

    @database_sync_to_async
    def update_topic(self, content: str, last: str):
        # 更新话题数据
        obj = Topic.objects.filter(
            talkId=self.talkId, user=self.scope['user']).first()
        if obj.round == 0:
            # 如果是第一回合,记录用户的话做为摘要
            obj.abstract = content
        obj.last = last
        obj.round += 1
        obj.save()
        return obj

    @database_sync_to_async
    def get_AIModel(self, model_code):
        # 获取智能体
        return AIModels.objects.filter(model_code=model_code).first()

    @database_sync_to_async
    def get_agent(self, id):
        # 获取智能体
        return Agent.objects.filter(id=id).first()

    @database_sync_to_async
    def get_account(self, user):
        # 获取智能体
        return Account.objects.filter(user=user).first()

    @database_sync_to_async
    def update_account(self, user):
        # 减次数
        obj = Account.objects.filter(user=user).first()
        obj.ai_count -= 1
        obj.save()
        return obj

    async def connect(self):
        # 会话id
        self.talkId = self.scope.get("talkId", [None])[0]
        agent_id = self.scope.get("agent", [None])[0]
        llm_code = self.scope.get("llm", [None])[0]
        tts_code = self.scope.get("tts", [None])[0]

        await self.accept()

        user = self.scope['user']
        if user.is_authenticated:
            self.topic = await self.get_topic(self.talkId, user)
            account = await self.get_account(user)
            # 可对话次数
            if account.ai_count <= 0:
                await self.close(code=4002, reason='今日次数已用完')
                return
            # 从缓存中取出智能体、模型
            agent = cache.get('agent_' + agent_id)
            llm = cache.get(llm_code)
            tts = cache.get(tts_code)

            if agent:
                print('缓存agent')
                self.agent = agent
            else:
                self.agent = await self.get_agent(agent_id)
                cache.set('agent_' + agent_id, self.agent, 3*24*60*60)

            if llm:
                print('缓存llm')
                self.llm = llm
            else:
                self.llm = await self.get_AIModel(llm_code)
                cache.set(llm_code, self.llm, 3*24*60*60)

            if tts:
                print('缓存tts')
                self.tts = tts
            else:
                self.tts = await self.get_AIModel(tts_code)
                cache.set(tts_code, self.tts, 3*24*60*60)
        else:
            print('登录过期')
            await self.close(code=4001, reason='登录过期')

    async def disconnect(self, close_code):
        # Leave room group
        print('websocket 断开')

    # 向客户端发送数据
    async def send_message(self, type: str, text: str):
        await self.send(text_data=json.dumps({
            'type': type,
            'value': text
        }))

    # 接收数据
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['value']
        user = self.scope['user']

        if not self.topic:
            await self.close(code=4003, reason='会话ID为空')
            return
        if not user.is_authenticated:
            await self.close(code=4001, reason='登录过期')
            return
        # 得到历史聊天记录
        history = await self.history_message(user)
        history.insert(0, {'role': 'assistant', 'content': self.agent.prompt})
        history.append({'role': 'user', 'content': message})
        # 调用deepseek大模型
        llm_msg = call_deepseek(history, self.llm)

        if llm_msg != '':
            # 内容写入数据库
            await self.add_message('user', message)
            await self.add_message('assistant', llm_msg)
            # 向客户端发送AI生成的文本
            await self.send_message('string', llm_msg)
            # 更新话题内容
            await self.update_topic(message, llm_msg)
            # 更新账户
            await self.update_account(user)

            # 清除表情和特殊字符
            t2a_msg = remove_emojis_and_special_chars(llm_msg)

            # 调用minimax文本转语音
            await text_to_audio(t2a_msg, self.send_message)
