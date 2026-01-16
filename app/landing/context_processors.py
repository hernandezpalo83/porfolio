from .models import MenuItem
from django.db.models import Q

def menu_int_processor(request):
    if not request.user.is_authenticated:
        return {'menu_items_int': []}

    # Obtenemos los grupos del usuario actual
    user_groups = request.user.groups.all()

    # Filtramos ítems activos, de primer nivel (sin padre) y que pertenezcan a los grupos del usuario
    # Si un ítem no tiene grupos asignados, podrías decidir si es público para todos los logueados
    menu_items = MenuItem.objects.filter(
        parent__isnull=True,
        is_active=True
    ).filter(
        Q(groups__in=user_groups) | Q(groups__isnull=True)
    ).distinct().prefetch_related('submenus')

    return {
        'menu_items_int': menu_items
    }