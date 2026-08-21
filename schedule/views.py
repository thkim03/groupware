import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Schedule
from approvals.models import ApprovalDoc
from trip.models import TripRequest
from leave.models import LeaveRequest


@login_required
def calendar_view(request):
    return render(request, 'schedule/calendar.html', {
        'colors': Schedule.COLOR_CHOICES,
        'categories': Schedule.CATEGORY_CHOICES,
    })


@login_required
def events_json(request):
    """FullCalendar용 JSON 이벤트 API"""
    start_str = request.GET.get('start', '')
    end_str = request.GET.get('end', '')
    try:
        start = datetime.date.fromisoformat(start_str[:10])
        end = datetime.date.fromisoformat(end_str[:10])
    except (ValueError, IndexError):
        today = datetime.date.today()
        start = today.replace(day=1)
        end = today.replace(day=28)

    events = []

    # 1. 개인 + 공유 일정
    schedules = Schedule.objects.filter(
        Q(author=request.user) | Q(category='SHARED'),
        start_date__lte=end,
        end_date__gte=start,
    ).select_related('author')

    for s in schedules:
        end_date = s.end_date + datetime.timedelta(days=1)  # FullCalendar exclusive end
        ev = {
            'id': f'sched_{s.pk}',
            'title': s.title if s.category == 'PERSONAL' else f'[공유] {s.title}',
            'start': s.start_date.isoformat(),
            'end': end_date.isoformat(),
            'backgroundColor': s.color,
            'borderColor': s.color,
            'extendedProps': {
                'type': 'schedule',
                'pk': s.pk,
                'author': s.author.get_full_name() or s.author.username,
                'memo': s.memo,
                'category': s.get_category_display(),
            },
        }
        if not s.all_day and s.start_time:
            ev['start'] = f'{s.start_date.isoformat()}T{s.start_time.strftime("%H:%M:%S")}'
            if s.end_time:
                ev['end'] = f'{s.end_date.isoformat()}T{s.end_time.strftime("%H:%M:%S")}'
        events.append(ev)

    # 2. 승인된 출장
    trips = TripRequest.objects.filter(
        doc__status='APPROVED',
        start_date__lte=end,
        end_date__gte=start,
    ).select_related('doc__author')

    for t in trips:
        end_date = t.end_date + datetime.timedelta(days=1)
        events.append({
            'id': f'trip_{t.pk}',
            'title': f'[출장] {t.doc.author.get_full_name() or t.doc.author.username}: {t.destination}',
            'start': t.start_date.isoformat(),
            'end': end_date.isoformat(),
            'backgroundColor': '#fd7e14',
            'borderColor': '#fd7e14',
            'extendedProps': {'type': 'trip', 'author': t.doc.author.get_full_name() or t.doc.author.username},
        })

    # 3. 승인된 휴가
    leaves = LeaveRequest.objects.filter(
        doc__status='APPROVED',
        start_date__lte=end,
        end_date__gte=start,
    ).select_related('doc__author')

    for lv in leaves:
        end_date = lv.end_date + datetime.timedelta(days=1)
        events.append({
            'id': f'leave_{lv.pk}',
            'title': f'[휴가] {lv.doc.author.get_full_name() or lv.doc.author.username}: {lv.get_leave_type_display()}',
            'start': lv.start_date.isoformat(),
            'end': end_date.isoformat(),
            'backgroundColor': '#20c997',
            'borderColor': '#20c997',
            'extendedProps': {'type': 'leave', 'author': lv.doc.author.get_full_name() or lv.doc.author.username},
        })

    return JsonResponse(events, safe=False)


@login_required
def schedule_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or start_date
        all_day = request.POST.get('all_day') == '1'
        start_time = request.POST.get('start_time') or None
        end_time = request.POST.get('end_time') or None
        category = request.POST.get('category', 'PERSONAL')
        color = request.POST.get('color', '#0d6efd')
        memo = request.POST.get('memo', '')
        if not title or not start_date:
            messages.error(request, '제목과 시작일은 필수입니다.')
        else:
            Schedule.objects.create(
                title=title,
                start_date=start_date,
                end_date=end_date,
                all_day=all_day,
                start_time=start_time if not all_day else None,
                end_time=end_time if not all_day else None,
                category=category,
                color=color,
                memo=memo,
                author=request.user,
            )
            messages.success(request, '일정이 등록되었습니다.')
            return redirect('schedule:calendar')
    return render(request, 'schedule/schedule_form.html', {
        'colors': Schedule.COLOR_CHOICES,
        'categories': Schedule.CATEGORY_CHOICES,
        'action': 'create',
    })


@login_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if schedule.author != request.user and not request.user.is_admin:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('schedule:calendar')
    if request.method == 'POST':
        schedule.title = request.POST.get('title', schedule.title).strip()
        schedule.start_date = request.POST.get('start_date', schedule.start_date)
        schedule.end_date = request.POST.get('end_date') or schedule.start_date
        schedule.all_day = request.POST.get('all_day') == '1'
        schedule.start_time = request.POST.get('start_time') or None if not schedule.all_day else None
        schedule.end_time = request.POST.get('end_time') or None if not schedule.all_day else None
        schedule.category = request.POST.get('category', schedule.category)
        schedule.color = request.POST.get('color', schedule.color)
        schedule.memo = request.POST.get('memo', '')
        schedule.save()
        messages.success(request, '일정이 수정되었습니다.')
        return redirect('schedule:calendar')
    return render(request, 'schedule/schedule_form.html', {
        'colors': Schedule.COLOR_CHOICES,
        'categories': Schedule.CATEGORY_CHOICES,
        'schedule': schedule,
        'action': 'edit',
    })


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if schedule.author != request.user and not request.user.is_admin:
        messages.error(request, '삭제 권한이 없습니다.')
    elif request.method == 'POST':
        schedule.delete()
        messages.success(request, '일정이 삭제되었습니다.')
    return redirect('schedule:calendar')
