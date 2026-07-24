import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

class FindReplaceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File String Find & Replace")
        self.resize(850, 600)
        self.init_ui()

    def init_ui(self):
        # Main Layout container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ------------------- TOP PANEL -------------------
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setFrameShadow(QFrame.Shadow.Raised)
        
        panel_layout = QVBoxLayout(panel)

        # Row 1: Folder Selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Folder Path:")
        folder_label.setFixedWidth(80)
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select a directory...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)

        # Row 2: Text Inputs & Buttons
        controls_layout = QHBoxLayout()

        # Find Input
        find_label = QLabel("Find:")
        find_label.setFixedWidth(80)
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Text to search...")

        # Replace Input
        replace_label = QLabel("Replace:")
        replace_label.setFixedWidth(60)
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Text to replace with...")

        # Action Buttons
        find_btn = QPushButton("Find")
        find_btn.clicked.connect(self.find_strings)
        
        replace_btn = QPushButton("Replace")
        replace_btn.clicked.connect(self.replace_strings)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        # Add items to Row 2
        controls_layout.addWidget(find_label)
        controls_layout.addWidget(self.find_input)
        controls_layout.addWidget(replace_label)
        controls_layout.addWidget(self.replace_input)
        controls_layout.addWidget(find_btn)
        controls_layout.addWidget(replace_btn)
        controls_layout.addWidget(close_btn)

        # Assemble Panel
        panel_layout.addLayout(folder_layout)
        panel_layout.addLayout(controls_layout)
        main_layout.addWidget(panel)

        # ------------------- RESULTS GRID -------------------
        self.grid = QTableWidget()
        self.grid.setColumnCount(3)
        self.grid.setHorizontalHeaderLabels(["Folder Name", "File Name", "Matched String"])
        
        # Grid layout adjustments
        header = self.grid.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.grid.setColumnWidth(1, 200)
        self.grid.setColumnWidth(2, 250)

        main_layout.addWidget(self.grid)

    # ------------------- LOGIC & EVENTS -------------------
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def find_strings(self):
        folder_path = self.folder_input.text().strip()
        search_str = self.find_input.text()

        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", "Please select a valid folder directory.")
            return

        if not search_str:
            QMessageBox.warning(self, "Error", "Please enter a search string in 'Find'.")
            return

        # Clear existing results
        self.grid.setRowCount(0)

        # Search recursively through folder
        matches_found = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_str in content:
                            row_idx = self.grid.rowCount()
                            self.grid.insertRow(row_idx)
                            
                            self.grid.setItem(row_idx, 0, QTableWidgetItem(root))
                            self.grid.setItem(row_idx, 1, QTableWidgetItem(file))
                            self.grid.setItem(row_idx, 2, QTableWidgetItem(search_str))
                            matches_found += 1
                except Exception:
                    # Skips non-readable binary files or system-restricted files safely
                    continue

        if matches_found == 0:
            QMessageBox.information(self, "Result", f"No matches found for '{search_str}'.")

    def replace_strings(self):
        folder_path = self.folder_input.text().strip()
        find_str = self.find_input.text()
        replace_str = self.replace_input.text()

        if not folder_path or not os.path.exists(folder_path):
            QMessageBox.warning(self, "Error", "Please select a valid folder directory.")
            return

        if not find_str:
            QMessageBox.warning(self, "Error", "Please enter a search string in 'Find'.")
            return

        # Confirm replacement action
        confirm = QMessageBox.question(
            self, 
            "Confirm Replace", 
            f"Are you sure you want to replace all occurrences of '{find_str}' with '{replace_str}' in all matching files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        replaced_count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if find_str in content:
                        new_content = content.replace(find_str, replace_str)
                        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                            f.write(new_content)
                        replaced_count += 1
                except Exception:
                    continue

        QMessageBox.information(self, "Success", f"Replaced text in {replaced_count} file(s).")
        # Refresh grid results after replace
        self.find_strings()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FindReplaceApp()
    window.show()
    sys.exit(app.exec())