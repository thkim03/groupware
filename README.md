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

## PDF → Markdown 변환기
PySide6 기반 GUI 도구로, PDF 파일을 Markdown 형식으로 변환합니다.

### 기능
- 드래그 & 드롭으로 PDF 파일 선택
- 텍스트 서식(볼드/이탤릭/헤딩) 자동 감지
- 테이블 자동 변환
- 이미지 추출 및 저장
- 실시간 변환 미리보기
- Figma 스타일 다크 테마 UI

### 실행 방법
```bash
pip install -r requirements.txt
python -m pdf_converter.main
```

## 그룹웨어 실행 방법
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
