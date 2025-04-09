from rest_framework import serializers
from .models import NameData

class NameDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NameData
        fields = ['name', 'count', 'country']
        extra_kwargs = {
            'name': {'validators': []}  # Отключаем валидацию уникальности
        }

    def validate_country(self, value):
        """Проверяем структуру массива стран"""
        for item in value:
            if not all(k in item for k in ['country_id', 'probability']):
                raise serializers.ValidationError("Each country must contain 'country_id' and 'probability'")
        return value