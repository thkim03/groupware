from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from approvals.models import ApprovalDoc, ApprovalLine
from attendance.models import AttendanceRecord


@login_required
def index(request):
    today = timezone.localdate()
    # 결재 대기 문서 (내가 결재해야 할)
    pending_lines = ApprovalLine.objects.filter(
        approver=request.user, status='PENDING'
    ).select_related('doc', 'doc__author').order_by('-doc__created_at')[:5]
    # 내가 기안한 문서
    my_docs = ApprovalDoc.objects.filter(
        author=request.user
    ).order_by('-created_at')[:5]
    # 오늘 근태
    today_record = AttendanceRecord.objects.filter(
        employee=request.user, date=today
    ).first()
    return render(request, 'dashboard/index.html', {
        'pending_lines': pending_lines,
        'my_docs': my_docs,
        'today_record': today_record,
        'today': today,
    })
