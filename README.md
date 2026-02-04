# Groupware Project

사내 그룹웨어 시스템 (근태관리 + 전자결재 + 관리자 대시보드)

## 기술 스택
- Backend: Django
- Frontend: Django Template + Bootstrap 5
- DB: SQLite (개발), 추후 PostgreSQL 전환 가능
- Auth: Custom User Model

## 주요 기능
- 직원관리 (직급/권한)
- 근태관리 (출근/퇴근/출장)
- 전자결재 (휴가/출장/구매/지출/기타)
- 관리자 대시보드

## 실행 방법
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
