from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee, RANK_CHOICES


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard:index'))
        messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def employee_list(request):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    employees = Employee.objects.all().order_by('rank', 'username')
    return render(request, 'accounts/employee_list.html', {'employees': employees})


@login_required
def employee_create(request):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        rank = request.POST.get('rank', '사원')
        department = request.POST.get('department', '')
        join_date = request.POST.get('join_date')
        if Employee.objects.filter(username=username).exists():
            messages.error(request, '이미 존재하는 아이디입니다.')
        else:
            emp = Employee.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                rank=rank,
                department=department,
            )
            if join_date:
                emp.join_date = join_date
                emp.save()
            emp.refresh_annual_leave()
            messages.success(request, f'{emp} 직원이 등록되었습니다.')
            return redirect('accounts:employee_list')
    return render(request, 'accounts/employee_form.html', {'rank_choices': RANK_CHOICES, 'action': 'create'})


@login_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if not request.user.is_admin and request.user.pk != pk:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('dashboard:index')
    return render(request, 'accounts/employee_detail.html', {'emp': emp})


@login_required
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if not request.user.is_admin and request.user.pk != pk:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('dashboard:index')
    if request.method == 'POST':
        emp.first_name = request.POST.get('first_name', emp.first_name)
        emp.last_name = request.POST.get('last_name', emp.last_name)
        emp.email = request.POST.get('email', emp.email)
        emp.department = request.POST.get('department', emp.department)
        if request.user.is_admin:
            emp.rank = request.POST.get('rank', emp.rank)
            join_date = request.POST.get('join_date')
            if join_date:
                emp.join_date = join_date
        password = request.POST.get('password')
        if password:
            emp.set_password(password)
        emp.save()
        messages.success(request, '정보가 수정되었습니다.')
        return redirect('accounts:employee_detail', pk=emp.pk)
    return render(request, 'accounts/employee_form.html', {
        'emp': emp, 'rank_choices': RANK_CHOICES, 'action': 'edit'
    })
