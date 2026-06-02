from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from approvals.models import ApprovalDoc, ApprovalLine
from accounts.models import Employee
from .models import TripRequest


@login_required
def trip_create(request):
    employees = Employee.objects.all().order_by('department', 'rank', 'username')
    if request.method == 'POST':
        destination = request.POST.get('destination')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        purpose = request.POST.get('purpose')
        title = request.POST.get('title', f'출장신청 - {destination}')
        approver_ids = request.POST.getlist('approvers')
        if not all([destination, start_date, end_date, purpose, approver_ids]):
            messages.error(request, '모든 필드를 입력해주세요.')
        else:
            doc = ApprovalDoc.objects.create(
                doc_type='TRIP',
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
            TripRequest.objects.create(
                doc=doc,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                purpose=purpose,
            )
            doc.submit()
            messages.success(request, '출장신청서가 상신되었습니다.')
            return redirect('trip:trip_detail', pk=doc.pk)
    return render(request, 'trip/trip_form.html', {'employees': employees})


@login_required
def trip_detail(request, pk):
    doc = get_object_or_404(ApprovalDoc, pk=pk, doc_type='TRIP')
    trip = get_object_or_404(TripRequest, doc=doc)
    lines = doc.approval_lines.order_by('order')
    return render(request, 'trip/trip_detail.html', {'doc': doc, 'trip': trip, 'lines': lines})


@login_required
def trip_list(request):
    docs = ApprovalDoc.objects.filter(doc_type='TRIP').select_related('author').order_by('-created_at')
    return render(request, 'trip/trip_list.html', {'docs': docs})
