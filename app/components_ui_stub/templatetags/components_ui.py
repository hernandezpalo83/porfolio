"""
Stub de django-components-ui para entornos CI sin acceso al paquete privado.
Registra todos los tags como no-ops que devuelven cadena vacía.
Solo se usa cuando DJANGO_ENV=testing y el paquete real no está instalado.
"""
from django import template

register = template.Library()

# Tags de inclusión usados en las plantillas del proyecto
_INCLUSION_TAGS = [
    'comp_tabla_mantenimiento',
    'comp_tabla',
    'comp_button',
    'comp_card',
    'comp_title',
    'comp_badge',
    'comp_icon',
    'comp_tabs',
    'comp_acordeon',
    'comp_steps',
    'comp_breadcrumbs',
    'comp_login_form',
    'comp_empty_state',
    'comp_stat_grid',
    'comp_search_bar',
    'comp_confirm_action',
    'comp_copy_button',
]

for _tag_name in _INCLUSION_TAGS:
    def _make_noop(name):
        @register.simple_tag(name=name, takes_context=True)
        def _noop(context, *args, **kwargs):
            return ''
        return _noop
    _make_noop(_tag_name)

# Filtros que el paquete expone
@register.filter(name='to_json')
def to_json(value):
    import json
    return json.dumps(value)
