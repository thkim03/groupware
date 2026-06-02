from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ApprovalDoc, ApprovalLine


@login_required
def inbox(request):
    lines = ApprovalLine.objects.filter(
        approver=request.user, status='PENDING'
    ).select_related('doc', 'doc__author').order_by('-doc__created_at')
    return render(request, 'approvals/inbox.html', {'lines': lines})


@login_required
def sent_box(request):
    docs = ApprovalDoc.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'approvals/sent.html', {'docs': docs})


@login_required
def approve_action(request, doc_pk):
    doc = get_object_or_404(ApprovalDoc, pk=doc_pk)
    line = ApprovalLine.objects.filter(doc=doc, approver=request.user, status='PENDING').first()
    if not line:
        messages.error(request, '결재할 수 있는 문서가 아닙니다.')
        return redirect('approvals:inbox')
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        if action in ('APPROVED', 'REJECTED'):
            doc.process_approval(request.user, action, comment)
            label = '승인' if action == 'APPROVED' else '반려'
            messages.success(request, f'문서를 {label}하였습니다.')
        return redirect('approvals:inbox')
    return render(request, 'approvals/approve_action.html', {'doc': doc, 'line': line})


@login_required
def cancel_doc(request, doc_pk):
    doc = get_object_or_404(ApprovalDoc, pk=doc_pk)
    if doc.author != request.user:
        messages.error(request, '본인이 기안한 문서만 취소할 수 있습니다.')
        return redirect('approvals:sent')
    if doc.status not in ('DRAFT', 'SUBMITTED', 'PENDING'):
        messages.error(request, '취소할 수 없는 상태입니다.')
        return redirect('approvals:sent')
    if request.method == 'POST':
        doc.status = 'CANCELED'
        doc.save()
        messages.success(request, '문서가 취소되었습니다.')
        return redirect('approvals:sent')
    return render(request, 'approvals/cancel_confirm.html', {'doc': doc})
