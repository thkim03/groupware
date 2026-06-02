from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from approvals.models import ApprovalDoc, ApprovalLine
from accounts.models import Employee
from .models import PurchaseRequest, PurchaseItem


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        if not request.user.is_admin:
            messages.error(request, '관리자만 접근할 수 있습니다.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def purchase_create(request):
    employees = Employee.objects.all().order_by('department', 'rank', 'username')
    if request.method == 'POST':
        title = request.POST.get('title')
        approver_ids = request.POST.getlist('approvers')
        names = request.POST.getlist('item_name')
        prices = request.POST.getlist('item_price')
        qtys = request.POST.getlist('item_qty')
        if not title or not approver_ids or not names:
            messages.error(request, '모든 필드를 입력해주세요.')
        else:
            doc = ApprovalDoc.objects.create(
                doc_type='PURCHASE',
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
            pr = PurchaseRequest.objects.create(doc=doc)
            for name, price, qty in zip(names, prices, qtys):
                if name:
                    PurchaseItem.objects.create(
                        purchase=pr,
                        name=name,
                        unit_price=price or 0,
                        quantity=qty or 1,
                    )
            doc.submit()
            messages.success(request, '구매요청서가 상신되었습니다.')
            return redirect('purchase:purchase_detail', pk=doc.pk)
    return render(request, 'purchase/purchase_form.html', {'employees': employees})


@admin_required
def purchase_detail(request, pk):
    doc = get_object_or_404(ApprovalDoc, pk=pk, doc_type='PURCHASE')
    purchase = get_object_or_404(PurchaseRequest, doc=doc)
    lines = doc.approval_lines.order_by('order')
    items = purchase.items.all()
    total = sum(item.total for item in items)
    return render(request, 'purchase/purchase_detail.html', {
        'doc': doc, 'purchase': purchase, 'lines': lines,
        'items': items, 'total': total
    })


@admin_required
def purchase_list(request):
    docs = ApprovalDoc.objects.filter(doc_type='PURCHASE').select_related('author').order_by('-created_at')
    return render(request, 'purchase/purchase_list.html', {'docs': docs})
