import configparser
import csv
import datetime
import os
from pathlib import Path
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class FindReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Find & Replace Tool (Single & CSV Batch Mode)")
        self.root.geometry("680x680")
        self.root.resizable(False, False)

        # Config Setup
        self.config_path = Path("config.ini")
        self.log_file_path = self.init_config()

        # Input Variables
        self.mode = tk.StringVar(value="single")  # 'single' or 'csv'
        self.folder_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.file_extension = tk.StringVar(value="web.config")
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()

        # Build UI
        self._create_widgets()
        self._toggle_mode()

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
        log_path_str = config.get("LOGGING", "log_file_path", fallback="find_replace_activity.log")
        return Path(log_path_str).resolve()

    def _create_widgets(self):
        # 1. System Config Info Display
        config_frame = tk.LabelFrame(self.root, text=" System Configuration ", font=("Segoe UI", 8, "italic"))
        config_frame.place(x=20, y=10, width=640, height=45)
        
        log_path_label = tk.Label(
            config_frame, 
            text=f"Log File: {self.log_file_path}", 
            font=("Segoe UI", 8),
            fg="#555555",
            anchor="w"
        )
        log_path_label.place(x=10, y=2, width=610)

        # 2. Source Selection Mode
        mode_frame = tk.LabelFrame(self.root, text=" Execution Source Mode ", font=("Segoe UI", 9, "bold"))
        mode_frame.place(x=20, y=60, width=640, height=160)

        tk.Radiobutton(
            mode_frame, text="Single Target Directory", variable=self.mode, value="single", 
            command=self._toggle_mode, font=("Segoe UI", 9)
        ).place(x=15, y=5)

        tk.Radiobutton(
            mode_frame, text="Load Locations from CSV File", variable=self.mode, value="csv", 
            command=self._toggle_mode, font=("Segoe UI", 9)
        ).place(x=200, y=5)

        # Single Folder Row
        self.lbl_folder = tk.Label(mode_frame, text="Target Directory:", font=("Segoe UI", 8, "bold"))
        self.lbl_folder.place(x=15, y=35)
        self.ent_folder = tk.Entry(mode_frame, textvariable=self.folder_path, width=65)
        self.ent_folder.place(x=15, y=55)
        self.btn_folder = tk.Button(mode_frame, text="Browse...", command=self.browse_folder, width=12)
        self.btn_folder.place(x=525, y=53)

        # CSV File Row
        self.lbl_csv = tk.Label(mode_frame, text="Target CSV File:", font=("Segoe UI", 8, "bold"))
        self.lbl_csv.place(x=15, y=85)
        self.ent_csv = tk.Entry(mode_frame, textvariable=self.csv_path, width=65)
        self.ent_csv.place(x=15, y=105)
        self.btn_csv = tk.Button(mode_frame, text="Browse...", command=self.browse_csv, width=12)
        self.btn_csv.place(x=525, y=103)

        # 3. Target File Pattern / Extension Filter
        filter_frame = tk.Frame(self.root)
        filter_frame.place(x=20, y=225, width=640, height=35)
        tk.Label(filter_frame, text="Target Configuration File / Pattern (e.g. web.config, *.config, *.*):", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Entry(filter_frame, textvariable=self.file_extension, width=22).pack(side=tk.LEFT, padx=10)

        # 4. Replacement Inputs
        replace_frame = tk.LabelFrame(self.root, text=" Replacement Values ", font=("Segoe UI", 9, "bold"))
        replace_frame.place(x=20, y=265, width=640, height=125)

        tk.Label(replace_frame, text="Find String / UserID / Password:", font=("Segoe UI", 9)).place(x=15, y=5)
        tk.Entry(replace_frame, textvariable=self.find_text, width=76).place(x=15, y=25)

        tk.Label(replace_frame, text="Replace With:", font=("Segoe UI", 9)).place(x=15, y=55)
        tk.Entry(replace_frame, textvariable=self.replace_text, width=76).place(x=15, y=75)

        # 5. Action Button
        run_btn = tk.Button(
            self.root, 
            text="Run Find & Replace Process", 
            command=self.run_replace, 
            bg="#0078D4", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            height=2
        )
        run_btn.place(x=20, y=400, width=640)

        # 6. UI Execution Log View
        tk.Label(self.root, text="Activity Output Log:", font=("Segoe UI", 9, "bold")).place(x=20, y=460)
        self.log_area = tk.Text(self.root, height=11, width=89, state="disabled", font=("Consolas", 8))
        self.log_area.place(x=20, y=485)

    def _toggle_mode(self):
        """Enables or disables input controls based on selected radio button mode."""
        selected_mode = self.mode.get()
        if selected_mode == "single":
            self.ent_folder.config(state="normal")
            self.btn_folder.config(state="normal")
            self.ent_csv.config(state="disabled")
            self.btn_csv.config(state="disabled")
        else:
            self.ent_folder.config(state="disabled")
            self.btn_folder.config(state="disabled")
            self.ent_csv.config(state="normal")
            self.btn_csv.config(state="normal")

    def browse_folder(self):
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.folder_path.set(selected_dir)

    def browse_csv(self):
        selected_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if selected_file:
            self.csv_path.set(selected_file)

    def log(self, message: str, write_to_file: bool = True):
        """Displays messages in GUI and writes formatted logs to file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, formatted_message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

        if write_to_file:
            try:
                self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(formatted_message + "\n")
            except Exception as e:
                print(f"Failed to write log file: {e}", file=sys.stderr)

    def _process_file(self, file_path: Path, find_str: str, replace_str: str, timestamp: str) -> int:
        """Helper to create a .bak backup and update file content."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        count = content.count(find_str)
        if count > 0:
            # Create timestamped backup file
            backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")
            shutil.copy2(file_path, backup_path)
            
            # Commit changes
            new_content = content.replace(find_str, replace_str)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        return count

    def run_replace(self):
        mode = self.mode.get()
        find_str = self.find_text.get()
        replace_str = self.replace_text.get()
        target_pattern = self.file_extension.get().strip().lower()

        if not find_str:
            messagebox.showerror("Error", "Please enter a search string.")
            return

        # Confirm Execution
        if not messagebox.askyesno("Confirm Replace", f"Are you sure you want to run Find & Replace for:\n'{find_str}' -> '{replace_str}'?"):
            return

        # Clear UI Log
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log("=" * 70)
        self.log(f"EXECUTION STARTED [Mode: {mode.upper()}] | Find: '{find_str}' | Replace: '{replace_str}'")

        if mode == "single":
            folder = self.folder_path.get().strip()
            if not folder or not os.path.exists(folder):
                messagebox.showerror("Error", "Please select a valid directory.")
                return

            modified_count, total_occurrences = self.process_single_directory(folder, target_pattern, find_str, replace_str, timestamp)
            summary = f"COMPLETED: Updated {modified_count} file(s) with {total_occurrences} replacement(s)."

        else:
            csv_file = self.csv_path.get().strip()
            if not csv_file or not os.path.exists(csv_file):
                messagebox.showerror("Error", "Please select a valid CSV file.")
                return

            summary = self.process_csv_batch(csv_file, find_str, replace_str, timestamp)

        self.log(summary)
        self.log("=" * 70)
        messagebox.showinfo("Complete", f"{summary}\n\nDetailed logs saved to:\n{self.log_file_path}")

    def process_single_directory(self, folder: str, pattern: str, find_str: str, replace_str: str, timestamp: str):
        """Processes a single target directory recursively."""
        modified_count = 0
        total_occurrences = 0

        for root_dir, _, files in os.walk(folder):
            for file in files:
                if pattern != "*.*" and not file.lower().endswith(pattern.replace("*", "")):
                    continue

                file_path = Path(root_dir) / file
                try:
                    count = self._process_file(file_path, find_str, replace_str, timestamp)
                    if count > 0:
                        modified_count += 1
                        total_occurrences += count
                        self.log(f"SUCCESS: Updated '{file_path}' ({count} replacements)")
                except Exception as e:
                    self.log(f"ERROR: Failed processing '{file_path}' - {e}")

        return modified_count, total_occurrences

    def process_csv_batch(self, csv_file_path: str, find_str: str, replace_str: str, timestamp: str) -> str:
        """Reads CSV, targets config files per folder, writes backup, and updates CSV status column."""
        rows = []
        headers = []

        try:
            with open(csv_file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
        except Exception as e:
            err_msg = f"Failed to read CSV file: {e}"
            self.log(f"ERROR: {err_msg}")
            return err_msg

        # Flexible column index mapping
        headers_lower = [h.strip().lower() for h in headers]
        
        def get_col_idx(possible_names):
            for name in possible_names:
                if name in headers_lower:
                    return headers_lower.index(name)
            return -1

        app_idx = get_col_idx(["app name", "app_name", "application", "app"])
        dir_idx = get_col_idx(["folder location", "folder_location", "directory", "folder", "path"])
        cfg_idx = get_col_idx(["configuration file name", "config_file", "file_name", "config file name", "config"])
        status_idx = get_col_idx(["status", "state"])

        if dir_idx == -1:
            return "ERROR: Could not find 'Folder Location' column in CSV."

        # Add Status column header if missing
        if status_idx == -1:
            headers.append("Status")
            status_idx = len(headers) - 1

        updated_apps = 0

        for row in rows:
            # Ensure row matches header length
            while len(row) < len(headers):
                row.append("")

            app_name = row[app_idx].strip() if app_idx != -1 else "N/A"
            folder_loc = row[dir_idx].strip()
            config_name = row[cfg_idx].strip() if cfg_idx != -1 else self.file_extension.get().strip()

            if not config_name:
                config_name = "web.config"

            if not folder_loc or not os.path.exists(folder_loc):
                row[status_idx] = "FAILED: Directory Not Found"
                self.log(f"SKIPPED [{app_name}]: Directory '{folder_loc}' not found.")
                continue

            # Search folder for specific config file
            target_files = [Path(root) / f for root, _, files in os.walk(folder_loc) for f in files if f.lower() == config_name.lower()]

            if not target_files:
                row[status_idx] = f"SKIPPED: '{config_name}' Not Found"
                self.log(f"SKIPPED [{app_name}]: No file matching '{config_name}' in '{folder_loc}'")
                continue

            app_replacements = 0
            for target_file in target_files:
                try:
                    count = self._process_file(target_file, find_str, replace_str, timestamp)
                    if count > 0:
                        app_replacements += count
                        self.log(f"SUCCESS [{app_name}]: Updated '{target_file.name}' ({count} replacements)")
                except Exception as e:
                    self.log(f"ERROR [{app_name}]: Failed on '{target_file}' - {e}")

            if app_replacements > 0:
                row[status_idx] = f"SUCCESS: Updated ({app_replacements} replacements)"
                updated_apps += 1
            else:
                row[status_idx] = "SKIPPED: Search string not found"

        # Overwrite CSV with updated Status values
        try:
            with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            self.log(f"CSV STATUS UPDATED: Rewrote results to '{csv_file_path}'")
        except Exception as e:
            self.log(f"ERROR: Could not update CSV status column - {e}")

        return f"BATCH COMPLETED: Processed {len(rows)} apps, modified configs in {updated_apps} app location(s)."


if __name__ == "__main__":
    root = tk.Tk()
    app = FindReplaceApp(root)
    root.mainloop()