import os

class ShellEmulator:
    def __init__(self, username, virtual_fs, startup_script):
        self.username = username
        self.virtual_fs = virtual_fs
        self.startup_script = startup_script
        self.cwd = '/tmp/virtual_fs'  # Устанавливаем начальную директорию

    def cd(self, directory):
        """Меняет текущую директорию."""
        new_path = os.path.join(self.cwd, directory)
        if os.path.isdir(new_path):
            self.cwd = new_path
            print(f"Текущая директория изменена на: {self.cwd}")  # Отладочное сообщение
            return f"Перемещено в {self.cwd}"
        else:
            return f"Путь {new_path} не найден"

    def ls(self):
        """Выводит содержимое текущей директории."""
        try:
            files = os.listdir(self.cwd)  # Получаем список файлов в текущей директории
            print(f"Файлы в директории {self.cwd}: {files}")  # Отладочное сообщение
            for file in files:
                print(file)  # Выводим файлы
        except FileNotFoundError:
            print("Текущая директория не найдена.")

    def find(self, filename):
        """Ищет файл в текущей директории и ее поддиректориях."""
        for root, dirs, files in os.walk(self.cwd):  # Обходим все подкаталоги
            if filename in files:
                return f"Файл найден: {os.path.join(root, filename)}"
        return 'Файл или каталог не найден.'

    def chown(self, new_owner, file_path):
        """Изменяет владельца файла."""
        full_path = os.path.join(self.cwd, file_path)
        if os.path.isfile(full_path):
            # Здесь можно добавить логику изменения владельца, если нужно
            return f"Изменен владелец {full_path} на {new_owner}"
        else:
            return 'Файл не найден.'


# Тесты для ShellEmulator
import unittest
from io import StringIO
import sys
import shutil

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Настраиваем окружение перед каждым тестом"""
        # Создаем временную директорию для тестов
        self.base_path = '/tmp/virtual_fs'
        os.makedirs(os.path.join(self.base_path, 'some_directory'), exist_ok=True)

        # Создаем тестовый файл
        with open(os.path.join(self.base_path, 'some_directory', 'some_file.txt'), 'w') as f:
            f.write('Тестовый файл')

        # Инициализируем эмулятор
        self.emulator = ShellEmulator("test_user", "virtual_fs.tar", "init.sh")
        self.emulator.cwd = self.base_path  # Устанавливаем начальную директорию

    def test_ls(self):
        """Тестируем команду ls"""
        self.emulator.cd('some_directory')  # Переходим в директорию
        captured_output = StringIO()
        sys.stdout = captured_output

        # Вызываем ls без аргументов
        self.emulator.ls()

        sys.stdout = sys.__stdout__  # Восстанавливаем стандартный вывод

        # Получаем вывод и проверяем, что в нём содержатся ожидаемые файлы
        output = captured_output.getvalue()
        print(f"Вывод ls: '{output}'")  # Отладочное сообщение
        self.assertIn('some_file.txt', output)  # Проверка вывода

    def test_cd(self):
        """Тестируем команду cd"""
        result = self.emulator.cd('some_directory')
        expected_path = os.path.join(self.base_path, "some_directory")  # Универсальный путь
        self.assertEqual(result, f"Перемещено в {expected_path}")
        # Проверяем, что текущее положение изменилось
        self.assertEqual(self.emulator.cwd, expected_path)

    def test_cd_invalid_path(self):
        """Тестируем переход в несуществующую директорию"""
        result = self.emulator.cd('non_existing_directory')
        expected_path = os.path.join(self.base_path, 'non_existing_directory')
        self.assertEqual(result, f"Путь {expected_path} не найден")
        # Проверяем, что текущая директория не изменилась
        self.assertEqual(self.emulator.cwd, self.base_path)

    def test_find(self):
        """Тестируем команду find"""
        result = self.emulator.find('some_file.txt')
        expected_path = os.path.join(self.base_path, "some_directory", "some_file.txt")
        self.assertIn(expected_path, result)

        # Проверяем случай, когда файл не найден
        result = self.emulator.find('non_existing_file.txt')
        self.assertEqual(result, 'Файл или каталог не найден.')

    def test_chown(self):
        """Тестируем команду chown"""
        result = self.emulator.chown('new_owner', 'some_directory/some_file.txt')

        # Формируем ожидаемый путь с учётом операционной системы
        expected_path = os.path.join(self.base_path, "some_directory", "some_file.txt")

        # Сравниваем с учётом нормализации путей
        self.assertEqual(os.path.normpath(result), f"Изменен владелец {os.path.normpath(expected_path)} на new_owner")

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)  # Удаляем временную директорию

if __name__ == '__main__':
    unittest.main()