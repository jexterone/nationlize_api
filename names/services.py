from django.core.cache import cache
from .models import NameData
import requests

def get_name_data(name):
    # Проверка кэша
    cache_key = f'name_{name}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Проверка БД
    try:
        name_data = NameData.objects.get(name=name)
        response_data = {
            'name': name_data.name,
            'count': name_data.count,
            'country': name_data.country
        }
        cache.set(cache_key, response_data, timeout=300)
        return response_data
    except NameData.DoesNotExist:
        return None

def fetch_external_api(name):
    try:
        response = requests.get(f'https://api.nationalize.io/?name={name}')
        data = response.json()
        return {
            'name': data['name'],
            'count': data.get('count', 0),
            'country': data['country']
        }
    except Exception as e:
        raise ValueError(str(e))

def save_name_data(name, count, country):
    if NameData.objects.filter(name=name).exists():
        raise ValueError("Name already exists in database")
    NameData.objects.create(name=name, count=count, country=country)