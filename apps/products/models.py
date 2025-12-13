from django.db import models

# Create your models here.


class Products(models.Model):
    '''商品'''
    id = models.CharField(
        verbose_name="ID", max_length=32, primary_key=True)
    product_name = models.CharField(verbose_name="商品名称", max_length=50)
    product_type = models.IntegerField(verbose_name="商品类型")
    thumbnail = models.TextField(verbose_name='商品小图', blank=True)
    banners = models.TextField(verbose_name='banner图', blank=True)
    price = models.DecimalField(
        verbose_name='商品价格', max_digits=10, decimal_places=2)
    origin_price = models.DecimalField(
        verbose_name='商品原价', max_digits=10, decimal_places=2, blank=True, null=True)
    color = models.CharField(
        verbose_name='商品颜色', max_length=100, blank=True)
    inventory = models.IntegerField(verbose_name='库存', default=0, blank=True)
    norm = models.IntegerField(verbose_name='规格', default=1, blank=True)
    brief = models.CharField(verbose_name='商品简介', max_length=200, blank=True)
    describe = models.TextField(verbose_name='商品描述', blank=True)

    class Meta:
        db_table = 'pd_products'
