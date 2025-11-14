import tkinter as tk
from tkinter import scrolledtext, messagebox
import re
import sys
from datetime import datetime
import os
import argparse
import logging


class VFSEmulator:
    def __init__(self, vfs_path=None, log_file=None, startup_script=None):
        self.vfs_path = vfs_path or "/virtual/root"
        self.current_dir = self.vfs_path
        self.log_file = log_file
        self.startup_script = startup_script

        # Настройка логирования
        if self.log_file:
            self.setup_logging()

        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
        }

    def setup_logging(self):
        # Настройка логирования
        try:
            logging.basicConfig(
                filename=self.log_file,
                level=logging.INFO,
                format='%(asctime)s,%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        except Exception as e:
            print(f"Ошибка настройки логирования: {e}")

    def log_command(self, command, args, error_message=None):
        # Логирование команды
        if self.log_file:
            message = f"COMMAND:{command},ARGS:{args},ERROR:{error_message or 'None'}"
            logging.info(message)

    def parse_arguments(self, input_string):
        # Парсер аргументов
        # Выражение для разбора аргументов в кавычках
        pattern = r'''(".*?"|'.*?'|\S+)'''
        matches = re.findall(pattern, input_string)

        # Убираем кавычки вокруг аргументов
        parsed_args = []
        for match in matches:
            if (match.startswith('"') and match.endswith('"')) or \
                    (match.startswith("'") and match.endswith("'")):
                parsed_args.append(match[1:-1])
            else:
                parsed_args.append(match)

        return parsed_args

    def cmd_ls(self, args):
        # Проверка количества аргументов
        if len(args) > 1:
            error_msg = "ls: too many arguments"
            self.log_command('ls', args, error_msg)
            return f"Error: {error_msg}"

        # Проверка что внутри кавычек не несколько аргументов
        if len(args) == 1 and ' ' in args[0]:
            # Если в кавычках передано несколько "аргументов" через пробелы
            error_msg = "ls: too many arguments"
            self.log_command('ls', args, error_msg)
            return f"Error: {error_msg}"

        result = f"ls command called with arguments: {args}"
        self.log_command('ls', args)
        return result

    def cmd_cd(self, args):
        # Проверка количества аргументов
        if len(args) > 1:
            error_msg = "cd: too many arguments"
            self.log_command('cd', args, error_msg)
            return f"Error: {error_msg}"

        # Проверка что внутри кавычек не несколько аргументов
        if len(args) == 1 and ' ' in args[0]:
            # Если в кавычках передано несколько "аргументов" через пробелы
            error_msg = "cd: too many arguments"
            self.log_command('cd', args, error_msg)
            return f"Error: {error_msg}"

        if len(args) == 0:
            result = "cd: missing argument"
            self.log_command('cd', args, result)
            return f"Error: {result}"
        else:
            result = f"cd command called with arguments: {args}"

        self.log_command('cd', args)
        return result


    def cmd_exit(self, args):
        # Команда exit
        # Проверка количества аргументов
        if len(args) > 0:
            error_msg = "exit: too many arguments"
            self.log_command('exit', args, error_msg)
            return f"Error: {error_msg}"

        # Проверка что внутри кавычек не несколько аргументов
        if len(args) == 1 and ' ' in args[0]:
            # Если в кавычках передано несколько "аргументов" через пробелы
            error_msg = "exit: too many arguments"
            self.log_command('exit', args, error_msg)
            return f"Error: {error_msg}"

        self.log_command('exit', args)
        return "EXIT"

    def execute_command(self, command_input):
        # Выполнени команды
        if not command_input.strip():
            return ""

        try:
            # Разбираем команду и аргументы
            parts = self.parse_arguments(command_input)
            if not parts:
                return ""

            command = parts[0]
            args = parts[1:]

            # Выполняем команду
            if command in self.commands:
                result = self.commands[command](args)
                if result == "EXIT":
                    return "EXIT"
                return result
            else:
                error_msg = f"Command not found: {command}"
                self.log_command(command, args, error_msg)
                return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.log_command('unknown', command_input, error_msg)
            return f"Error: {error_msg}"


class VFSGUI:
    def __init__(self, vfs_emulator):
        self.vfs = vfs_emulator

        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title(f"VFS Emulator - {self.vfs.vfs_path}")
        self.root.geometry("800x600")

        # Создаем текстовое поле для вывода
        self.output_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg='black',
            fg='white',
            insertbackground='white'
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)

        # Создаем поле ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prompt_label = tk.Label(input_frame, text=f"{self.vfs.current_dir}$ ", fg='green')
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(input_frame, bg='black', fg='white', insertbackground='white')
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.input_entry.bind('<Return>', self.execute_command)
        self.input_entry.focus()

        # Кнопка выполнения
        self.execute_button = tk.Button(input_frame, text="Execute", command=self.execute_command)
        self.execute_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Приветственное сообщение
        self.print_output("VFS Emulator v1.0")
        self.print_output("Type 'exit' to quit\n")

        # Если указан стартовый скрипт, выполняем его
        if self.vfs.startup_script:
            self.root.after(100, self.execute_startup_script)

    def execute_startup_script(self):
        # Выполнение стартового скрипта
        try:
            with open(self.vfs.startup_script, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.print_output(f"Executing startup script: {self.vfs.startup_script}")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if line and not line.startswith('#'):
                    self.print_output(f"{self.vfs.current_dir}$ {line}")
                    result = self.vfs.execute_command(line)

                    if result and result != "EXIT":
                        self.print_output(result)

                    # Проверяем на ошибки
                    if result and result.startswith("Error:"):
                        self.print_output(f"Script stopped at line {line_num} due to error")
                        break

                    if result == "EXIT":
                        break

        except Exception as e:
            error_msg = f"Error executing startup script: {str(e)}"
            self.print_output(error_msg)
            messagebox.showerror("Script Error", error_msg)

    def update_prompt(self):
        # Обновление приглашения командной строки
        self.prompt_label.config(text=f"{self.vfs.current_dir}$ ")

    def print_output(self, text):
        # Вывод текста в текстовое поле
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + '\n')
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def execute_command(self, event=None):
        # Выполнение команды из поля ввода
        command = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)

        if not command:
            return

        # Выводим команду
        self.print_output(f"{self.vfs.current_dir}$ {command}")

        # Выполняем команду
        result = self.vfs.execute_command(command)

        # Обрабатываем результат
        if result and result != "EXIT":
            self.print_output(result)

        if result == "EXIT":
            self.root.quit()
            return

        # Обновляем приглашение
        self.update_prompt()

    def run(self):
        # Запуск GUI
        self.root.mainloop()


def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='VFS Emulator')
    parser.add_argument('--vfs-path', type=str, default='/virtual/root',
                        help='Path to VFS physical location')
    parser.add_argument('--log-file', type=str,
                        help='Path to log file (CSV format)')
    parser.add_argument('--startup-script', type=str,
                        help='Path to startup script')

    args = parser.parse_args()

    # Отладочный вывод параметров
    print("VFS Emulator starting with parameters:")
    print(f"  VFS Path: {args.vfs_path}")
    print(f"  Log File: {args.log_file}")
    print(f"  Startup Script: {args.startup_script}")

    # Создаем эмулятор VFS
    vfs = VFSEmulator(
        vfs_path=args.vfs_path,
        log_file=args.log_file,
        startup_script=args.startup_script
    )

    # Запускаем GUI
    gui = VFSGUI(vfs)
    gui.run()


if __name__ == "__main__":
    main()