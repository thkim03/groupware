from django.db import models
from django.conf import settings


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='attendance_records', verbose_name='직원')
    date = models.DateField(verbose_name='날짜')
    check_in = models.TimeField(null=True, blank=True, verbose_name='출근시간')
    check_out = models.TimeField(null=True, blank=True, verbose_name='퇴근시간')
    is_business_trip = models.BooleanField(default=False, verbose_name='출장여부')
    note = models.CharField(max_length=200, blank=True, verbose_name='비고')

    class Meta:
        unique_together = ('employee', 'date')
        verbose_name = '근태기록'
        verbose_name_plural = '근태기록 목록'
        ordering = ['-date']

    def __str__(self):
        return f'{self.employee} - {self.date}'
