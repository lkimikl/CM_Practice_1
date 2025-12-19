# -*- coding: utf-8 -*-
"""
Эмулятор командной строки ОС с VFS (Вариант 9)
Этапы 1-5
"""

import os
import sys
import json
import zipfile
import base64
import csv
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import hashlib

# ==================== VFS ====================
class VFSNode:
    def __init__(self, name, is_dir=True, content=None):
        self.name = name
        self.is_dir = is_dir
        self.content = content if content else b''
        self.children = {} if is_dir else None
        self.parent = None

class VFS:
    def __init__(self, name="default_vfs"):
        self.name = name
        self.root = VFSNode("/", is_dir=True)
        self.current = self.root
        self.default_vfs = None

    def get_path(self, node=None):
        if node is None:
            node = self.current
        path = []
        while node.parent:
            path.append(node.name)
            node = node.parent
        path.append("")
        return "/".join(reversed(path))

    def find_node(self, path):
        if path.startswith("/"):
            node = self.root
            parts = path.strip("/").split("/")
        else:
            node = self.current
            parts = path.split("/")
        for p in parts:
            if not p or p == ".":
                continue
            if p == "..":
                if node.parent:
                    node = node.parent
                continue
            if node.is_dir and p in node.children:
                node = node.children[p]
            else:
                return None
        return node

    def mkdir(self, path):
        parent = self.find_node(os.path.dirname(path))
        name = os.path.basename(path)
        if parent and parent.is_dir and name not in parent.children:
            new_node = VFSNode(name, is_dir=True)
            new_node.parent = parent
            parent.children[name] = new_node
            return True
        return False

    def touch(self, path, content=b""):
        parent = self.find_node(os.path.dirname(path))
        name = os.path.basename(path)
        if parent and parent.is_dir and name not in parent.children:
            new_node = VFSNode(name, is_dir=False, content=content)
            new_node.parent = parent
            parent.children[name] = new_node
            return True
        return False

    def listdir(self, node=None):
        if node is None:
            node = self.current
        if node.is_dir:
            return list(node.children.keys())
        return []

    def save_to_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'w') as zf:
            self._save_node(self.root, "", zf)

    def _save_node(self, node, path, zf):
        if node.is_dir:
            for child in node.children.values():
                self._save_node(child, f"{path}/{node.name}", zf)
        else:
            arcname = f"{path}/{node.name}".lstrip("/")
            zf.writestr(arcname, base64.b64encode(node.content).decode())

    @classmethod
    def load_from_zip(cls, zip_path, vfs_name=None):
        vfs = cls(vfs_name or os.path.basename(zip_path))

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for filename in zf.namelist():
                if filename.endswith('/'):
                    continue  # пропускаем директории

                # Простая логика: все файлы в корень VFS
                file_name = os.path.basename(filename)
                try:
                    content = base64.b64decode(zf.read(filename))
                except:
                    content = zf.read(filename)  # fallback

                vfs.touch(file_name, content)

        return vfs

    def create_default(self):
        self.root = VFSNode("/", is_dir=True)
        self.current = self.root
        self.touch("/file1.txt", b"Hello")
        self.touch("/file2.txt", b"World")
        self.mkdir("/dir1")
        self.touch("/dir1/file3.txt", b"Test")
        self.mkdir("/dir1/subdir")
        self.touch("/dir1/subdir/file4.txt", b"Deep")

