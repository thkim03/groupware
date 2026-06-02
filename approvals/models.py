from django.db import models
from django.conf import settings


class ApprovalDoc(models.Model):
    DOC_TYPE_CHOICES = [
        ('LEAVE', '휴가신청'),
        ('TRIP', '출장신청'),
        ('PURCHASE', '구매요청'),
        ('EXPENSE', '지출결의'),
        ('ETC', '기타'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', '임시저장'),
        ('SUBMITTED', '상신'),
        ('PENDING', '결재중'),
        ('APPROVED', '승인'),
        ('REJECTED', '반려'),
        ('CANCELED', '취소'),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, verbose_name='문서종류')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name='상태')
    title = models.CharField(max_length=200, verbose_name='제목')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='authored_docs', verbose_name='기안자')
    approvers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ApprovalLine',
                                       related_name='approval_docs', verbose_name='결재자')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '결재문서'
        verbose_name_plural = '결재문서 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_doc_type_display()}] {self.title}'

    def submit(self):
        self.status = 'SUBMITTED'
        self.save()
        # Move to PENDING for first approver
        first_line = self.approval_lines.order_by('order').first()
        if first_line:
            first_line.status = 'PENDING'
            first_line.save()
            self.status = 'PENDING'
            self.save()

    def process_approval(self, approver, action, comment=''):
        """action: APPROVED or REJECTED"""
        line = self.approval_lines.filter(approver=approver, status='PENDING').first()
        if not line:
            return False
        from django.utils import timezone
        line.status = action
        line.comment = comment
        line.acted_at = timezone.now()
        line.save()
        ApprovalLog.objects.create(doc=self, actor=approver, action=action, comment=comment)
        if action == 'REJECTED':
            self.status = 'REJECTED'
            self.save()
        elif action == 'APPROVED':
            next_line = self.approval_lines.filter(order__gt=line.order, status='PENDING').order_by('order').first()
            if not next_line:
                # check if there are remaining lines not yet PENDING
                remaining = self.approval_lines.filter(order__gt=line.order).order_by('order').first()
                if remaining:
                    remaining.status = 'PENDING'
                    remaining.save()
                else:
                    self.status = 'APPROVED'
                    self.save()
                    self._on_approved()
        return True

    def _on_approved(self):
        if self.doc_type == 'LEAVE':
            try:
                lr = self.leave_request
                lr.deduct_leave()
            except Exception:
                pass
        elif self.doc_type == 'PURCHASE':
            try:
                from purchase.models import PurchaseRequest
                pr = self.purchase_request
                pr.create_expense_doc()
            except Exception:
                pass


class ApprovalLine(models.Model):
    STATUS_CHOICES = [
        ('WAITING', '대기'),
        ('PENDING', '결재대기'),
        ('APPROVED', '승인'),
        ('REJECTED', '반려'),
    ]

    doc = models.ForeignKey(ApprovalDoc, on_delete=models.CASCADE, related_name='approval_lines')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='approval_lines')
    order = models.IntegerField(verbose_name='순서')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING')
    comment = models.TextField(blank=True, verbose_name='의견')
    acted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.doc} - {self.approver} ({self.order})'


class ApprovalLog(models.Model):
    doc = models.ForeignKey(ApprovalDoc, on_delete=models.CASCADE, related_name='logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Attachment(models.Model):
    doc = models.ForeignKey(ApprovalDoc, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
