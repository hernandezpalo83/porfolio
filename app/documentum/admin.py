"""
Django Admin Configuration for Documentation Hub
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Document, DocumentVersion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'document_count_display', 'order', 'is_visible')
    list_display_links = ('name',)
    list_editable = ('order', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'order', 'is_visible')
        }),
    )
    
    def document_count_display(self, obj):
        count = obj.document_count
        url = reverse('admin:docs_document_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{} docs</a>', url, count)
    document_count_display.short_description = 'Documents'


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    fields = ('created_at', 'changed_by', 'change_summary')
    readonly_fields = ('created_at', 'changed_by', 'change_summary')
    can_delete = False
    max_num = 5
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'stack_version', 'reading_time_display', 'last_revision')
    list_display_links = ('title',)
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content_markdown', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'status')
        }),
        ('Content', {
            'fields': ('content_markdown', 'content_preview'),
            'description': 'Write in Markdown. HTML preview is auto-generated.'
        }),
        ('Metadata', {
            'fields': ('stack_version', 'last_revision'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',),
            'description': 'Optimize for search engines'
        }),
    )
    
    readonly_fields = ('content_preview', 'last_revision')
    inlines = [DocumentVersionInline]
    
    def content_preview(self, obj):
        """Show HTML preview of Markdown content"""
        if obj and obj.pk:
            return mark_safe(f'<div style="border:1px solid #ddd; padding:15px; background:#f9f9f9; max-height:400px; overflow:auto;">{obj.content_html}</div>')
        return "(Save to see preview)"
    content_preview.short_description = "HTML Preview"
    
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
    reading_time_display.short_description = "Reading Time"
    
    def save_model(self, request, obj, form, change):
        """Override to track who made changes"""
        super().save_model(request, obj, form, change)
        # Update the last version's changed_by field
        if obj.versions.exists():
            last_version = obj.versions.first()
            last_version.changed_by = request.user.username
            last_version.save()


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'created_at', 'changed_by', 'change_summary_short')
    list_filter = ('document__category', 'created_at')
    search_fields = ('document__title', 'changed_by', 'change_summary')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fields = ('document', 'content_markdown', 'created_at', 'changed_by', 'change_summary')
    readonly_fields = ('created_at',)
    
    def change_summary_short(self, obj):
        return obj.change_summary[:50] + '...' if len(obj.change_summary) > 50 else obj.change_summary
    change_summary_short.short_description = 'Summary'
    
    def has_add_permission(self, request):
        return False  # Versions are auto-created
