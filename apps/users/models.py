from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    '''用户'''
    # 微信开放平台ID
    union_id = models.CharField(max_length=100, default='', null=True)
    open_id = models.CharField(max_length=100,  default='', null=True)
    real_name = models.CharField(max_length=15,  default='', null=True)
    nick_name = models.CharField(max_length=50, default='', null=True)
    avatar = models.URLField(default='', null=True)
    mobile = models.CharField(max_length=11, default='', null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'a_users'


class Account(models.Model):
    '''账户'''
    # AI聊天次数
    ai_count = models.IntegerField(default=0, blank=True)
    # AI额外聊天次数
    ai_extra_count = models.IntegerField(default=0, blank=True)
    # 对应用户
    user = models.OneToOneField(
        'users.Users', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    # 更新日期
    update_date = models.DateField(blank=True, null=True)
    # vip类型 1：月会员 2：季会员 3：年会员
    vip_type = models.IntegerField(default=0, blank=True)
    # 会员到期日
    vip_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'a_account'


class AccountRecord(models.Model):
    '''充值和消费记录'''
    # 金额
    amount = models.FloatField()
    # 动账类型  1:充值   2：消费
    amount_type = models.IntegerField()
    # 对应用户
    user = models.ForeignKey(
        'users.Users', on_delete=models.CASCADE)

    class Meta:
        db_table = 'a_account_record'


class Fans(models.Model):
    '''用户粉丝'''
    # 绑定时间
    binding_time = models.DateTimeField(auto_now_add=True)
    # 对应用户
    user = models.ForeignKey(
        'users.Users',  on_delete=models.CASCADE, blank=True, null=True)
    # 对应粉丝
    fans = models.OneToOneField(
        'users.Users', related_name='users_fans_set', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'a_fans'
