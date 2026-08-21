from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='제목')),
                ('start_date', models.DateField(verbose_name='시작일')),
                ('end_date', models.DateField(verbose_name='종료일')),
                ('all_day', models.BooleanField(default=True, verbose_name='종일여부')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='시작시간')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='종료시간')),
                ('category', models.CharField(choices=[('PERSONAL', '개인'), ('SHARED', '전체공유')], default='PERSONAL', max_length=20, verbose_name='공개범위')),
                ('color', models.CharField(choices=[('#0d6efd', '파랑'), ('#198754', '초록'), ('#dc3545', '빨강'), ('#ffc107', '노랑'), ('#0dcaf0', '하늘'), ('#6c757d', '회색'), ('#6f42c1', '보라')], default='#0d6efd', max_length=20, verbose_name='색상')),
                ('memo', models.TextField(blank=True, verbose_name='메모')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to=settings.AUTH_USER_MODEL, verbose_name='작성자')),
            ],
            options={
                'verbose_name': '일정',
                'verbose_name_plural': '일정 목록',
                'ordering': ['start_date', 'start_time'],
            },
        ),
    ]
