import os
import tarfile
import sys
import tkinter as tk
from tkinter import scrolledtext
import csv


class ShellEmulator:
    def __init__(self, username, fs_path, init_script):
        self.username = username
        self.cwd = "/tmp/virtual_fs"  # Set initial directory
        self.fs_path = fs_path
        self.init_script = init_script
        self.check_or_create_filesystem()
        self.run_script(init_script)

    def check_or_create_filesystem(self):
        """Checks if the filesystem exists; creates it if not."""
        if not os.path.exists(self.fs_path):
            print(f"File system not found. Creating {self.fs_path}...")
            self.create_filesystem()
        else:
            self.load_filesystem()

    def create_filesystem(self):
        """Creates a virtual filesystem and saves it to a tar file."""
        os.makedirs("/tmp/virtual_fs/some_directory", exist_ok=True)
        os.makedirs("/tmp/virtual_fs/another_directory", exist_ok=True)

        with open("/tmp/virtual_fs/some_directory/some_file.txt", "w") as f:
            f.write("This is a test file.")

        with open("/tmp/virtual_fs/some_directory/another_file.txt", "w") as f:
            f.write("This is another test file.")

        with open("/tmp/virtual_fs/another_directory/file_in_another_directory.txt", "w") as f:
            f.write("This is a file in another directory.")

        with tarfile.open(self.fs_path, "w") as tar:
            tar.add("/tmp/virtual_fs", arcname="virtual_fs")

        print(f"File system successfully created and saved to {self.fs_path}")

    def load_filesystem(self):
        """Loads the virtual filesystem from a tar file."""
        print(f"Loading file system from {self.fs_path}")
        with tarfile.open(self.fs_path, "r") as tar:
            tar.extractall("/tmp")
        print(f"File system loaded from {self.fs_path}")

    def run_script(self, script_path):
        """Runs the initial script."""
        if not os.path.exists(script_path):
            print(f"Initial script {script_path} not found. Skipping execution.")
            return

        with open(script_path, 'r') as f:
            commands = f.readlines()
        for command in commands:
            command = command.strip()
            if command.startswith("#") or not command:
                continue
            print(f"Executing command: {command}")
            self.run_command(command)

    def run_command(self, command):
        """Executes commands."""
        if command.startswith("ls"):
            return self.ls()
        elif command.startswith("cd"):
            return self.cd(command.split()[1])
        elif command.startswith("find"):
            return self.find(command.split()[1])
        elif command.startswith("chown"):
            parts = command.split()
            return self.chown(parts[1], parts[2]) if len(parts) == 3 else "Error: 'chown' requires <owner> <path>"
        elif command.startswith("exit"):
            sys.exit()
        else:
            return f"Command '{command}' not supported in emulator."

    def ls(self):
        """Implementation of the ls command."""
        return "\n".join(os.listdir(self.cwd))

    def cd(self, path):
        """Implementation of the cd command."""
        new_path = os.path.join(self.cwd, path)
        if os.path.exists(new_path):
            self.cwd = new_path
            return f"Changed directory to {self.cwd}"
        else:
            return f"Path {new_path} not found"

    def find(self, filename):
        """Searches for a file within the current directory and subdirectories."""
        matches = []
        for root, dirs, files in os.walk(self.cwd):
            if filename in files or filename in dirs:
                matches.append(os.path.join(root, filename))
        return "\n".join(matches) if matches else f"'{filename}' not found"

    def chown(self, owner, path):
        """Changes the ownership of a file."""
        target_path = os.path.join(self.cwd, path)
        if os.path.exists(target_path):
            # Just a simulation: add an "owner" attribute (in a real FS, this would require permissions)
            # Assuming ownership is saved in a simple dictionary for demonstration purposes
            return f"Ownership of '{target_path}' changed to '{owner}'"
        else:
            return f"Path {target_path} not found"


class GUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = tk.Tk()
        self.window.title("Shell Emulator")

        self.output_area = scrolledtext.ScrolledText(self.window, width=80, height=20)
        self.output_area.pack()

        self.input_area = tk.Entry(self.window, width=80)
        self.input_area.pack()
        self.input_area.bind("<Return>", self.process_command)

        self.output_area.insert(tk.END, f"{self.emulator.username}@emulator:~$ ")
        self.output_area.see(tk.END)

    def process_command(self, event):
        command = self.input_area.get()
        self.input_area.delete(0, tk.END)
        if command.strip():
            output = self.emulator.run_command(command)
            self.output_area.insert(tk.END, f"{command}\n{output}\n")
            self.output_area.insert(tk.END, f"{self.emulator.username}@emulator:~$ ")
            self.output_area.see(tk.END)

    def run(self):
        self.window.mainloop()


def main():
    # Read configuration from CSV
    with open('config.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emulator = ShellEmulator(row['username'], row['virtual_fs'], row['initial_script'])
            gui = GUI(emulator)
            gui.run()


if __name__ == "__main__":
    main()
