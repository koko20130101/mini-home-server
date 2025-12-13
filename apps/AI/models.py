from django.db import models
from common.utils import get_upload_to


class Agent(models.Model):
    '''智能体'''
    agent_name = models.CharField(verbose_name="智能体名称", max_length=100)
    sex = models.IntegerField(verbose_name="性别", blank=True, null=True)
    age = models.IntegerField(verbose_name="年龄", blank=True, null=True)
    classify = models.ForeignKey(
        'assets.GlobalClassify', verbose_name="所属分类", on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(verbose_name="描述")
    brief = models.CharField(verbose_name="一句话简介", max_length=100)
    prompt = models.TextField(verbose_name="提示词")
    avatar = models.CharField(
        verbose_name="头像", max_length=300)
    avatar_bg = models.CharField(
        verbose_name="背景图片", max_length=300, blank=True)
    avatar_wait = models.CharField(
        verbose_name="等待动画", max_length=300, blank=True)
    avatar_speaking = models.CharField(
        verbose_name="说话动画", max_length=300, blank=True)
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    salutation = models.TextField(verbose_name="开场白", blank=True)
    salutation_audio = models.CharField(
        verbose_name="开场白声音", max_length=300, blank=True)
    salutation_new = models.TextField(
        verbose_name="新对话开场白", default="", blank=True)
    salutation_new_audio = models.CharField(
        verbose_name="新对话开场白声音", max_length=300, blank=True)
    max_round = models.IntegerField(
        verbose_name="最大回合数", default=0, blank=True)
    model = models.CharField(
        verbose_name="AI模型", max_length=50, null=True)
    tts = models.CharField(
        verbose_name="语音合成", max_length=50, null=True)
    asr = models.CharField(
        verbose_name="语音识别", max_length=50, null=True)
    voice_role = models.CharField(
        verbose_name="音色", max_length=50, null=True)
    emotion = models.CharField(
        verbose_name="音色情感", max_length=20, default="", null=True, blank=True)
    voice_rate = models.IntegerField(verbose_name="语速", default=0)
    pitch_rate = models.IntegerField(verbose_name="语调", default=0)
    temperature = models.CharField(
        verbose_name="温度", max_length=10, blank=True)

    class Meta:
        db_table = 'ai_agent'
        ordering = ('id',)


class Topic(models.Model):
    '''话题'''
    talkId = models.CharField(verbose_name="会话ID", max_length=32, blank=True)
    round = models.IntegerField(verbose_name='回合', default=0, blank=True)
    user = models.ForeignKey(
        'users.Users', verbose_name="所属用户", on_delete=models.CASCADE, null=True)
    agent = models.ForeignKey(
        'AI.Agent', verbose_name="所属智能体", on_delete=models.DO_NOTHING, null=True)
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        db_table = 'ai_topic'
        ordering = ('id',)


class Memory(models.Model):
    '''记忆'''
    user = models.ForeignKey(
        'users.Users', verbose_name="所属用户", on_delete=models.CASCADE, null=True)
    agent = models.ForeignKey(
        'AI.Agent', verbose_name="所属智能体", on_delete=models.DO_NOTHING, null=True)
    memory_type = models.IntegerField(
        verbose_name="记忆类型", default=1, blank=True)
    abstract = models.TextField(verbose_name="记忆摘要", blank=True)
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        db_table = 'ai_memory'
        ordering = ('id',)


class Dialog(models.Model):
    '''对话记录'''
    topic = models.ForeignKey(
        'AI.Topic', verbose_name="所属话题", on_delete=models.CASCADE)
    user = models.ForeignKey(
        'users.Users', verbose_name="所属用户", on_delete=models.CASCADE, null=True)
    role = models.CharField(verbose_name="角色", max_length=10)
    content = models.TextField(verbose_name="内容")
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        db_table = 'ai_dialog'
        ordering = ('id',)


class AIModels(models.Model):
    '''AI模型'''
    model_name = models.CharField(verbose_name="模型名称", max_length=100)
    model_code = models.CharField(verbose_name="模型编码", max_length=50)
    model_type = models.CharField(verbose_name="模型类型", max_length=30)
    base_url = models.TextField(verbose_name="调用URL", blank=True)
    api_key = models.TextField(verbose_name="API密钥", blank=True)
    app_key = models.TextField(verbose_name="应用ID", blank=True)
    accesskey_id = models.TextField(verbose_name="密钥ID", blank=True)
    sort = models.IntegerField(verbose_name="排序", default=0)
    is_enabled = models.BooleanField(verbose_name="是否启用", default=False)
    call_count = models.IntegerField(
        verbose_name="最大并发", default=2, blank=True)
    remark = models.TextField(verbose_name="备注", blank=True)

    class Meta:
        db_table = 'ai_models'
        ordering = ('sort',)


class VoiceRole(models.Model):
    '''音色'''
    voice_name = models.CharField(verbose_name="音色名称", max_length=100)
    voice_code = models.CharField(verbose_name="音色编码", max_length=50)
    is_emotion = models.BooleanField(verbose_name="是否多情感", default=False)
    voice_type = models.IntegerField(
        verbose_name="音色类型",  default=0)
    audio_url = models.TextField(verbose_name="试听链接", blank=True)
    ai_model = models.ForeignKey(
        'AI.AIModels', on_delete=models.DO_NOTHING,  blank=True)

    class Meta:
        db_table = 'ai_voice_role'
        ordering = ('id',)


class DefyAgent(models.Model):
    '''AI练习智能体'''
    agent_role = models.ForeignKey(
        'AI.Agent', verbose_name="所属智能体", on_delete=models.DO_NOTHING)
    assess = models.ForeignKey(
        'AI.Assess', verbose_name="结果评估维度", on_delete=models.DO_NOTHING)
    classify = models.ForeignKey(
        'assets.GlobalClassify', verbose_name="所属分类", on_delete=models.CASCADE, blank=True, null=True)
    max_round = models.IntegerField(verbose_name='最大回合', default=0)
    description = models.TextField(verbose_name="练习目标")
    count = models.IntegerField(verbose_name='练习人数', default=10)
    shelf_status = models.BooleanField(verbose_name='上架状态', default=True)
    index = models.IntegerField(verbose_name='排序', default=0)

    class Meta:
        db_table = 'ai_defy_agent'
        ordering = ('id',)


class Assess(models.Model):
    '''评估维度'''
    assess_name = models.CharField(verbose_name='维度名称', max_length=50)
    prompt = models.TextField(verbose_name='提示词')
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        db_table = 'ai_defy_assess'
        ordering = ('id',)


class UserDefy(models.Model):
    '''用户练习记录'''
    user = models.ForeignKey(
        'users.Users', verbose_name="所属用户", on_delete=models.CASCADE, blank=True, null=True)
    agent_role = models.ForeignKey(
        'AI.DefyAgent', on_delete=models.DO_NOTHING, verbose_name="挑战角色", blank=True, null=True)
    round = models.IntegerField(verbose_name="已挑战回合", default=0, blank=True)
    defy_status = models.IntegerField(
        verbose_name='状态', default=0, blank=True)
    result_status = models.CharField(
        verbose_name='结果状态', max_length=30, blank=True, null=True)
    result = models.TextField(verbose_name='评估结果', blank=True, null=True)
    vip_check = models.BooleanField(verbose_name='做为VIP查看过', default=False)
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    lastTime = models.DateTimeField(
        verbose_name='最后时间', blank=True, null=True)

    class Meta:
        db_table = 'ai_user_defy'
        ordering = ('id',)


class DefyDialog(models.Model):
    '''练习对话记录'''
    user = models.ForeignKey(
        'users.Users', verbose_name="所属用户", on_delete=models.CASCADE, null=True)
    defy = models.ForeignKey(
        'AI.UserDefy', on_delete=models.CASCADE, verbose_name='所属挑战用户')
    role = models.CharField(verbose_name="角色", max_length=10)
    emotion = models.CharField(
        verbose_name="情绪", max_length=10, default="", blank=True)
    content = models.TextField(verbose_name="内容")
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        db_table = 'ai_defy_dialog'
        ordering = ('id',)
