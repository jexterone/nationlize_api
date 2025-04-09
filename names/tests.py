from django.test import TestCase
from rest_framework.test import APIClient
from names.models import NameData
from names.services import get_name_data, save_name_data, fetch_external_api
import requests
from unittest.mock import patch

class NameModelTestCase(TestCase):
    def test_create_name_data(self):
        """Тестирование создания записи в БД через модель."""
        name_data = NameData.objects.create(
            name="John",
            count=10,
            country=[{"country_id": "US", "probability": 0.8}]
        )
        self.assertEqual(name_data.name, "John")
        self.assertEqual(name_data.count, 10)
        self.assertEqual(name_data.country, [{"country_id": "US", "probability": 0.8}])

class ServiceTestCase(TestCase):
    def test_get_name_data_from_db(self):
        """Тестирование получения данных из БД через сервис."""
        NameData.objects.create(
            name="John",
            count=10,
            country=[{"country_id": "US", "probability": 0.8}]
        )
        result = get_name_data("John")
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'John')
        self.assertEqual(result['count'], 10)

    def test_get_name_data_not_found(self):
        """Тестирование случая, когда данные отсутствуют в БД."""
        result = get_name_data("NonExistentName")
        self.assertIsNone(result)

    @patch('requests.get')  # Мокаем запрос к внешнему API
    def test_fetch_external_api(self, mock_get):
        """Тестирование вызова внешнего API."""
        mock_response = {
            "name": "John",
            "country": [{"country_id": "US", "probability": 0.8}]
        }
        mock_get.return_value.json.return_value = mock_response

        result = fetch_external_api("John")
        self.assertEqual(result['name'], 'John')
        self.assertEqual(result['country'], [{"country_id": "US", "probability": 0.8}])

    def test_save_name_data(self):
        """Тестирование сохранения данных через сервис."""
        save_name_data("Alice", 5, [{"country_id": "GB", "probability": 0.7}])
        name_data = NameData.objects.get(name="Alice")
        self.assertEqual(name_data.count, 5)
        self.assertEqual(name_data.country, [{"country_id": "GB", "probability": 0.7}])

    def test_save_name_data_duplicate(self):
        """Тестирование попытки сохранить дубликат имени."""
        NameData.objects.create(
            name="John",
            count=10,
            country=[{"country_id": "US", "probability": 0.8}]
        )
        with self.assertRaises(ValueError) as context:
            save_name_data("John", 5, [{"country_id": "GB", "probability": 0.7}])
        self.assertEqual(str(context.exception), "Name already exists in database")

class NameViewTestCase(TestCase):
    def setUp(self):
        """Настройка клиента для тестирования API."""
        self.client = APIClient()

    def test_get_existing_name(self):
        """Тестирование GET-запроса для существующего имени."""
        NameData.objects.create(
            name="John",
            count=10,
            country=[{"country_id": "US", "probability": 0.8}]
        )
        response = self.client.get('/names/', {'name': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'John')
        self.assertEqual(response.data['count'], 10)

    @patch('requests.get')  # Мокаем запрос к внешнему API
    def test_get_nonexistent_name(self, mock_get):
        """Тестирование GET-запроса для имени, которого нет в БД."""
        mock_response = {
            "name": "Alice",
            "country": [{"country_id": "GB", "probability": 0.7}]
        }
        mock_get.return_value.json.return_value = mock_response

        response = self.client.get('/names/', {'name': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Alice')
        self.assertEqual(response.data['country'], [{"country_id": "GB", "probability": 0.7}])

    def test_post_new_name(self):
        """Тестирование POST-запроса для создания новой записи."""
        data = {
            'name': 'Alice',
            'count': 5,
            'country': [{'country_id': 'GB', 'probability': 0.7}]
        }
        response = self.client.post('/names/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Data saved successfully')

    def test_post_existing_name(self):
        """Тестирование POST-запроса для существующего имени."""
        NameData.objects.create(
            name="John",
            count=10,
            country=[{"country_id": "US", "probability": 0.8}]
        )
        data = {
            'name': 'John',
            'count': 5,
            'country': [{'country_id': 'GB', 'probability': 0.7}]
        }
        response = self.client.post('/names/', data, format='json')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['error'], 'Name already exists in database')

    def test_get_without_name_parameter(self):
        """Тестирование GET-запроса без параметра name."""
        response = self.client.get('/names/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Name parameter is required')
