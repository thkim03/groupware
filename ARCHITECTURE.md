# 시스템 구조

## 앱 분리 원칙
- accounts : 사용자 / 직급 / 권한
- attendance : 근태 관리
- approvals : 결재 엔진 (공통)
- leave / trip / purchase / expense : 도메인 화면 및 로직

※ approvals는 "결재 프레임워크" 역할만 담당

---

## approvals 책임 범위
- ApprovalDoc
- ApprovalLine
- ApprovalLog
- Attachment
- 결재함 / 문서 검색 / 결재 처리

---

## 도메인 앱 책임
- 입력 폼
- 항목 관리
- 자동 생성 로직
- 화면(UI)

---

## 템플릿 구조
templates/
  layout/
    base.html
  approvals/
    inbox/
    read/
  trip/
  purchase/
  expense/
