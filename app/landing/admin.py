from django.contrib import admin
from .models import Info, Skill, Experience, Education, Project, Contact, Contacto
from .models import MenuItem

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
    # Columnas visibles en la lista
    list_display = ('title', 'parent', 'order', 'is_active', 'display_groups')
    # Filtros laterales
    list_filter = ('parent', 'is_active', 'groups')
    # Buscador por título
    search_fields = ('title', 'url_name')
    # Permitir editar el orden y el estado activo directamente desde la lista
    list_editable = ('order', 'is_active')
    # Orden por defecto
    ordering = ('parent__id', 'order')
    
    # Configuración de los campos al editar
    filter_horizontal = ('groups',) # Interfaz mucho más cómoda para elegir grupos
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('title', 'icon', 'url_name', 'is_active')
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