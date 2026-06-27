"""
Тесты для Яндекс.Диск REST API
Проверка создания папки на Диске
"""

import pytest
import requests
import os

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Токен Яндекс.Диска (получить можно здесь: https://yandex.ru/dev/disk/poligon/)
# Для тестов нужно создать отдельную папку и использовать тестовый токен
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN', '')
BASE_URL = 'https://cloud-api.yandex.net/v1/disk'


# ============================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С API
# ============================================================

def create_folder(token, folder_path):
    """
    Создаёт папку на Яндекс.Диске
    Возвращает кортеж (status_code, response_json)
    """
    url = f"{BASE_URL}/resources"
    headers = {
        'Authorization': f'OAuth {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'path': folder_path,
        'overwrite': 'false'
    }
    
    response = requests.put(url, headers=headers, params=params)
    
    if response.status_code == 201:
        return response.status_code, response.json()
    elif response.status_code == 409:
        # Папка уже существует — это ошибка для нашего теста
        return response.status_code, response.json()
    else:
        # Другие ошибки
        return response.status_code, response.json()


def check_folder_exists(token, folder_path):
    """
    Проверяет, существует ли папка на Яндекс.Диске
    Возвращает True/False
    """
    url = f"{BASE_URL}/resources"
    headers = {
        'Authorization': f'OAuth {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'path': folder_path
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.status_code == 200


def delete_folder(token, folder_path):
    """
    Удаляет папку на Яндекс.Диске (для очистки после тестов)
    """
    url = f"{BASE_URL}/resources"
    headers = {
        'Authorization': f'OAuth {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'path': folder_path,
        'permanently': 'true'
    }
    
    response = requests.delete(url, headers=headers, params=params)
    return response.status_code


# ============================================================
# ТЕСТЫ
# ============================================================

@pytest.mark.skipif(not YANDEX_DISK_TOKEN, reason="Токен Яндекс.Диска не задан")
class TestYandexDiskCreateFolder:
    """Тесты для создания папки на Яндекс.Диске"""
    
    # Имя тестовой папки с временной меткой для уникальности
    TEST_FOLDER = f"test_folder_{int(__import__('time').time())}"
    
    def test_create_folder_success(self):
        """
        Позитивный тест: успешное создание папки
        Ожидаемый код ответа: 201
        """
        status_code, response = create_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
        
        # Проверяем код ответа
        assert status_code == 201, f"Ожидался код 201, получен {status_code}"
        
        # Проверяем, что папка появилась в списке
        assert check_folder_exists(YANDEX_DISK_TOKEN, self.TEST_FOLDER), \
            "Папка не найдена на Диске после создания"
        
        # Очищаем после теста
        delete_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
    
    def test_create_folder_already_exists(self):
        """
        Негативный тест: создание папки, которая уже существует
        Ожидаемый код ответа: 409 (Conflict)
        """
        # Создаём папку первый раз
        status_code, _ = create_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
        assert status_code == 201, "Не удалось создать папку для теста"
        
        # Пытаемся создать папку с тем же именем
        status_code, response = create_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
        
        # Проверяем код ответа
        assert status_code == 409, f"Ожидался код 409, получен {status_code}"
        assert response.get('error') == 'DiskPathPointsToExistentDirectoryError', \
            "Ошибка не соответствует ожидаемой"
        
        # Очищаем после теста
        delete_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
    
    def test_create_folder_invalid_token(self):
        """
        Негативный тест: неверный токен
        Ожидаемый код ответа: 401 (Unauthorized)
        """
        invalid_token = "invalid_token_123"
        status_code, _ = create_folder(invalid_token, self.TEST_FOLDER)
        
        assert status_code == 401, f"Ожидался код 401, получен {status_code}"
    
    def test_create_folder_invalid_path(self):
        """
        Негативный тест: недопустимое имя папки (слишком длинное)
        Ожидаемый код ответа: 404 (Not Found) или 400
        """
        long_name = "a" * 300
        status_code, _ = create_folder(YANDEX_DISK_TOKEN, long_name)
    
        # Яндекс.Диск возвращает 404 для слишком длинных имён
        assert status_code in [400, 404], f"Ожидался код 400 или 404, получен {status_code}"
    
    def test_create_folder_check_listing(self):
        """
        Позитивный тест: проверка, что папка появляется в списке файлов
        """
        # Создаём папку
        status_code, _ = create_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)
        assert status_code == 201, "Не удалось создать папку"
        
        # Проверяем, что папка есть в списке
        assert check_folder_exists(YANDEX_DISK_TOKEN, self.TEST_FOLDER), \
            "Папка не найдена на Диске"
        
        # Дополнительная проверка: запрос к ресурсам показывает, что это папка
        url = f"{BASE_URL}/resources"
        headers = {'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'}
        params = {'path': self.TEST_FOLDER}
        
        response = requests.get(url, headers=headers, params=params)
        assert response.status_code == 200, "Не удалось получить информацию о папке"
        
        data = response.json()
        assert data.get('type') == 'dir', "Созданный ресурс не является папкой"
        assert data.get('name') == self.TEST_FOLDER, "Имя папки не совпадает"
        
        # Очищаем после теста
        delete_folder(YANDEX_DISK_TOKEN, self.TEST_FOLDER)


# ============================================================
# ЗАПУСК ТЕСТОВ
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ ДЛЯ ЯНДЕКС.ДИСК API")
    print("=" * 60)
    
    if not YANDEX_DISK_TOKEN:
        print("\n⚠️ Токен Яндекс.Диска не задан!")
        print("Установите переменную окружения YANDEX_DISK_TOKEN")
        print("или укажите токен прямо в коде.")
        print("Получить токен можно здесь: https://yandex.ru/dev/disk/poligon/")
    
    pytest.main([__file__, "-v", "--tb=short"])