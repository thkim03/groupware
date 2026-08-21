from django.db import models
from django.conf import settings


class Schedule(models.Model):
    CATEGORY_CHOICES = [
        ('PERSONAL', '개인'),
        ('SHARED', '전체공유'),
    ]
    COLOR_CHOICES = [
        ('#0d6efd', '파랑'),
        ('#198754', '초록'),
        ('#dc3545', '빨강'),
        ('#ffc107', '노랑'),
        ('#0dcaf0', '하늘'),
        ('#6c757d', '회색'),
        ('#6f42c1', '보라'),
    ]

    title = models.CharField(max_length=200, verbose_name='제목')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    all_day = models.BooleanField(default=True, verbose_name='종일여부')
    start_time = models.TimeField(null=True, blank=True, verbose_name='시작시간')
    end_time = models.TimeField(null=True, blank=True, verbose_name='종료시간')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='PERSONAL', verbose_name='공개범위')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='#0d6efd', verbose_name='색상')
    memo = models.TextField(blank=True, verbose_name='메모')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='schedules', verbose_name='작성자')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '일정'
        verbose_name_plural = '일정 목록'
        ordering = ['start_date', 'start_time']

    def __str__(self):
        return self.title
