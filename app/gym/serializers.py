from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        precio = data.get('precio')
        coste = data.get('coste', 0)
        if precio is not None and precio < 0:
            raise serializers.ValidationError({'precio': 'El precio no puede ser negativo.'})
        if coste is not None and coste < 0:
            raise serializers.ValidationError({'coste': 'El coste no puede ser negativo.'})
        if precio is not None and coste is not None and precio < coste:
            raise serializers.ValidationError(
                {'precio': 'El precio no puede ser menor al costo.'}
            )
        return data
