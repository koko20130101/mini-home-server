from django.db import models

# Create your models here.


class Orders(models.Model):
    id = models.CharField(
        verbose_name="ID", max_length=48, primary_key=True)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    amount = models.DecimalField(
        verbose_name='订单金额', max_digits=10, decimal_places=2, default=0)
    buy_num = models.IntegerField(verbose_name='订单数量', default=0)
    product_name = models.CharField(
        verbose_name="商品名称", max_length=50, default='')
    product_price = models.DecimalField(
        verbose_name='商品单价', max_digits=10, decimal_places=2, default=0)
    activity_id = models.IntegerField(
        verbose_name='关联活动ID',  blank=True, null=True)
    # 0 待支付 1已支付 2 待发货 3已发货 4已完成 5已取消
    status = models.IntegerField(
        verbose_name='订单状态', default=0)
    remarks = models.CharField(verbose_name='备注', max_length=200, blank=True)
    user = models.ForeignKey(
        'users.Users', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'pd_orders'
