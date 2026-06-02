from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'rank', 'department', 'join_date', 'annual_leave_days')
    list_filter = ('rank', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('직원 정보', {'fields': ('rank', 'department', 'join_date', 'annual_leave_days')}),
    )
