from django.db import models
from approvals.models import ApprovalDoc


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('ANNUAL', '연차'),
        ('PUBLIC', '공가'),
        ('SICK', '병가'),
        ('MORNING_HALF', '오전반차'),
        ('AFTERNOON_HALF', '오후반차'),
    ]

    doc = models.OneToOneField(ApprovalDoc, on_delete=models.CASCADE, related_name='leave_request')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, verbose_name='휴가종류')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    days_count = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='일수')

    class Meta:
        verbose_name = '휴가신청'
        verbose_name_plural = '휴가신청 목록'

    def __str__(self):
        return f'{self.doc.author} - {self.get_leave_type_display()} ({self.start_date}~{self.end_date})'

    def deduct_leave(self):
        if self.leave_type in ('ANNUAL', 'MORNING_HALF', 'AFTERNOON_HALF'):
            author = self.doc.author
            author.annual_leave_days -= self.days_count
            author.save(update_fields=['annual_leave_days'])
