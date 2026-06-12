from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime


RANK_CHOICES = [
    ('사원', '사원'),
    ('주임', '주임'),
    ('대리', '대리'),
    ('과장', '과장'),
    ('차장', '차장'),
    ('부장', '부장'),
    ('이사', '이사'),
    ('대표이사', '대표이사'),
]

RANK_ORDER = ['사원', '주임', '대리', '과장', '차장', '부장', '이사', '대표이사']


class Employee(AbstractUser):
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, default='사원', verbose_name='직급')
    department = models.CharField(max_length=100, blank=True, verbose_name='부서')
    join_date = models.DateField(default=datetime.date.today, verbose_name='입사일')
    annual_leave_days = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name='연차일수')

    class Meta:
        verbose_name = '직원'
        verbose_name_plural = '직원 목록'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.rank})'

    @property
    def is_admin(self):
        rank_idx = RANK_ORDER.index(self.rank) if self.rank in RANK_ORDER else 0
        return rank_idx >= RANK_ORDER.index('부장')

    def calculate_annual_leave(self):
        """근로기준법 제60조 기준 연차 계산"""
        today = datetime.date.today()
        delta = today - self.join_date
        total_days = delta.days
        years = total_days // 365
        months = (total_days % 365) // 30

        if years < 1:
            # 1년 미만: 매 1개월 개근 시 1일 (최대 11일)
            return min(months, 11)
        else:
            # 1년 이상: 15일 기본, 3년차부터 2년마다 1일 추가, 최대 25일
            extra = (years - 1) // 2
            return min(15 + extra, 25)

    def refresh_annual_leave(self):
        self.annual_leave_days = self.calculate_annual_leave()
        self.save(update_fields=['annual_leave_days'])
