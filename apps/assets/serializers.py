from rest_framework import serializers
from .models import UploadImages, SystemConfig, GlobalClassify


class UploadImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadImages
        fields = '__all__'


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'


class GlobalClassifySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = GlobalClassify
        fields = '__all__'

    def to_representation(self, instance):
        fields = ['id', 'classify_name', 'classify_image', 'children']
        data = super().to_representation(instance)
        resData = {}
        for field_name in data:
            if field_name in fields:
                resData[field_name] = data[field_name]
        return resData

    def get_children(self, obj):
        # 获取当前对象的所有子对象并序列化它们
        children = obj.children.all()
        serializer = self.__class__(children, many=True)
        if len(serializer.data):
            return serializer.data


''' ====== 后台用的序列化 ====== '''


class AdminGlobalClassifySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = GlobalClassify
        fields = '__all__'

    def get_children(self, obj):
        # 获取当前对象的所有子对象并序列化它们
        children = obj.children.all()
        serializer = self.__class__(children, many=True)
        if len(serializer.data):
            return serializer.data
