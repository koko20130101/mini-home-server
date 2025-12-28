from rest_framework import serializers
from .models import Agent, Topic, Dialog, AIModels, VoiceRole, DefyAgent, Assess, DefyDialog, UserDefy, Memory


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

    def to_representation(self, instance):
        fields = ['id', 'agent_name', 'avatar',
                  'max_round', 'salutation', 'salutation_audio','salutation_new', 'salutation_new_audio', 'brief', 'description', 'avatar_bg', 'avatar_wait', 'avatar_speaking', 'model', 'asr', 'tts','voice_role', 'voice_rate', 'pitch_rate']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in fields:
                resData[field_name] = data[field_name]
        return resData


class TopicSerializer(serializers.ModelSerializer):
    agent_avatar = serializers.ReadOnlyField(source='agent.avatar')
    agent_name = serializers.ReadOnlyField(source='agent.agent_name')

    class Meta:
        model = Topic
        fields = '__all__'

    def to_representation(self, instance):
        fields = ['id', 'talkId', 'agent_avatar', 'agent_name',
                  'round', 'abstract', 'last_ask', 'last', 'createTime']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in fields:
                resData[field_name] = data[field_name]
        return resData


class DialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialog
        fields = '__all__'


class DefyAgentSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField(source='agent_role.avatar')
    agent_name = serializers.ReadOnlyField(source='agent_role.agent_name')
    age = serializers.ReadOnlyField(source='agent_role.age')
    sex = serializers.ReadOnlyField(source='agent_role.sex')
    brief = serializers.ReadOnlyField(source='agent_role.brief')
    asr = serializers.ReadOnlyField(source='agent_role.asr')
    voice_role = serializers.ReadOnlyField(source='agent_role.voice_role')
    voice_rate = serializers.ReadOnlyField(source='agent_role.voice_rate')
    pitch_rate = serializers.ReadOnlyField(source='agent_role.pitch_rate')
    emotion = serializers.ReadOnlyField(source='agent_role.emotion')
    agent_description = serializers.ReadOnlyField(
        source='agent_role.description')

    class Meta:
        model = DefyAgent
        fields = '__all__'


class UserDefySerializer(serializers.ModelSerializer):
    agent_avatar = serializers.ReadOnlyField(
        source='agent_role.agent_role.avatar')
    agent_name = serializers.ReadOnlyField(
        source='agent_role.agent_role.agent_name')
    agent_id = serializers.ReadOnlyField(
        source='agent_role.id')
    agent_age = serializers.ReadOnlyField(
        source='agent_role.agent_role.age')
    agent_brief = serializers.ReadOnlyField(
        source='agent_role.agent_role.brief')
    agent_description = serializers.ReadOnlyField(
        source='agent_role.agent_role.description')
    max_round = serializers.ReadOnlyField(
        source='agent_role.max_round')
    classify = serializers.ReadOnlyField(
        source='agent_role.classify.classify_name')

    class Meta:
        model = UserDefy
        fields = '__all__'

    def to_representation(self, instance):
        path = self.context['request'].path
        listfields = ['id', 'defy_status',
                      'round', 'agent_avatar', 'agent_name', 'max_round', 'agent_id', 'classify', 'lastTime']
        detailsfields = ['id', 'defy_status',
                         'round', 'result', 'result_status', 'agent_age', 'agent_brief', 'agent_description']
        data = super().to_representation(instance)

        resData = {}
        if path == '/user-defy':
            # 列表字段
            for field_name in data:
                if field_name in listfields:
                    resData[field_name] = data[field_name]
        else:
            # 详情字段
            for field_name in data:
                if field_name in detailsfields:
                    resData[field_name] = data[field_name]
        return resData


class DefyDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefyDialog
        fields = '__all__'


class MemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Memory
        fields = '__all__'


''' ====== 后台用的序列化 ====== '''


class AgentAdminSerializer(serializers.ModelSerializer):
    classifyName = serializers.ReadOnlyField(source='classify.classify_name')

    class Meta:
        model = Agent
        fields = '__all__'


class AIModelsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModels
        fields = '__all__'


class VoiceRoleAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceRole
        fields = '__all__'


class DefyAgentAdminSerializer(serializers.ModelSerializer):
    agent_name = serializers.ReadOnlyField(source='agent_role.agent_name')
    avatar = serializers.ReadOnlyField(source='agent_role.avatar')

    class Meta:
        model = DefyAgent
        fields = '__all__'


class AssessAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assess
        fields = '__all__'


class UserDefyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDefy
        fields = '__all__'
