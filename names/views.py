from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import NameData
from .serializers import NameDataSerializer


class NameView(APIView):
    # GET метод остается без изменений
    def get(self, request):
        name = request.query_params.get('name')
        if not name:
            return Response(
                {'error': 'Name parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка кэша
        cache_key = f'name_{name}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Проверка БД
        try:
            name_data = NameData.objects.get(name=name)
            serializer = NameDataSerializer(name_data)
            response_data = {
                'name': serializer.data['name'],
                'count': serializer.data['count'],
                'country': serializer.data['country']  # Теперь поле называется 'country'
            }
            cache.set(cache_key, response_data, timeout=300)
            return Response(response_data)
        except NameData.DoesNotExist:
            # Запрос к внешнему API (если нужно)
            try:
                response = requests.get(f'https://api.nationalize.io/?name={name}')
                data = response.json()
                return Response({
                    'name': data['name'],
                    'count': data.get('count', 0),
                    'country': data['country']  # Соответствует новому формату
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

    # POST метод с обновленной логикой (как в предыдущем ответе)
    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'count': request.data.get('count'),
            'country': request.data.get('country', [])
        }

        serializer = NameDataSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data format', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        name = serializer.validated_data['name']
        if NameData.objects.filter(name=name).exists():
            return Response(
                {'error': 'Name already exists in database'},
                status=status.HTTP_409_CONFLICT
            )

        serializer.save()
        return Response(
            {'message': 'Data saved successfully'},
            status=status.HTTP_201_CREATED
        )