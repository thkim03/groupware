from django.db import models
from approvals.models import ApprovalDoc


class ExpenseRequest(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('MANUAL', '직접입력'),
        ('TRIP', '출장'),
        ('PURCHASE', '구매'),
    ]

    doc = models.OneToOneField(ApprovalDoc, on_delete=models.CASCADE, related_name='expense_request')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='MANUAL')
    attachment = models.FileField(upload_to='expense_attachments/', null=True, blank=True, verbose_name='첨부파일')

    class Meta:
        verbose_name = '지출결의'
        verbose_name_plural = '지출결의 목록'

    def __str__(self):
        return str(self.doc)

    def total_amount(self):
        return sum(item.amount for item in self.items.all())


class ExpenseItem(models.Model):
    expense = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200, verbose_name='항목')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='금액')

    class Meta:
        verbose_name = '지출항목'
