from django.db import models


class Activity(models.Model):
    '''活动'''
    act_name = models.CharField(verbose_name='活动名称', max_length=50)
    start_time = models.DateTimeField(
        verbose_name='开始时间', blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    remarks = models.CharField(verbose_name='备注', max_length=200, blank=True)

    class Meta:
        db_table = 'ot_activity'
        ordering = ('id',)
