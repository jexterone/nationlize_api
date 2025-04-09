from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_name_data, fetch_external_api, save_name_data
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class NameView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Имя для поиска",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        name = request.query_params.get('name')
        if not name:
            return Response(
                {'error': 'Name parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = get_name_data(name)
        if data:
            return Response(data)

        try:
            external_data = fetch_external_api(name)
            return Response(external_data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя'),
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество'),
                'country': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                          description='Страны'),
            },
            required=['name', 'count', 'country']
        )
    )
    def post(self, request):
        name = request.data.get('name')
        count = request.data.get('count')
        country = request.data.get('country', [])

        try:
            save_name_data(name, count, country)
            return Response({'message': 'Data saved successfully'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)