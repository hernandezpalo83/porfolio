from rest_framework import serializers

def create_dynamic_serializer(model_class, fields_to_display, editable_fields):
    """
    Creates a ModelSerializer dynamically.
    """
    # Combine fields to display with editable fields to get all needed fields
    all_fields = list(set(list(fields_to_display) + list(editable_fields)))
    
    # Identify fields that should be read-only
    read_only_fields = [f for f in all_fields if f not in editable_fields]

    meta_attrs = {
        'model': model_class,
        'fields': all_fields,
        'read_only_fields': read_only_fields
    }
    
    Meta = type('Meta', (object,), meta_attrs)
    
    serializer_name = f"{model_class.__name__}DynamicSerializer"
    return type(serializer_name, (serializers.ModelSerializer,), {'Meta': Meta})
