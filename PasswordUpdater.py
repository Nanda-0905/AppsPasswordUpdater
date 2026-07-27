import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FindReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Find & Replace Tool")
        self.root.geometry("600x480")
        self.root.resizable(False, False)

        # Variables
        self.folder_path = tk.StringVar()
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.file_extension = tk.StringVar(value="*.*")

        # Build UI
        self._create_widgets()

    def _create_widgets(self):
        # Folder Selection
        tk.Label(self.root, text="Target Directory:", font=("Segoe UI", 9, "bold")).place(x=20, y=20)
        tk.Entry(self.root, textvariable=self.folder_path, width=58).place(x=20, y=45)
        tk.Button(self.root, text="Browse...", command=self.browse_folder, width=12).place(x=480, y=43)

        # File Filter
        tk.Label(self.root, text="File Pattern (e.g., *.txt, *.py, or *.*):", font=("Segoe UI", 9)).place(x=20, y=85)
        tk.Entry(self.root, textvariable=self.file_extension, width=20).place(x=20, y=110)

        # Find Input
        tk.Label(self.root, text="Find String:", font=("Segoe UI", 9, "bold")).place(x=20, y=150)
        tk.Entry(self.root, textvariable=self.find_text, width=68).place(x=20, y=175)

        # Replace Input
        tk.Label(self.root, text="Replace With:", font=("Segoe UI", 9, "bold")).place(x=20, y=215)
        tk.Entry(self.root, textvariable=self.replace_text, width=68).place(x=20, y=240)

        # Action Button
        replace_btn = tk.Button(
            self.root, 
            text="Find & Replace", 
            command=self.run_replace, 
            bg="#0078D4", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        replace_btn.place(x=20, y=285, width=552)

        # Log Window
        tk.Label(self.root, text="Execution Log:", font=("Segoe UI", 9)).place(x=20, y=350)
        self.log_area = tk.Text(self.root, height=5, width=68, state="disabled", font=("Consolas", 8))
        self.log_area.place(x=20, y=375)

    def browse_folder(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.folder_path.set(selected_dir)

    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def run_replace(self):
        folder = self.folder_path.get().strip()
        find_str = self.find_text.get()
        replace_str = self.replace_text.get()
        pattern = self.file_extension.get().strip().lower()

        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        if not find_str:
            messagebox.showerror("Error", "Please enter a string to find.")
            return

        confirm = messagebox.askyesno(
            "Confirm Replace", 
            f"Are you sure you want to replace all occurrences of:\n'{find_str}' -> '{replace_str}'\n\nin folder: {folder}?"
        )
        if not confirm:
            return

        # Reset Log
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

        modified_count = 0
        total_occurrences = 0

        # Process Files
        for root_dir, _, files in os.walk(folder):
            for file in files:
                # Basic pattern matching for extension
                if pattern != "*.*" and not file.lower().endswith(pattern.replace("*", "")):
                    continue

                file_path = os.path.join(root_dir, file)

                try:
                    # Read using UTF-8 encoding (ignores unreadable binary chunks safely)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    count = content.count(find_str)
                    if count > 0:
                        new_content = content.replace(find_str, replace_str)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        modified_count += 1
                        total_occurrences += count
                        self.log(f"Updated: {file} ({count} replacement{'s' if count > 1 else ''})")

                except Exception as e:
                    self.log(f"Skipped/Error on {file}: {e}")

        summary = f"Finished! Updated {modified_count} file(s) with {total_occurrences} total replacement(s)."
        self.log("-" * 50)
        self.log(summary)
        messagebox.showinfo("Complete", summary)


if __name__ == "__main__":
    root = tk.Tk()
    app = FindReplaceApp(root)
    root.mainloop()