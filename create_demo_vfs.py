# create_demo_vfs.py (упрощенная версия для ТЗ)
import zipfile
import base64

with zipfile.ZipFile('final_demo.zip', 'w') as zf:
    # Просто 3 файла в корне (минимум по ТЗ)
    zf.writestr('file1.txt', base64.b64encode(b'File 1 content').decode())
    zf.writestr('file2.txt', base64.b64encode(b'File 2 content').decode())
    zf.writestr('file3.txt', base64.b64encode(b'File 3 content').decode())

    # Один файл с путем для демонстрации иерархии
    zf.writestr('folder/file4.txt', base64.b64encode(b'Nested file').decode())

print("Создан final_demo.zip")