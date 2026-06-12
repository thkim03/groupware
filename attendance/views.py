import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import AttendanceRecord
from accounts.models import Employee


@login_required
def check_in(request):
    if request.method == 'POST':
        today = date.today()
        from django.utils import timezone
        now = timezone.localtime().time()
        record, created = AttendanceRecord.objects.get_or_create(
            employee=request.user, date=today,
            defaults={'check_in': now}
        )
        if not created and not record.check_in:
            record.check_in = now
            record.save()
            messages.success(request, f'출근 처리되었습니다. ({now.strftime("%H:%M")})')
        elif created:
            messages.success(request, f'출근 처리되었습니다. ({now.strftime("%H:%M")})')
        else:
            messages.info(request, '이미 출근 처리되었습니다.')
    return redirect('dashboard:index')


@login_required
def check_out(request):
    if request.method == 'POST':
        today = date.today()
        from django.utils import timezone
        now = timezone.localtime().time()
        is_trip = request.POST.get('is_business_trip') == '1'
        record = AttendanceRecord.objects.filter(employee=request.user, date=today).first()
        if record:
            record.check_out = now
            if is_trip:
                record.is_business_trip = True
            record.save()
            label = '출장(외근)후 퇴근' if is_trip else '퇴근'
            messages.success(request, f'{label} 처리되었습니다. ({now.strftime("%H:%M")})')
        else:
            messages.error(request, '출근 기록이 없습니다.')
    return redirect('dashboard:index')


@login_required
def my_attendance(request, year=None, month=None):
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    _, last_day = calendar.monthrange(year, month)
    days = [date(year, month, d) for d in range(1, last_day + 1)]
    records = {r.date: r for r in AttendanceRecord.objects.filter(
        employee=request.user, date__year=year, date__month=month
    )}
    prev_month = date(year, month, 1).replace(day=1)
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return render(request, 'attendance/my_attendance.html', {
        'year': year, 'month': month, 'days': days,
        'records': records, 'today': today,
        'prev_month': prev_month, 'next_month': next_month,
    })


@login_required
def edit_attendance(request, pk):
    record = get_object_or_404(AttendanceRecord, pk=pk)
    if record.employee != request.user and not request.user.is_admin:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('attendance:my_attendance')
    if request.method == 'POST':
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        note = request.POST.get('note', '')
        from datetime import time as dtime
        if check_in_str:
            h, m = check_in_str.split(':')
            record.check_in = dtime(int(h), int(m))
        else:
            record.check_in = None
        if check_out_str:
            h, m = check_out_str.split(':')
            record.check_out = dtime(int(h), int(m))
        else:
            record.check_out = None
        record.note = note
        record.is_business_trip = 'is_business_trip' in request.POST
        record.save()
        messages.success(request, '근태 기록이 수정되었습니다.')
        if request.user.is_admin:
            return redirect('attendance:admin_attendance')
        return redirect('attendance:my_attendance')
    return render(request, 'attendance/edit_attendance.html', {'record': record})


@login_required
def admin_attendance(request, year=None, month=None):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    _, last_day = calendar.monthrange(year, month)
    days = [date(year, month, d) for d in range(1, last_day + 1)]
    employees = Employee.objects.all().order_by('department', 'rank', 'username')
    records_qs = AttendanceRecord.objects.filter(date__year=year, date__month=month)
    records = {}
    for r in records_qs:
        records[(r.employee_id, r.date)] = r
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return render(request, 'attendance/admin_attendance.html', {
        'year': year, 'month': month, 'days': days,
        'employees': employees, 'records': records,
        'prev_month': prev_month, 'next_month': next_month,
    })


@login_required
def admin_edit_attendance(request, pk):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    return edit_attendance(request, pk)


@login_required
def admin_attendance_excel(request, year, month):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    try:
        import openpyxl
    except ImportError:
        return HttpResponse('openpyxl이 설치되어 있지 않습니다.', status=500)
    _, last_day = calendar.monthrange(int(year), int(month))
    days = [date(int(year), int(month), d) for d in range(1, last_day + 1)]
    employees = Employee.objects.all().order_by('department', 'username')
    records_qs = AttendanceRecord.objects.filter(date__year=year, date__month=month)
    records = {}
    for r in records_qs:
        records[(r.employee_id, r.date)] = r
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f'{year}년 {month}월 근태'
    headers = ['직원', '부서'] + [str(d.day) for d in days]
    ws.append(headers)
    for emp in employees:
        row = [str(emp), emp.department]
        for d in days:
            rec = records.get((emp.pk, d))
            if rec:
                ci = rec.check_in.strftime('%H:%M') if rec.check_in else ''
                co = rec.check_out.strftime('%H:%M') if rec.check_out else ''
                row.append(f'{ci}/{co}' if ci or co else '')
            else:
                row.append('')
        ws.append(row)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=attendance_{year}_{month}.xlsx'
    wb.save(response)
    return response
