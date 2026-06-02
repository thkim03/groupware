import datetime
from django.core.management.base import BaseCommand
from accounts.models import Employee


class Command(BaseCommand):
    help = '초기 데이터 생성 (관리자 계정)'

    def handle(self, *args, **options):
        if not Employee.objects.filter(username='admin').exists():
            emp = Employee.objects.create_superuser(
                username='admin',
                password='admin1234',
                first_name='관리자',
                last_name='',
                email='admin@groupware.local',
            )
            emp.rank = '대표이사'
            emp.department = '경영진'
            emp.join_date = datetime.date.today()
            emp.annual_leave_days = 15
            emp.save()
            self.stdout.write(self.style.SUCCESS('관리자 계정이 생성되었습니다. (admin/admin1234)'))
        else:
            self.stdout.write('관리자 계정이 이미 존재합니다.')
