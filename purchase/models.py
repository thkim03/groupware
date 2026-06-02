from django.db import models
from approvals.models import ApprovalDoc


class PurchaseRequest(models.Model):
    doc = models.OneToOneField(ApprovalDoc, on_delete=models.CASCADE, related_name='purchase_request')
    expense_doc = models.ForeignKey(ApprovalDoc, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='purchase_expense_source', verbose_name='지출결의서')

    class Meta:
        verbose_name = '구매요청'
        verbose_name_plural = '구매요청 목록'

    def __str__(self):
        return str(self.doc)

    def create_expense_doc(self):
        from expense.models import ExpenseRequest, ExpenseItem
        expense_doc = ApprovalDoc.objects.create(
            doc_type='EXPENSE',
            status='DRAFT',
            title=f'[구매] {self.doc.title} 지출결의',
            author=self.doc.author,
        )
        er = ExpenseRequest.objects.create(
            doc=expense_doc,
            source_type='PURCHASE',
        )
        for item in self.items.all():
            ExpenseItem.objects.create(
                expense=er,
                description=item.name,
                amount=item.total,
            )
        self.expense_doc = expense_doc
        self.save(update_fields=['expense_doc'])
        return expense_doc


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200, verbose_name='품명')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='단가')
    quantity = models.IntegerField(verbose_name='수량')

    class Meta:
        verbose_name = '구매항목'

    @property
    def total(self):
        return self.unit_price * self.quantity
