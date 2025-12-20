# Эмулятор командной строки с VFS (Вариант 9)

## Описание
Эмулятор командной строки UNIX-подобной операционной системы с виртуальной файловой системой (VFS). Все операции производятся только в памяти. Проект реализован в рамках дисциплины "Конфигурационное управление"

## Функции
- Графический интерфейс (GUI) с заголовком VFS
- Парсер команд с поддержкой аргументов в кавычках
- Виртуальная файловая система в памяти
- Команды: ls, cd, du, history, cal, touch, mkdir, vfs-load, vfs-info, exit
- Логирование в CSV формате
- Выполнение стартовых скриптов
- Обработка ошибок выполнения

## Требования
- Python 3.7+
- Стандартные библиотеки Python

## Запуск
```bash
# 1. Без параметров (создаст VFS по умолчанию)
python emulator.py

# 2. С параметрами конфигурации
python emulator.py --vfs архив.zip --script скрипт.txt --log логи.csv

# 3. Помощь по параметрам
python emulator.py --help

Пример 1: Базовое использование
> python emulator.py

Создана VFS по умолчанию в памяти
default_vfs$ ls /
file1.txt  file2.txt  dir1
default_vfs$ cd /dir1
default_vfs$ ls
file3.txt  subdir
default_vfs$ cd /
default_vfs$ history
=== История команд ===
1: ls /
2: cd /dir1
3: ls
4: cd /
5: history
=====================
default_vfs$ cal
   December 2025
Mo Tu We Th Fr Sa Su
 1  2  3  4  5  6  7
 8  9 10 11 12 13 14
15 16 17 18 19 20 21
22 23 24 25 26 27 28
29 30 31

Пример 2: Создание файлов и каталогов
> python emulator.py

default_vfs$ mkdir /projects
Создан каталог /projects
default_vfs$ mkdir /projects/src
Создан каталог /projects/src
default_vfs$ touch /projects/readme.txt
Создан файл /projects/readme.txt
default_vfs$ touch /projects/src/main.py
Создан файл /projects/src/main.py
default_vfs$ ls /projects
src  readme.txt
default_vfs$ du /projects
0 байт

Пример 3: Работа с VFS из ZIP-архива
> python emulator.py --vfs final_demo.zip

Загружена VFS из final_demo.zip
final_demo.zip$ ls /
file1.txt  file2.txt  file3.txt
final_demo.zip$ vfs-info
Имя VFS: final_demo.zip
final_demo.zip$ vfs-load другой_архив.zip
Загружена VFS из другой_архив.zip

Пример 4: Тестирование с помощью batch-скрипта
> test_emulator.bat

============================================
Testing command line emulator with VFS
============================================

1. Test without parameters (default VFS)
[окно эмулятора открывается]

2. Test with script final_test.txt
[выполнение скрипта, создание test1.csv]

3. Test with VFS from ZIP archive
[загрузка VFS из final_demo.zip]

4. Test error handling
[скрипт останавливается на ошибке]

5. Test with logging only
[создание логов без скрипта]

Все тесты завершены. Проверьте созданные файлы:
[список созданных CSV файлов]