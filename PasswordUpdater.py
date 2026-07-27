import configparser
import datetime
import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FindReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Find & Replace Tool")
        self.root.geometry("620x520")
        self.root.resizable(False, False)

        # Config Setup
        self.config_path = Path("config.ini")
        self.log_file_path = self.init_config()

        # Variables
        self.folder_path = tk.StringVar()
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.file_extension = tk.StringVar(value="*.*")

        # Build UI
        self._create_widgets()

    def init_config(self) -> Path:
        """Reads config.ini or creates default configuration if missing."""
        config = configparser.ConfigParser()

        if not self.config_path.exists():
            config["LOGGING"] = {
                "log_file_path": "find_replace_activity.log"
            }
            with open(self.config_path, "w", encoding="utf-8") as configfile:
                config.write(configfile)

        config.read(self.config_path, encoding="utf-8")

        # Extract log path with fallback
        log_path_str = config.get("LOGGING", "log_file_path", fallback="find_replace_activity.log")
        return Path(log_path_str).resolve()

    def _create_widgets(self):
        # Config Info Display
        config_frame = tk.LabelFrame(self.root, text=" System Config ", font=("Segoe UI", 8, "italic"))
        config_frame.place(x=20, y=10, width=580, height=45)
        
        log_path_label = tk.Label(
            config_frame, 
            text=f"Log File Location: {self.log_file_path}", 
            font=("Segoe UI", 8),
            fg="#555555",
            anchor="w"
        )
        log_path_label.place(x=10, y=2, width=550)

        # Folder Selection
        tk.Label(self.root, text="Target Directory:", font=("Segoe UI", 9, "bold")).place(x=20, y=65)
        tk.Entry(self.root, textvariable=self.folder_path, width=60).place(x=20, y=90)
        tk.Button(self.root, text="Browse...", command=self.browse_folder, width=12).place(x=500, y=88)

        # File Filter
        tk.Label(self.root, text="File Extension Filter (e.g., *.txt, *.config, or *.*):", font=("Segoe UI", 9)).place(x=20, y=125)
        tk.Entry(self.root, textvariable=self.file_extension, width=22).place(x=20, y=150)

        # Find Input
        tk.Label(self.root, text="Find String / UserID / Password:", font=("Segoe UI", 9, "bold")).place(x=20, y=185)
        tk.Entry(self.root, textvariable=self.find_text, width=70).place(x=20, y=210)

        # Replace Input
        tk.Label(self.root, text="Replace With:", font=("Segoe UI", 9, "bold")).place(x=20, y=245)
        tk.Entry(self.root, textvariable=self.replace_text, width=70).place(x=20, y=270)

        # Action Button
        replace_btn = tk.Button(
            self.root, 
            text="Run Find & Replace", 
            command=self.run_replace, 
            bg="#0078D4", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        replace_btn.place(x=20, y=310, width=580)

        # UI Execution Log Window
        tk.Label(self.root, text="Activity Log (UI View):", font=("Segoe UI", 9)).place(x=20, y=370)
        self.log_area = tk.Text(self.root, height=7, width=71, state="disabled", font=("Consolas", 8))
        self.log_area.place(x=20, y=395)

    def browse_folder(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.folder_path.set(selected_dir)

    def log(self, message: str, write_to_file: bool = True):
        """Displays messages in GUI and writes formatted logs to file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Write to GUI Log
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, formatted_message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

        # Write to Log File configured in config.ini
        if write_to_file:
            try:
                # Ensure target log parent directory exists
                self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(formatted_message + "\n")
            except Exception as e:
                print(f"Failed to write log file: {e}", file=sys.stderr)

    def run_replace(self):
        folder = self.folder_path.get().strip()
        find_str = self.find_text.get()
        replace_str = self.replace_text.get()
        pattern = self.file_extension.get().strip().lower()

        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        if not find_str:
            messagebox.showerror("Error", "Please enter a search string.")
            return

        confirm = messagebox.askyesno(
            "Confirm Replace", 
            f"Are you sure you want to replace occurrences of:\n'{find_str}' -> '{replace_str}'\n\nin folder: {folder}?"
        )
        if not confirm:
            return

        # Clear UI Log view
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

        self.log("=" * 60)
        self.log(f"STARTING PROCESS: Folder='{folder}' | Find='{find_str}' | Replace='{replace_str}'")

        modified_count = 0
        total_occurrences = 0

        # Process Files
        for root_dir, _, files in os.walk(folder):
            for file in files:
                # Extension Filter Check
                if pattern != "*.*" and not file.lower().endswith(pattern.replace("*", "")):
                    continue

                file_path = os.path.join(root_dir, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    count = content.count(find_str)
                    if count > 0:
                        new_content = content.replace(find_str, replace_str)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)

                        modified_count += 1
                        total_occurrences += count
                        self.log(f"SUCCESS: Updated '{file_path}' ({count} replacement{'s' if count > 1 else ''})")

                except Exception as e:
                    self.log(f"ERROR: Skipped '{file_path}' - {e}")

        summary = f"COMPLETED: Updated {modified_count} file(s) with {total_occurrences} total replacement(s)."
        self.log(summary)
        self.log("=" * 60)
        
        messagebox.showinfo("Complete", f"{summary}\n\nLog saved to:\n{self.log_file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FindReplaceApp(root)
    root.mainloop()