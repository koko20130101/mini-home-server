from rest_framework import viewsets, status, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.core.cache import cache
from common.permissions import IsOwnerOrReadOnly, IsOwner, ReadOnly
from apps.AI.models import Agent, Topic, Dialog, AIModels, DefyAgent, UserDefy, DefyDialog, Memory
from apps.AI.serializers import AgentSerializer, TopicSerializer, DialogSerializer, DefyAgentSerializer, UserDefySerializer, DefyDialogSerializer, MemorySerializer
from apps.users.models import Account
from common.utils import generate_random_string
from common.ai_llm import call_deepseek
from datetime import datetime
import threading
import re


def running_task(instance, history, llm):
    '''线程，用于调用大模型评估'''
    llm_msg = call_deepseek(history, llm)
    instance.result = llm_msg
    instance.defy_status = 2
    instance.save()


class AgentViewSet(viewsets.ModelViewSet):
    '''智能体视图集'''
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        classify__code = self.request.GET.get('classify__code')
        return Agent.objects.filter(classify__code=classify__code)


class TopicViewSet(viewsets.ModelViewSet):
    '''话题视图集'''
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ['agent']

    def get_queryset(self):
        '''获取当前用户的话题'''
        return Topic.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        '''创建或返回话题'''
        user = request.user
        agentId = request.data.get('agentId')
        newTopic = request.data.get('newTopic')

        if not agentId:
            return Response({'msg': '请选择聊天对象'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        instance = self.filter_queryset(
            self.get_queryset()).filter(user=user, agent=agentId).last()

        if instance:
            # 返回话题
            serializer = self.get_serializer(instance)
            if newTopic and instance.round == 0:
                return Response(serializer.data,  status.HTTP_200_OK)
            elif not newTopic:
                return Response(serializer.data,  status.HTTP_200_OK)

        # 创建新话题
        serializer = self.get_serializer(
            data={**request.data, 'user': user.id})
        if serializer.is_valid():
            agent = Agent.objects.filter(id=agentId).first()
            serializer.save(talkId=generate_random_string())
            serializer.save(user=user)
            print(55)
            serializer.save(agent=agent)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'msg': serializer.errors})

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})


