import calendar
from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from approvals.models import ApprovalDoc, ApprovalLine
from attendance.models import AttendanceRecord
from trip.models import TripRequest


@login_required
def index(request):
    today = timezone.localdate()

    # 결재 대기 문서
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

    # 이번달 달력 데이터
    year, month = today.year, today.month
    _, last_day = calendar.monthrange(year, month)
    first_date = date(year, month, 1)
    last_date = date(year, month, last_day)

    # 승인된 출장 중 이번달에 걸치는 건
    approved_trips = TripRequest.objects.filter(
        doc__status='APPROVED',
        start_date__lte=last_date,
        end_date__gte=first_date,
    ).select_related('doc__author')

    # {date: [직원이름, ...]} 딕셔너리 생성
    trip_by_date = {}
    for trip in approved_trips:
        cur = max(trip.start_date, first_date)
        end = min(trip.end_date, last_date)
        while cur <= end:
            trip_by_date.setdefault(cur, []).append(trip.doc.author.get_full_name() or trip.doc.author.username)
            cur += timedelta(days=1)

    # 달력 주(week) 구조 생성
    cal = calendar.monthcalendar(year, month)
    cal_weeks = []
    for week in cal:
        week_days = []
        for d in week:
            if d == 0:
                week_days.append({'day': None, 'trips': [], 'is_today': False})
            else:
                day_date = date(year, month, d)
                week_days.append({
                    'day': d,
                    'date': day_date,
                    'trips': trip_by_date.get(day_date, []),
                    'is_today': day_date == today,
                })
        cal_weeks.append(week_days)

    return render(request, 'dashboard/index.html', {
        'pending_lines': pending_lines,
        'my_docs': my_docs,
        'today_record': today_record,
        'today': today,
        'cal_weeks': cal_weeks,
        'cal_year': year,
        'cal_month': month,
    })
