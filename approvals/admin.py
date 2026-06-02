from django.contrib import admin
from .models import ApprovalDoc, ApprovalLine, ApprovalLog, Attachment

class ApprovalLineInline(admin.TabularInline):
    model = ApprovalLine
    extra = 0

@admin.register(ApprovalDoc)
class ApprovalDocAdmin(admin.ModelAdmin):
    list_display = ('title', 'doc_type', 'status', 'author', 'created_at')
    list_filter = ('doc_type', 'status')
    inlines = [ApprovalLineInline]

admin.site.register(ApprovalLog)
admin.site.register(Attachment)
