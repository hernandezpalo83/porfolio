import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def to_json(value):
    """Convierte un objeto Python a una cadena JSON válida."""
    return mark_safe(json.dumps(value))

@register.filter
def get_item(dictionary, key):
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def replace(value, arg):
    """Replaces a string with another. Usage: {{ value|replace:"old,new" }}"""
    if ',' not in arg:
        return value.replace(arg, '')
    old, new = arg.split(',', 1)
    return value.replace(old, new)



# ==========================================
# 1. ELEMENTOS ATÓMICOS (19 Elementos)
# ==========================================

@register.inclusion_tag('components_ui/elementos/button.html')
def comp_button(text, appearance='contained', color='primary', icon=None, icon_right=None, size='medium',
                loading=False, disabled=False, onclick=None, tooltip=None, classes="", style="", type="button", form=None, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/input_text.html')
def comp_input_text(name, label='', required=False, placeholder='', type='text',
                    value='', icon=None, mask=None, validation=None, classes="", readonly=False, disabled=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/input_date.html')
def comp_input_date(name, label='', required=False, value='', icon='CalendarIcon', classes="", disabled=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/input_number.html')
def comp_input_number(name, label='', required=False, value='', min_val=None, max_val=None, step='any', classes="", disabled=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/icon.html')
def comp_icon(name, color="currentColor", size="w-6 h-6", classes="", solid=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/image.html')
def comp_image(src, alt='', width='auto', height='auto', rounded=True, classes="", object_fit="cover", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/modal.html')
def comp_modal(id, title='', classes="", width="md:w-1/2", open_on_load=False, close_on_click_outside=True, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/dropdown.html')
def comp_dropdown(name, options, label='', required=False, value='', classes="", disabled=False, multiple=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/menu_list.html')
def comp_menu_list(items, title='', classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/toggle.html')
def comp_toggle(name, label='', checked=False, disabled=False, color='primary', classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/tooltip.html')
def comp_tooltip(text, position="top", classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/notification.html')
def comp_notification(id, message='', type='info', duration=3000, classes="", position="bottom-right", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/calendar.html')
def comp_calendar(name, value='', classes="", locale="es", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/app_bar.html')
def comp_app_bar(title='', color='primary', classes="", shadow=True, fixed=False, left_icon=None, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/title.html')
def comp_title(text, level=1, color='text-gray-900', classes="", hr=False, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/card.html')
def comp_card(title=None, subtitle=None, value=None, classes="", padding="p-6", shadow="shadow-md", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/floating_button.html')
def comp_floating_button(icon, color='primary', position='bottom-right', onclick=None, classes="", tooltip=None, **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/chart.html')
def comp_chart(id, type='bar', data=None, options=None, height='400px', classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/elementos/gauge.html')
def comp_gauge(id, value=0, min_val=0, max_val=100, label='', color='primary', classes="", **kwargs):
    return locals()


# ==========================================
# 2. COMPONENTES COMPLEJOS (33 Componentes)
# ==========================================

@register.inclusion_tag('components_ui/componentes/agenda.html', takes_context=True)
def comp_agenda(context, data_url, editable=False, view_mode='month', initial_date=None, 
                disable_day_mode=False, permisos=None, onclick_evento=None, onclick_dia=None, classes="", locale="es", **kwargs):
    return {
        'request': context.get('request'),
        'data_url': data_url,
        'editable': editable,
        'view_mode': view_mode,
        'initial_date': initial_date,
        'disable_day_mode': disable_day_mode,
        'permisos': permisos,
        'onclick_evento': onclick_evento,
        'onclick_dia': onclick_dia,
        'classes': classes,
        'locale': locale,
        **kwargs
    }

@register.inclusion_tag('components_ui/componentes/tabla.html')
def comp_tabla(data_url, columns=None, editable=False, page_size=10, selectable=False, 
               group_by=None, searchable=False, filterable=False, height="400px", 
               theme="modern", classes="", **kwargs):
    """
    Componente de tabla avanzada basado en Tabulator.
    """
    if columns is None: columns = []
    return locals()

@register.inclusion_tag('components_ui/componentes/tabla_mantenimiento.html')
def comp_tabla_mantenimiento(data_url, columns=None, create_url=None, group_by=None, 
                           searchable=True, filterable=True, theme="modern", classes="", **kwargs):
    """
    Versión de Tabulator optimizada para CRUD.
    """
    if columns is None: columns = []
    return locals()

@register.inclusion_tag('components_ui/componentes/formulario.html', takes_context=True)
def comp_formulario(context, action='.', method='POST', id='auto_form', classes="", **kwargs):
    request = context.get('request')
    csrf_token = context.get('csrf_token')
    return locals()

@register.inclusion_tag('components_ui/componentes/navbar.html', takes_context=True)
def comp_navbar(context, title='App', links=None, show_user=True, classes="", **kwargs):
    request = context.get('request')
    return locals()

@register.inclusion_tag('components_ui/componentes/sidebar_menu.html', takes_context=True)
def comp_sidebar_menu(context, menu_items=None, is_open=True, classes="", **kwargs):
    request = context.get('request')
    return locals()

@register.inclusion_tag('components_ui/componentes/tabs.html')
def comp_tabs(id, tabs_data, active_tab=0, classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/componentes/tabla_informes.html')
def comp_tabla_informes(data_url, columns=None, export_url=None, group_by=None, 
                       height="600px", filterable=True, theme="bulma", classes="", **kwargs):
    """
    Versión de Tabulator para reportes detallados con exportación.
    """
    if columns is None: columns = []
    return locals()

@register.inclusion_tag('components_ui/componentes/animacion_contenedor.html')
def comp_animacion_contenedor(type="fadeIn", duration="300ms", delay="0ms", classes="", **kwargs):
    return locals()

@register.inclusion_tag('components_ui/componentes/desplegable.html')
def comp_desplegable(name, lookup_url, label='', value='', display_value='', required=False, classes="", **kwargs):
    """Select2 o similar con búsqueda remota"""
    return locals()

@register.inclusion_tag('components_ui/componentes/permisos.html', takes_context=True)
def comp_permisos(context, required_perms, any_perm=False, **kwargs):
    """Renderiza contenido solo si el usuario tiene permiso"""
    request = context.get('request')
    return locals()

# --- 22 Componentes Genéricos Adicionales para llegar a los 33 total mapeados ---

@register.inclusion_tag('components_ui/componentes/acordeon.html')
def comp_acordeon(id, items, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/breadcrumbs.html')
def comp_breadcrumbs(items, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/carousel.html')
def comp_carousel(items, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/steps.html')
def comp_steps(current_step, steps, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/avatar.html')
def comp_avatar(user, size='md', show_name=False, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/badge.html')
def comp_badge(text, color='primary', type='solid', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/alert.html')
def comp_alert(text, type='info', dismissible=True, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/spinner.html')
def comp_spinner(size='md', color='primary', text='', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/progress_bar.html')
def comp_progress_bar(value, max_val=100, color='primary', show_label=False, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/skeleton.html')
def comp_skeleton(type='text', width='100%', height='100%', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/list_group.html')
def comp_list_group(items, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/timeline.html')
def comp_timeline(items, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_tree_view(data_url, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_file_upload(name, label='', multiple=False, accept='*/*', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_color_picker(name, label='', value='#000000', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_rating(name, value=0, max_stars=5, read_only=False, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_rich_text_editor(name, value='', height='300px', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/map.html')
def comp_map(id, center_lat, center_lng, zoom=13, markers=None, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_video_player(src, poster='', controls=True, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_audio_player(src, controls=True, classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_pdf_viewer(src, height='600px', classes="", **kwargs): return locals()

@register.inclusion_tag('components_ui/componentes/comp_generico.html')
def comp_qr_code(data, size=128, classes="", **kwargs): return locals()
