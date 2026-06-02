from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from approvals.models import ApprovalDoc, ApprovalLine
from accounts.models import Employee
from .models import LeaveRequest


@login_required
def leave_create(request):
    employees = Employee.objects.all().order_by('department', 'rank', 'username')
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        days_count = request.POST.get('days_count')
        title = request.POST.get('title', f'휴가신청')
        approver_ids = request.POST.getlist('approvers')
        if not all([leave_type, start_date, end_date, days_count, approver_ids]):
            messages.error(request, '모든 필드를 입력해주세요.')
        else:
            doc = ApprovalDoc.objects.create(
                doc_type='LEAVE',
                status='DRAFT',
                title=title,
                author=request.user,
            )
            for i, aid in enumerate(approver_ids):
                ApprovalLine.objects.create(
                    doc=doc,
                    approver_id=int(aid),
                    order=i + 1,
                    status='WAITING',
                )
            LeaveRequest.objects.create(
                doc=doc,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days_count=days_count,
            )
            doc.submit()
            messages.success(request, '휴가신청서가 상신되었습니다.')
            return redirect('leave:leave_detail', pk=doc.pk)
    return render(request, 'leave/leave_form.html', {
        'employees': employees,
        'leave_types': LeaveRequest.LEAVE_TYPE_CHOICES,
    })


@login_required
def leave_detail(request, pk):
    doc = get_object_or_404(ApprovalDoc, pk=pk, doc_type='LEAVE')
    leave = get_object_or_404(LeaveRequest, doc=doc)
    lines = doc.approval_lines.order_by('order')
    return render(request, 'leave/leave_detail.html', {'doc': doc, 'leave': leave, 'lines': lines})


@login_required
def leave_list(request):
    docs = ApprovalDoc.objects.filter(doc_type='LEAVE').select_related('author').order_by('-created_at')
    return render(request, 'leave/leave_list.html', {'docs': docs})
