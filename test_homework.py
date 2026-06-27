"""
Тесты для заданий из модуля «Основы языка программирования Python»
Используются решения из предыдущих домашних заданий
"""

import pytest
import re
from datetime import datetime

# ============================================================
# ФУНКЦИИ ДЛЯ ТЕСТИРОВАНИЯ (из предыдущих ДЗ)
# ============================================================

# --- Функция из ДЗ «Итераторы и генераторы» ---
def flat_generator(list_of_list):
    """Генератор плоского представления списка списков"""
    for sublist in list_of_list:
        for item in sublist:
            yield item


# --- Функция из ДЗ «Декораторы» (логирование) ---
def sum_numbers(a, b):
    """Сложение двух чисел"""
    return a + b


def multiply_numbers(a, b):
    """Умножение двух чисел"""
    return a * b


# --- Функция из ДЗ «Регулярные выражения» (обработка телефонов) ---
def normalize_phone(phone):
    """
    Приводит телефон к формату +7(999)999-99-99
    """
    if not phone:
        return ""
    
    # Убираем все лишние символы, оставляем только цифры
    digits = re.sub(r'\D', '', phone)
    
    # Ищем добавочный номер
    ext_match = re.search(r'(доб\.|доп\.|ext\.)\s*(\d{4})', phone, re.IGNORECASE)
    ext = ""
    if ext_match:
        ext = f" доб.{ext_match.group(2)}"
    
    # Форматируем основной номер
    if len(digits) == 10:
        digits = '7' + digits
    elif len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 11 and digits.startswith('7'):
        pass
    else:
        return phone
    
    if not digits.startswith('7') or len(digits) != 11:
        return phone
    
    return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:11]}" + ext


# ============================================================
# ТЕСТЫ ДЛЯ ФУНКЦИЙ
# ============================================================

# --- Тесты для flat_generator ---
class TestFlatGenerator:
    """Тесты для генератора flat_generator"""
    
    def test_flat_generator_basic(self):
        """Тест: базовое преобразование списка списков"""
        list_of_lists = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
            [1, 2, 3]
        ]
        result = list(flat_generator(list_of_lists))
        expected = ['a', 'b', 'c', 'd', 'e', 'f', 1, 2, 3]
        assert result == expected
    
    def test_flat_generator_empty(self):
        """Тест: пустой список"""
        list_of_lists = [[], [], []]
        result = list(flat_generator(list_of_lists))
        expected = []
        assert result == expected
    
    def test_flat_generator_mixed_types(self):
        """Тест: смешанные типы данных"""
        list_of_lists = [
            [1, 'a', True],
            [None, 2.5, False],
            ['b', 3]
        ]
        result = list(flat_generator(list_of_lists))
        expected = [1, 'a', True, None, 2.5, False, 'b', 3]
        assert result == expected
    
    @pytest.mark.parametrize("input_data, expected", [
        ([['a', 'b'], ['c', 'd']], ['a', 'b', 'c', 'd']),
        ([['x'], ['y'], ['z']], ['x', 'y', 'z']),
        ([['1', '2'], ['3', '4']], ['1', '2', '3', '4']),
        ([['hello'], ['world']], ['hello', 'world']),
    ])
    def test_flat_generator_parametrized(self, input_data, expected):
        """Параметризованный тест для flat_generator"""
        result = list(flat_generator(input_data))
        assert result == expected


# --- Тесты для sum_numbers и multiply_numbers ---
class TestMathFunctions:
    """Тесты для математических функций"""
    
    def test_sum_numbers_positive(self):
        """Тест: сложение положительных чисел"""
        assert sum_numbers(2, 3) == 5
        assert sum_numbers(10, 5) == 15
        assert sum_numbers(0, 0) == 0
    
    def test_sum_numbers_negative(self):
        """Тест: сложение отрицательных чисел"""
        assert sum_numbers(-2, -3) == -5
        assert sum_numbers(-5, 3) == -2
    
    def test_multiply_numbers_positive(self):
        """Тест: умножение положительных чисел"""
        assert multiply_numbers(2, 3) == 6
        assert multiply_numbers(10, 5) == 50
        assert multiply_numbers(1, 100) == 100
    
    def test_multiply_numbers_zero(self):
        """Тест: умножение на ноль"""
        assert multiply_numbers(5, 0) == 0
        assert multiply_numbers(0, 0) == 0
    
    @pytest.mark.parametrize("a, b, expected_sum, expected_mult", [
        (2, 3, 5, 6),
        (-1, 5, 4, -5),
        (0, 7, 7, 0),
        (-2, -3, -5, 6),
    ])
    def test_math_parametrized(self, a, b, expected_sum, expected_mult):
        """Параметризованный тест для математических функций"""
        assert sum_numbers(a, b) == expected_sum
        assert multiply_numbers(a, b) == expected_mult


# --- Тесты для normalize_phone ---
class TestNormalizePhone:
    """Тесты для нормализации телефонных номеров"""
    
    def test_normalize_phone_standard(self):
        """Тест: стандартные номера"""
        assert normalize_phone("8-495-987-65-43") == "+7(495)987-65-43"
        assert normalize_phone("8(999)987-65-43") == "+7(999)987-65-43"
        assert normalize_phone("+7 999 123 45 67") == "+7(999)123-45-67"
    
    def test_normalize_phone_with_ext(self):
        """Тест: номера с добавочным"""
        result = normalize_phone("+7(999)123-45-67 доб.1234")
        assert result == "+7(999)123-45-67 доб.1234"
    
    def test_normalize_phone_empty(self):
        """Тест: пустой номер"""
        assert normalize_phone("") == ""
        assert normalize_phone(None) == ""
    
    @pytest.mark.parametrize("input_phone, expected", [
        ("8-495-123-45-67", "+7(495)123-45-67"),
        ("8(495)1234567", "+7(495)123-45-67"),
        ("+7 495 123 45 67", "+7(495)123-45-67"),
        ("84951234567", "+7(495)123-45-67"),
    ])
    def test_normalize_phone_parametrized(self, input_phone, expected):
        """Параметризованный тест для normalize_phone"""
        assert normalize_phone(input_phone) == expected


# ============================================================
# ЗАПУСК ТЕСТОВ
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])