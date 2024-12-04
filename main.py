import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import re
import math
import sys

sys.set_int_max_str_digits(700) 

# Токен бота
API_TOKEN = "7508024571:AAHwQ-k8YhdZm2ZU-qjc4koXP21NImHdVr8"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот-калькулятор. Введи математическое выражение, и я посчитаю его.\n"
                         "Также я могу переводить числа между системами счисления. Пример: 10 из 10 в 2 (двоичную систему).\n"
                         "Для вычисления факториала можно использовать шаблон '3!' или 'факториал из 3'. "
                         "Я также могу вычислять числа в разных системах счисления. Пример: 10010_2.")

# Функция для обработки выражения
def process_math_expression(expression: str) -> str:
    # Заменяем ^ на ** для возведения в степень
    expression = expression.replace("^", "**")
    
    # Добавляем * между числом и скобкой, если они идут подряд
    expression = re.sub(r'(\d)(\()', r'\1*(', expression)

    # Обрабатываем факториалы: как числа перед "!", так и выражения в скобках, например (5 + 3)!
    expression = re.sub(r'(\([^\)]+\)|\d+)!', r'math.factorial(\1)', expression)

    # Обрабатываем числа в разных системах счисления, например, 10010_2 или 1A_16
    expression = re.sub(r'([0-9A-Fa-f]+)_([0-9]+)', lambda match: str(int(match.group(1), int(match.group(2)))), expression)
    
    return expression
    
    return expression

# Функция для перевода системы счисления
def convert_base(number: str, from_base: int, to_base: int) -> str:
    try:
        base10 = int(number, from_base)

        if to_base == 2:
            return bin(base10)[2:]
        elif to_base == 8:
            return oct(base10)[2:]
        elif to_base == 16:
            return hex(base10)[2:].upper()
        else:
            return str(base10)
    except ValueError:
        return "Ошибка при конвертации числа."

# Функция для проверки на допустимые символы (числа, операторы, скобки)
def is_valid_expression(expression: str) -> bool:
    return bool(re.match(r'^[\d+\-*/^().! _]+$', expression))

# Функция для проверки длины чисел в выражении
def check_number_length(expression: str, limit: int = 4300) -> bool:
    numbers = re.findall(r'\d+', expression)
    for number in numbers:
        if len(number) > limit:
            return False
    return True

@dp.message()
async def calculate(message: Message):
    expression = message.text.strip()

    # Проверка на системы счисления
    if " из " in expression and " в " in expression:
        try:
            parts = expression.split()
            number = parts[0]
            from_base = int(parts[2])
            to_base = int(parts[4])
            result = convert_base(number, from_base, to_base)
            await message.answer(f"Результат: {result}")
        except Exception:
            await message.answer("Неверный формат. Пример: 10 из 10 в 2")
    else:
        # Проверяем, выражение на только допустимые символы
        if not is_valid_expression(expression):
            await message.answer("Пожалуйста, вводите только числа и математические операторы.")
            return
        
        # Проверяем, что числа в выражении не слишком большие
        if not check_number_length(expression):
            await message.answer("Число слишком большое для обработки. Пожалуйста, вводите числа с меньшим количеством цифр.")
            return

        try:
            # Обработка математического выражения
            expression = process_math_expression(expression)
            result = eval(expression, {"__builtins__": None}, {"math": math})
            await message.answer(f"Результат: {result}")
        except Exception as e:
            await message.answer(f"Ошибка в выражении: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())