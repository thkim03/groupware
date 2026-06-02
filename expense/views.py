from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from approvals.models import ApprovalDoc, ApprovalLine
from accounts.models import Employee
from .models import ExpenseRequest, ExpenseItem


@login_required
def expense_create(request):
    employees = Employee.objects.all().order_by('department', 'rank', 'username')
    if request.method == 'POST':
        title = request.POST.get('title')
        approver_ids = request.POST.getlist('approvers')
        descriptions = request.POST.getlist('item_desc')
        amounts = request.POST.getlist('item_amount')
        if not title or not approver_ids:
            messages.error(request, '모든 필드를 입력해주세요.')
        else:
            doc = ApprovalDoc.objects.create(
                doc_type='EXPENSE',
                status='DRAFT',
                title=title,
                author=request.user,
            )
            for i, aid in enumerate(approver_ids):
                ApprovalLine.objects.create(
                    doc=doc,
                    approver_id=int(aid),
                    order=i + 1,
                    status='WAITING',
                )
            er = ExpenseRequest.objects.create(
                doc=doc,
                source_type='MANUAL',
            )
            if request.FILES.get('attachment'):
                er.attachment = request.FILES['attachment']
                er.save()
            for desc, amount in zip(descriptions, amounts):
                if desc and amount:
                    ExpenseItem.objects.create(
                        expense=er,
                        description=desc,
                        amount=amount,
                    )
            doc.submit()
            messages.success(request, '지출결의서가 상신되었습니다.')
            return redirect('expense:expense_detail', pk=doc.pk)
    return render(request, 'expense/expense_form.html', {'employees': employees})


@login_required
def expense_detail(request, pk):
    doc = get_object_or_404(ApprovalDoc, pk=pk, doc_type='EXPENSE')
    if not request.user.is_admin and doc.author != request.user:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('dashboard:index')
    expense = get_object_or_404(ExpenseRequest, doc=doc)
    lines = doc.approval_lines.order_by('order')
    items = expense.items.all()
    total = expense.total_amount()
    return render(request, 'expense/expense_detail.html', {
        'doc': doc, 'expense': expense, 'lines': lines,
        'items': items, 'total': total
    })


@login_required
def expense_list(request):
    if not request.user.is_admin:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('dashboard:index')
    docs = ApprovalDoc.objects.filter(doc_type='EXPENSE').select_related('author').order_by('-created_at')
    return render(request, 'expense/expense_list.html', {'docs': docs})
