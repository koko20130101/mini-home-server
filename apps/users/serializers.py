from rest_framework import serializers
from .models import Users, Account, Fans


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'avatar',
                     'is_superuser', 'mobile', 'created']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['happy_coin', 'ai_count','ai_extra_count', 'vip_type', 'vip_date']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class FansSerializer(serializers.ModelSerializer):
    nick_name = serializers.ReadOnlyField(source='fans.nick_name')

    class Meta:
        model = Fans
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['nick_name', 'binding_time']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


''' ====== 后台用的序列化 ====== '''


class AdminUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

    def to_representation(self, instance):
        usefields = ['id', 'nick_name', 'avatar',
                     'is_superuser', 'mobile', 'created', 'real_name', 'is_active']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in usefields:
                resData[field_name] = data[field_name]
        return resData


class AdminAccountSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField(source='user.avatar')
    nick_name = serializers.ReadOnlyField(source='user.nick_name')

    class Meta:
        model = Account
        fields = '__all__'
