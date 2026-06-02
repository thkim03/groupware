from django.db import models
from approvals.models import ApprovalDoc


class TripRequest(models.Model):
    doc = models.OneToOneField(ApprovalDoc, on_delete=models.CASCADE, related_name='trip_request')
    destination = models.CharField(max_length=200, verbose_name='목적지')
    start_date = models.DateField(verbose_name='출발일')
    end_date = models.DateField(verbose_name='귀환일')
    purpose = models.TextField(verbose_name='출장목적')
    expense_doc = models.ForeignKey(ApprovalDoc, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='trip_expense_source', verbose_name='지출결의서')

    class Meta:
        verbose_name = '출장신청'
        verbose_name_plural = '출장신청 목록'

    def __str__(self):
        return f'{self.doc.author} - {self.destination} ({self.start_date}~{self.end_date})'

    def create_expense_doc(self):
        from expense.models import ExpenseRequest
        expense_doc = ApprovalDoc.objects.create(
            doc_type='EXPENSE',
            status='DRAFT',
            title=f'[출장] {self.destination} 지출결의',
            author=self.doc.author,
        )
        ExpenseRequest.objects.create(
            doc=expense_doc,
            source_type='TRIP',
        )
        self.expense_doc = expense_doc
        self.save(update_fields=['expense_doc'])
        return expense_doc
