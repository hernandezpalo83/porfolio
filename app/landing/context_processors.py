from .models import MenuItem
from django.db.models import Q
from django.core.cache import cache

def menu_int_processor(request):
    """
    Context processor para el menú interno.
    
    Optimizaciones:
    - Cache de 1 hora para usuarios anónimos
    - prefetch_related para submenús
    - Evita N+1 queries con groups
    """
    if not request.user.is_authenticated:
        return {'menu_items_int': []}

    # Intentar obtener del cache
    cache_key = f'menu_items_user_{request.user.id}'
    menu_items = cache.get(cache_key)
    
    if menu_items is None:
        # Obtenemos los grupos del usuario actual
        user_groups = request.user.groups.all()

        # Filtramos ítems activos, de primer nivel (sin padre) y que pertenezcan a los grupos del usuario
        menu_items = MenuItem.objects.filter(
            parent__isnull=True,
            is_active=True
        ).filter(
            Q(groups__in=user_groups) | Q(groups__isnull=True)
        ).distinct().prefetch_related('submenus', 'groups')
        
        # Cachear por 1 hora (3600 segundos)
        cache.set(cache_key, list(menu_items), 3600)
        menu_items = list(menu_items)

    return {
        'menu_items_int': menu_items
    }