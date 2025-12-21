from django.contrib import admin
from .models import Info, Skill, Experience, Education, Project, Contact

@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address')
    search_fields = ('name', 'email', 'phone', 'address')
    list_filter = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'position', 'start_date', 'end_date')
    search_fields = ('company', 'position')
    list_filter = ('company', 'position')
    ordering = ('-start_date',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'start_date', 'end_date')
    search_fields = ('institution', 'degree')
    list_filter = ('institution', 'degree')
    ordering = ('-start_date',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('title',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone')
    search_fields = ('email', 'phone')
    list_filter = ('email',)

class GlobalAdminMedia:
    class Media:
        css = {
            'all': ('landing/css/admin_dark_ckeditor.css',)
        }
        
for model, model_admin in admin.site._registry.items():
    if not hasattr(model_admin, 'Media'):
        model_admin.__class__.Media = GlobalAdminMedia.Media
        