# ==================== REPL GUI ====================
class ShellEmulator:
    def __init__(self, vfs_path=None, script_path=None, log_path=None):
        self.vfs = VFS()
        self.script_path = script_path
        self.log_path = log_path
        self.history = []
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'du': self.cmd_du,
            'history': self.cmd_history,
            'cal': self.cmd_cal,
            'touch': self.cmd_touch,
            'mkdir': self.cmd_mkdir,
            'vfs-load': self.cmd_vfs_load,
            'vfs-save': self.cmd_vfs_save,
            'vfs-info': self.cmd_vfs_info,
            'help': self.cmd_help,
        }
        self.setup_gui()
        self.load_vfs(vfs_path)
        self.run_script()

    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title(f"VFS: {self.vfs.name}")
        self.window.geometry("800x600")

        self.output_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, state='disabled')
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_label = tk.Label(self.input_frame, text=f"{self.vfs.name}$ ")
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.process_input)
        self.input_entry.focus()

        self.window.protocol("WM_DELETE_WINDOW", self.cmd_exit)

    def print_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def process_input(self, event=None):
        line = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        if line:
            self.print_output(f"{self.vfs.name}$ {line}")
            self.execute_command(line)

    def execute_command(self, line):
        parts = self.parse_line(line)
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        # ДОБАВЛЯЕМ КОМАНДУ В ИСТОРИЮ ПЕРЕД ВЫПОЛНЕНИЕМ
        self.history.append(line)

        self.log_command(cmd, args)
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self.print_output(f"Ошибка: {e}")
        else:
            self.print_output(f"Неизвестная команда: {cmd}")

    def parse_line(self, line):
        parts = []
        in_quotes = False
        current = []
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == ' ' and not in_quotes:
                if current:
                    parts.append(''.join(current))
                    current = []
            else:
                current.append(ch)
        if current:
            parts.append(''.join(current))
        return parts

    def log_command(self, cmd, args):
        if not self.log_path:
            return
        try:
            with open(self.log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), cmd, ' '.join(args), ''])
        except:
            pass

    # ==================== Команды ====================
    def cmd_ls(self, args):
        path = args[0] if args else "."
        node = self.vfs.find_node(path)
        if node is None:
            self.print_output(f"ls: {path}: Нет такого файла или каталога")
        elif node.is_dir:
            files = self.vfs.listdir(node)
            self.print_output("  ".join(files))
        else:
            self.print_output(node.name)

    def cmd_cd(self, args):
        if not args:
            target = "/"
        else:
            target = args[0]
        node = self.vfs.find_node(target)
        if node is None:
            self.print_output(f"cd: {target}: Нет такого файла или каталога")
        elif not node.is_dir:
            self.print_output(f"cd: {target}: Не каталог")
        else:
            self.vfs.current = node
            self.prompt_label.config(text=f"{self.vfs.name}$ ")

    def cmd_du(self, args):
        def size_node(node):
            if not node.is_dir:
                return len(node.content)
            total = 0
            for child in node.children.values():
                total += size_node(child)
            return total
        path = args[0] if args else "."
        node = self.vfs.find_node(path)
        if node:
            self.print_output(f"{size_node(node)} байт")

    def cmd_history(self, args):
        if not self.history:
            self.print_output("История команд пуста")
            return

        self.print_output("=== История команд ===")
        # Показываем последние 10 команд или меньше, если их меньше
        start_index = max(0, len(self.history) - 10)
        for i, cmd in enumerate(self.history[start_index:], start_index + 1):
            self.print_output(f"{i}: {cmd}")
        self.print_output("=====================")

    def cmd_cal(self, args):
        import calendar
        now = datetime.now()
        cal_text = calendar.month(now.year, now.month)
        self.print_output(cal_text)

    def cmd_touch(self, args):
        if not args:
            self.print_output("touch: требуется аргумент")
            return
        for f in args:
            if self.vfs.touch(f):
                self.print_output(f"Создан файл {f}")
            else:
                self.print_output(f"Ошибка создания файла {f}")

    def cmd_mkdir(self, args):
        if not args:
            self.print_output("mkdir: требуется аргумент")
            return
        for d in args:
            if self.vfs.mkdir(d):
                self.print_output(f"Создан каталог {d}")
            else:
                self.print_output(f"Ошибка создания каталога {d}")

    def cmd_vfs_load(self, args):
        if not args:
            self.print_output("vfs-load: требуется путь")
            return
        path = args[0]
        if not os.path.exists(path):
            self.print_output(f"Файл не найден: {path}")
            return
        try:
            self.vfs = VFS.load_from_zip(path, os.path.basename(path))
            self.window.title(f"VFS: {self.vfs.name}")
            self.prompt_label.config(text=f"{self.vfs.name}$ ")
            self.print_output(f"Загружена VFS: {self.vfs.name}")
        except:
            self.print_output("Ошибка загрузки VFS")

    def cmd_vfs_save(self, args):
        if not args:
            self.print_output("vfs-save: требуется путь")
            return
        try:
            self.vfs.save_to_zip(args[0])
            self.print_output(f"VFS сохранена в {args[0]}")
        except:
            self.print_output("Ошибка сохранения VFS")

    def cmd_vfs_info(self, args):
        self.print_output(f"Имя VFS: {self.vfs.name}")

    def cmd_help(self, args):
        help_text = """
        ls [путь]          - список файлов
        cd [путь]          - сменить каталог
        du [путь]          - размер файлов
        history            - история команд
        cal                - календарь
        touch <файл>       - создать файл
        mkdir <каталог>    - создать каталог
        vfs-load <путь>    - загрузить VFS
        vfs-save <путь>    - сохранить VFS
        vfs-info           - информация о VFS
        help               - справка
        exit               - выход
        """
        self.print_output(help_text)

    def cmd_exit(self, args=None):
        self.window.quit()

    # ==================== Загрузка VFS ====================
    def load_vfs(self, vfs_path):
        if vfs_path and os.path.exists(vfs_path):
            try:
                self.vfs = VFS.load_from_zip(vfs_path, os.path.basename(vfs_path))
                self.window.title(f"VFS: {self.vfs.name}")
                self.prompt_label.config(text=f"{self.vfs.name}$ ")
                self.print_output(f"Загружена VFS из {vfs_path}")
            except:
                self.print_output("Ошибка загрузки VFS, создана VFS по умолчанию")
                self.vfs.create_default()
        else:
            self.vfs.create_default()
            self.print_output("Создана VFS по умолчанию в памяти")

    # ==================== Скрипт ====================
    def run_script(self):
        if not self.script_path or not os.path.exists(self.script_path):
            return
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                self.print_output(f"{self.vfs.name}$ {line}")
                self.execute_command(line)
                if "Ошибка" in self.output_area.get("end-2l", "end-1l"):
                    self.print_output("Скрипт остановлен из-за ошибки")
                    break
        except Exception as e:
            self.print_output(f"Ошибка выполнения скрипта: {e}")

    def run(self):
        self.window.mainloop()

# ==================== Точка входа ====================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Эмулятор командной строки с VFS")
    parser.add_argument("--vfs", type=str, help="Путь к VFS (ZIP-архив)")
    parser.add_argument("--script", type=str, help="Путь к стартовому скрипту")
    parser.add_argument("--log", type=str, help="Путь к лог-файлу (CSV)")
    args = parser.parse_args()

    emulator = ShellEmulator(vfs_path=args.vfs, script_path=args.script, log_path=args.log)
    emulator.run()