class DialogViewSet(viewsets.ModelViewSet):
    '''对话视图集'''
    queryset = Dialog.objects.all()
    serializer_class = DialogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ['topic']

    def get_queryset(self):
        topicId = self.request.GET.get(
            'topicId') or self.request.data.get('topicId')
        return Dialog.objects.filter(user=self.request.user, topic=topicId)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        topicId = self.request.data.get('topicId')
        message = self.request.data.get('message')
        if not message:
            return Response({'msg': '会话内容不能为空'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not topicId:
            return Response({'msg': '会话ID不能为空'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        my_account = Account.objects.filter(user=user).first()

        if my_account.ai_count <= 0 and my_account.ai_extra_count <= 0:
            return Response({'msg': '可对话次数不足'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        topic = Topic.objects.filter(id=topicId, user=user).first()
        memory = Memory.objects.filter(user=user, agent=topic.agent.id)
        last_menory = memory.last()
        # 提示词
        prompt = topic.agent.prompt

        # 历史对话
        if last_menory:
            # 有记忆
            history = list(self.filter_queryset(self.get_queryset()).filter(
                user=user, topic=topic, createTime__gt=last_menory.createTime).values('role', 'content'))
        else:
            # 无记忆
            history = list(self.filter_queryset(self.get_queryset()).filter(
                user=user, topic=topic).values('role', 'content'))
        # 去除少于3个字和全是数字的用户对话
        history = [history[i:i+2] for i in range(0, len(history), 2)]
        history = [item for sublist in history if len(
            sublist[0]['content']) > 2 and not sublist[0]['content'].isdigit() for item in sublist]
        if (len(history)) > 30:
            # 总结摘要，形成记忆
            prompt += '\n-总结user角色的内容,生成尽量精减的摘要,附加在最后的[]中,字数控制在50字以内。\n'
        else:
            if last_menory:
                # 有记忆
                prompt += '\n## 历史摘要\n'
                for item in list(memory.values()):
                    prompt += '[{}]{}\n'.format(item['createTime'].strftime(
                        '%Y-%m-%d %H:%M:%S'), item['abstract'])
        if (len(history) > 50):
            history = history[-30:]

        prompt += '## 对话背景\n-当前时间:{}' .format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        history.insert(0, {'role': 'system', 'content': prompt})
        history.append({'role': 'user', 'content': message})
        llm_code = topic.agent.model
        llm = AIModels.objects.filter(model_code=llm_code).first()
        print(history)
        # 从缓存中调用大模式设置
        # llm = cache.get(llm_code)
        # return Response('', status=status.HTTP_200_OK)
        # if not llm:
        #     # 从数据库中获取大模型配置
        #     llm = AIModels.objects.filter(model_code=llm_code).first()
        #     # 存入缓存（3天）
        #     cache.set(llm_code, llm, 3*24*60*60)
        # 调用deepseek大模型
        llm_msg = call_deepseek(history, llm)
        print(llm_msg)
        if llm_msg:
            # print(llm_msg)
            # 提取总结
            abstract = re.findall(r'\[([^\]]*)\]', llm_msg)
            print(abstract)
            # 删除总结[]内容
            new_llm_msg = re.sub(r'\[[^\]]*\]', '', llm_msg)
            # print(abstract)
            # print(new_llm_msg)
            if len(abstract) != 0:
                # 创建记记忆
                memory_serializer = MemorySerializer(
                    data={'user': user.id, 'agent': topic.agent.id, 'abstract': abstract[0], })
                if memory_serializer.is_valid():
                    # 保存记忆
                    memory_serializer.save()

            # 保存用户对话
            serializer = self.get_serializer(
                data={'user': user.id, 'topic': topic.id, 'role': 'user', 'content': message})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # 保存AI回复
            serializer = self.get_serializer(
                data={'user': user.id, 'topic': topic.id, 'role': 'assistant', 'content': new_llm_msg})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # 更新话题
            topic.round += 1
            topic.save()
            # 更新账户
            if my_account.ai_count > 0:
                # 优先扣减每日额定
                my_account.ai_count -= 1
            elif my_account.ai_extra_count > 0:
                my_account.ai_extra_count -= 1
            my_account.save()
            return Response(new_llm_msg, status=status.HTTP_200_OK)
        else:
            return Response({'msg': '好像出了些问题，请稍后重试'}, status=status.HTTP_502_BAD_GATEWAY)


class DefyAgentViewSet(viewsets.ModelViewSet):
    '''AI训练智能体视图集'''
    queryset = DefyAgent.objects.all()
    serializer_class = DefyAgentSerializer
    permission_classes = [ReadOnly]
    filterset_fields = ['classify']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(shelf_status=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserDefyViewSet(viewsets.ModelViewSet):
    '''用户AI训练视图集'''
    queryset = UserDefy.objects.all()
    serializer_class = UserDefySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    # filterset_fields = ['agent']

    def get_queryset(self):
        return UserDefy.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        '''创建或返回练习'''
        user = request.user
        agentId = request.data.get('agentId')
        if not agentId:
            return Response({'msg': '请选择聊天对象'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        instance = self.filter_queryset(
            self.get_queryset()).filter(user=user, agent_role=agentId, defy_status=0).first()

        if instance:
            # 返回进行中的练习
            serializer = self.get_serializer(instance)
            return Response(serializer.data,  status.HTTP_200_OK)

        # 新练习
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            agent = DefyAgent.objects.filter(id=agentId).first()
            serializer.save(user=user)
            serializer.save(agent_role=agent)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response({'msg': serializer.errors})

    def retrieve(self, request, *args, **kwargs):
        # 查看详情
        user = request.user
        instance = self.get_object()
        my_account = Account.objects.filter(user=user).first()
        if my_account.vip_type != 0 and not instance.vip_check:
            # VIP会员查看
            instance.vip_check = True
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # 不能put更新
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    def destroy(self, request, *args, **kwargs):
        # 不能删除
        raise exceptions.AuthenticationFailed(
            {'status': status.HTTP_403_FORBIDDEN, 'msg': '非法操作'})

    @action(methods=['POST'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def finish(self, request, *args, **kwargs):
        user = request.user
        defyId = request.data.get('defyId')

        if not defyId:
            return Response({'msg': '练习ID不能为空'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        instance = self.filter_queryset(
            self.get_queryset()).filter(user=user, id=defyId).first()
        if instance:
            # 修改状态为评估中
            instance.defy_status = 1
            instance.save()
            # ============== 评估过程 ==============
            # 所有练习对话
            history = list(DefyDialog.objects.filter(
                user=user, defy=instance).values('role', 'content'))
            # 插入system提示词
            history.insert(
                0, {'role': 'system', 'content': instance.agent_role.assess.prompt})
            llm_code = instance.agent_role.agent_role.model
            llm = AIModels.objects.filter(model_code=llm_code).first()
            # 调用线程进行大模型评估
            threading.Thread(target=running_task, args=(
                instance, history, llm), daemon=True).start()
            # ============== 评估过程结束 ==============
        return Response({'msg': '练习结束'}, status=status.HTTP_200_OK)


class DefyDialogViewSet(viewsets.ModelViewSet):
    '''AI练习对话视图集'''
    queryset = DefyDialog.objects.all()
    serializer_class = DefyDialogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ['defy']

    def get_queryset(self):
        defyId = self.request.GET.get(
            'defyId') or self.request.data.get('defyId')
        return DefyDialog.objects.filter(user=self.request.user, defy=defyId)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        defyId = self.request.data.get('defyId')
        message = self.request.data.get('message')
        if not message:
            return Response({'msg': '会话内容不能为空'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not defyId:
            return Response({'msg': '练习ID不能为空'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        my_account = Account.objects.filter(user=user).first()

        if my_account.ai_count <= 0 and my_account.ai_extra_count <= 0:
            return Response({'msg': '可对话次数不足'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user_defy = UserDefy.objects.filter(
            id=defyId, user=user).first()
        if user_defy.defy_status != 0:
            return Response({'msg': '本次练习已结束'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 历史对话
        history = list(self.get_queryset().values('role', 'content'))
        # 插入“导演”system提示词
        history.insert(
            0, {'role': 'system', 'content': user_defy.agent_role.agent_role.prompt})
        history.append({'role': 'user', 'content': message})
        llm_code = user_defy.agent_role.agent_role.model
        llm = AIModels.objects.filter(model_code=llm_code).first()
        # llm = cache.get(llm_code)
        # if not llm:
        #     llm = AIModels.objects.filter(model_code=llm_code).first()
        #     cache.set(llm_code, llm, 3*24*60*60)
        # 调用deepseek大模型
        print(history)
        llm_msg = call_deepseek(history, llm)

        if llm_msg != '':
            # 提取情绪{}中的内容
            emotion = re.findall(r'\{([^\]]*)\}', llm_msg)
            print(emotion)
            # 删除情绪{}内容
            new_llm_msg = re.sub(r'\{[^\]]*\}', '', llm_msg)
            # 保存用户对话
            serializer = self.get_serializer(
                data={'user': user.id, 'defy': user_defy.id, 'role': 'user', 'content': message})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # 保存AI回复
            serializer = self.get_serializer(
                data={'user': user.id, 'defy': user_defy.id, 'role': 'assistant', 'emotion': emotion[0] if len(emotion) > 0 else '', 'content': new_llm_msg})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            defy_status = 0
            if user_defy.defy_status == 0:
                # 回合次数增加
                user_defy.round += 1
                user_defy.lastTime = datetime.now()
            if user_defy.round == user_defy.agent_role.max_round:
                # 回合数等于最大回合数，回合结束,评估中
                user_defy.defy_status = 1
                user_defy.count += 1
                defy_status = 1
                if my_account.vip_type != 0:
                    # VIP会员完成
                    user_defy.vip_check = True

                # ============== 评估过程 ==============
                history = list(self.get_queryset().values('role', 'content'))
                # 插入system提示词
                history.insert(
                    0, {'role': 'system', 'content': user_defy.agent_role.assess.prompt})
                llm_code = user_defy.agent_role.agent_role.model
                llm = AIModels.objects.filter(model_code=llm_code).first()
                # 调用线程进行大模型评估
                threading.Thread(target=running_task, args=(
                    user_defy, history, llm), daemon=True).start()
                # ============== 评估过程结束 ==============
            user_defy.save()

            # 更新账户
            if my_account.ai_count > 0:
                # 优先扣减每日额定
                my_account.ai_count -= 1
            elif my_account.ai_extra_count > 0:
                # 扣减扩展的次数
                my_account.ai_extra_count -= 1
            my_account.save()

            return Response({"defy_status": defy_status, "round": user_defy.round, "message": new_llm_msg}, status=status.HTTP_200_OK)
