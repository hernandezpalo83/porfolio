from django.contrib import admin
from .models import Info, Skill, Experience, Education, Project, Contact, Contacto, Metric
from .models import MenuItem

@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address')
    search_fields = ('name', 'email', 'phone', 'address')
    list_filter = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'score')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('score',)
    list_editable = ('score',)
    ordering = ('-score',)

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
    list_display = ('title', 'categoria', 'get_description_short')
    search_fields = ('title', 'categoria', 'description')
    list_filter = ('categoria',)
    readonly_fields = ('get_description_preview',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'categoria')
        }),
        ('Contenido', {
            'fields': ('description', 'get_description_preview')
        }),
        ('Enlaces', {
            'fields': ('imagen', 'link')
        }),
    )
    
    def get_description_short(self, obj):
        """Mostrar descripción corta en el listado"""
        from django.utils.html import strip_tags
        texto = strip_tags(obj.description) if obj.description else ""
        return texto[:50] + "..." if len(texto) > 50 else texto
    get_description_short.short_description = "Descripción"
    
    def get_description_preview(self, obj):
        """Preview HTML de la descripción en readonly"""
        if obj and obj.pk:
            from django.utils.safestring import mark_safe
            return mark_safe(obj.description) if obj.description else "(vacío)"
        return "(Guarda primero para ver el preview)"
    get_description_preview.short_description = "Preview"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone')
    search_fields = ('email', 'phone')
    list_filter = ('email',)
    readonly_fields = ('email', 'phone')

class GlobalAdminMedia:
    class Media:
        css = {
            'all': ('landing/css/admin_dark_ckeditor.css',)
        }
        
for model, model_admin in admin.site._registry.items():
    if not hasattr(model_admin, 'Media'):
        model_admin.__class__.Media = GlobalAdminMedia.Media

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    # Columnas que se verán en el listado principal
    list_display = ('nombre', 'email', 'asunto', 'fecha_envio', 'leido')
    
    # Filtros laterales (muy útiles cuando tengas muchos mensajes)
    list_filter = ('leido', 'fecha_envio')
    
    # Buscador para encontrar mensajes por nombre, email o contenido
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    
    # Orden predeterminado: los más nuevos primero
    ordering = ('-fecha_envio',)
    
    # Campos que solo queremos leer (no editar la fecha de envío)
    readonly_fields = ('fecha_envio',)
    
    # Acción personalizada para gestionar el flujo de trabajo (Workflow)
    actions = ['marcar_como_leido', 'marcar_como_no_leido']

    @admin.action(description="Marcar seleccionados como LEÍDOS")
    def marcar_como_leido(self, request, queryset):
        filas_actualizadas = queryset.update(leido=True)
        self.message_user(request, f"{filas_actualizadas} mensajes han sido marcados como leídos.")

    @admin.action(description="Marcar seleccionados como NO LEÍDOS")
    def marcar_como_no_leido(self, request, queryset):
        filas_actualizadas = queryset.update(leido=False)
        self.message_user(request, f"{filas_actualizadas} mensajes han sido marcados como no leídos.")

    # Esto hace que el panel sea más limpio
    fieldsets = (
        ('Información del Remitente', {
            'fields': ('nombre', 'email')
        }),
        ('Contenido del Mensaje', {
            'fields': ('asunto', 'mensaje')
        }),
        ('Estado y Registro', {
            'fields': ('leido', 'fecha_envio')
        }),
    )
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'app_name', 'url_name', 'parent', 'order', 'is_active')
    list_editable = ( 'app_name','url_name', 'order', 'is_active')
    list_filter = ('parent', 'is_active', 'groups')
    search_fields = ('title', 'url_name')
    ordering = ('parent__id', 'order')
    
    # Configuración de los campos al editar
    filter_horizontal = ('groups',) # Interfaz mucho más cómoda para elegir grupos
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('title', 'icon', 'app_name','url_name', 'is_active')
        }),
        ('Jerarquía y Orden', {
            'fields': ('parent', 'order')
        }),
        ('Control de Acceso', {
            'fields': ('groups',),
            'description': 'Si no se selecciona ningún grupo, el ítem será visible para todos los usuarios logueados.'
        }),
    )

    def display_groups(self, obj):
        """Muestra los nombres de los grupos en la lista del admin."""
        return ", ".join([g.name for g in obj.groups.all()])
    display_groups.short_description = 'Grupos con acceso'

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'get_display_value', 'is_visible')
    list_display_links = ('title',)
    list_editable = ('order', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('title', 'description')
    ordering = ('order', 'id')
    
    fieldsets = (
        ('Valor', {
            'fields': ('value', 'prefix', 'suffix')
        }),
        ('Contenido', {
            'fields': ('title', 'description')
        }),
        ('Configuración', {
            'fields': ('is_visible', 'order')
        }),
    )
    
    def get_display_value(self, obj):
        """Muestra el valor formateado en el listado"""
        return f"{obj.prefix}{obj.value}{obj.suffix}"
    get_display_value.short_description = 'Valor'