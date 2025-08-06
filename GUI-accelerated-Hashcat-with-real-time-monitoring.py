import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QComboBox, QTextEdit, QLineEdit
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

class HashcatGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU-Accelerated Hashcat GUI")
        self.setFixedSize(640, 550)
        self.setWindowIcon(QIcon("iconfile25.ico"))
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.setup_ui()
        self.hashcat_process = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_hashcat_output)

    def setup_ui(self):
        layout = QVBoxLayout()

        self.hash_file_label = QLabel("Select hash file:")
        self.hash_file_btn = QPushButton("📂 Choose File")
        self.hash_file_btn.clicked.connect(self.choose_hash_file)
        self.hash_file_path = ""

        self.attack_mode_label = QLabel("Attack Mode:")
        self.attack_mode_combo = QComboBox()
        self.attack_mode_combo.addItems([
            "0 - Straight (Dictionary)",
            "3 - Brute Force",
            "6 - Hybrid (Dict + Mask)"
        ])

        self.hash_type_label = QLabel("Hash Type:")
        self.hash_type_combo = QComboBox()
        self.hash_type_combo.addItems([
            "0 - MD5",
            "100 - SHA1",
            "2500 - WPA/WPA2",
            "1400 - SHA256",
            "1800 - SHA512"
        ])

        self.wordlist_label = QLabel("Wordlist path (for dict/hybrid):")
        self.wordlist_input = QLineEdit()

        self.mask_label = QLabel("Mask (for brute-force/hybrid, e.g. ?l?l?l?l):")
        self.mask_input = QLineEdit()

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("background-color: #121212; color: #00ff99; font-family: Consolas;")

        self.start_btn = QPushButton("🚀 Start Crack")
        self.start_btn.clicked.connect(self.run_hashcat)

        layout.addWidget(self.hash_file_label)
        layout.addWidget(self.hash_file_btn)
        layout.addWidget(self.hash_type_label)
        layout.addWidget(self.hash_type_combo)
        layout.addWidget(self.attack_mode_label)
        layout.addWidget(self.attack_mode_combo)
        layout.addWidget(self.wordlist_label)
        layout.addWidget(self.wordlist_input)
        layout.addWidget(self.mask_label)
        layout.addWidget(self.mask_input)
        layout.addWidget(self.start_btn)
        layout.addWidget(QLabel("📡 Real-time Output:"))
        layout.addWidget(self.output_console)

        self.setLayout(layout)

    def choose_hash_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select hash file")
        if file_path:
            self.hash_file_path = file_path
            self.hash_file_label.setText(f"✅ Selected: {file_path}")

    def run_hashcat(self):
        if not self.hash_file_path:
            self.output_console.append("❌ Error: Hash file not selected.")
            return

        hash_type = self.hash_type_combo.currentText().split(" - ")[0].strip()
        attack_mode = self.attack_mode_combo.currentText().split(" - ")[0].strip()
        wordlist = self.wordlist_input.text().strip()
        mask = self.mask_input.text().strip()

        command = ["hashcat", "-m", hash_type, "-a", attack_mode, self.hash_file_path]

        if attack_mode in ["0", "6"] and wordlist:
            command.append(wordlist)
        if attack_mode in ["3", "6"] and mask:
            command.append(mask)

        command += ["--force", "--status", "--status-timer", "2"]

        self.output_console.append("🚀 Starting Hashcat...")
        self.output_console.append("🔧 Command: " + " ".join(command))

        try:
            self.hashcat_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            self.timer.start(1000)
        except Exception as e:
            self.output_console.append(f"❌ Error running Hashcat: {e}")

    def read_hashcat_output(self):
        if self.hashcat_process:
            output = self.hashcat_process.stdout.readline()
            if output:
                self.output_console.append(output.strip())
            if self.hashcat_process.poll() is not None:
                self.output_console.append("✅ Hashcat finished.")
                self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashcatGUI()
    window.show()
    sys.exit(app.exec())