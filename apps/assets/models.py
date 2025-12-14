from django.db import models
from common.utils import get_upload_to


class UploadImages(models.Model):
    '''上传的图片'''
    height = models.PositiveIntegerField(default=155)
    width = models.PositiveIntegerField(default=155)
    # 图片所属用户
    user = models.ForeignKey(
        'users.Users', on_delete=models.CASCADE, blank=True, null=True)
    image_name = models.CharField(max_length=100, blank=True, null=True)
    image_type = models.IntegerField(default=0)
    image_url = models.ImageField(
        upload_to=get_upload_to, height_field='height', width_field='width', blank=True, null=True)

    class Meta:
        db_table = 'ot_upload_imges'


class SystemConfig(models.Model):
    '''系统配置'''
    config_name = models.CharField(verbose_name='配置名', max_length=50, )
    config_val = models.CharField(
        verbose_name='配置值', max_length=50, blank=True)

    class Meta:
        db_table = 'ot_system_config'


class GlobalClassify(models.Model):
    '''分类管理'''
    classify_name = models.CharField(verbose_name='分类名称', max_length=50)
    code = models.CharField(verbose_name='分类标识', max_length=50, blank=True)
    index = models.IntegerField(verbose_name='排序', default=0)
    classify_image = models.CharField(
        verbose_name='分类图片', max_length=200, default='', blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', blank=True, null=True)

    class Meta:
        db_table = 'ot_classify'
        ordering = ('id', 'index')
