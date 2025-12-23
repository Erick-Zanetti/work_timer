import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, QPoint


class FloatingTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Work Timer")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setFixedSize(320, 150)  # Slightly larger for better spacing
        
        # Nord Theme Colors
        self.colors = {
            "bg": "#2E3440",
            "fg": "#D8DEE9",
            "accent": "#88C0D0",
            "success": "#A3BE8C",
            "warning": "#EBCB8B",
            "danger": "#BF616A",
            "highlight": "#4C566A"
        }

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg']};
                color: {self.colors['fg']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                border-radius: 10px;
            }}
            QPushButton {{
                border: none;
                border-radius: 5px;
                padding: 2px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['highlight']};
            }}
        """)
        self.setWindowOpacity(0.92)  # Slightly more opaque

        # Data
        self.timer_data = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Header
        header = QHBoxLayout()
        
        title = QLabel("Work Timer")
        title.setStyleSheet(f"font-weight: bold; color: {self.colors['accent']}; font-size: 14px;")
        header.addWidget(title)

        header.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedSize(24, 24)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_timer)
        add_btn.setStyleSheet(f"color: {self.colors['success']}; font-weight: bold; font-size: 18px;")
        add_btn.setToolTip("Add new timer")
        header.addWidget(add_btn)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet(f"color: {self.colors['danger']}; font-weight: bold;")
        btn_close.setToolTip("Close")
        header.addWidget(btn_close)

        self.layout.addLayout(header)

        # Scroll area or just a layout? Layout is fine for small number of timers.
        self.timers_layout = QVBoxLayout()
        self.layout.addLayout(self.timers_layout)
        self.layout.addStretch()

        self.name_labels = {}
        self.time_labels = {}
        self.buttons = {}
        self.reset_buttons = {}
        self.add_time_buttons = {}

        self.drag_position = QPoint()

    def parse_time_input(self, time_str):
        try:
            parts = time_str.strip().split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return None
        except ValueError:
            return None

    def parse_duration_input(self, duration_str):
        """Parse inputs like '10', '10m', '1h', '30s' into seconds."""
        s = duration_str.strip().lower()
        if not s:
            return 0
        
        multiplier = 60 # Default to minutes
        if s.endswith("s"):
            multiplier = 1
            s = s[:-1]
        elif s.endswith("m"):
            multiplier = 60
            s = s[:-1]
        elif s.endswith("h"):
            multiplier = 3600
            s = s[:-1]
        
        try:
            return int(float(s) * multiplier)
        except ValueError:
            return None

    def add_timer(self, name=None, auto=False):
        if len(self.timer_data) >= 10: # Increased limit to 10
            QMessageBox.warning(self, "Limit Reached", "Limit of 10 timers reached.")
            return

        if not auto:
            name, ok = QInputDialog.getText(self, "New Timer", "Name:")
            if not ok or not name.strip():
                return
            name = name.strip()
            
            initial_time, ok = QInputDialog.getText(self, "Initial Time", "HH:MM:SS or MM:SS (Empty = 0):")
            if not ok:
                return
            if not initial_time.strip():
                initial_time = "00:00:00"
        else:
            name = name.strip()
            initial_time = "00:00:00"

        if name in self.timer_data:
            QMessageBox.warning(self, "Error", "A timer with this name already exists.")
            return

        initial_seconds = self.parse_time_input(initial_time)
        if initial_seconds is None:
            QMessageBox.warning(self, "Error", "Invalid format. Use HH:MM:SS")
            return

        self.timer_data[name] = {"seconds": initial_seconds, "running": False}
        self.adjust_window_height()

        # Row Layout
        row = QHBoxLayout()
        row.setSpacing(5)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet(f"font-weight: 600; color: {self.colors['accent']}; border: none;")
        name_label.setFixedWidth(70)
        self.name_labels[name] = name_label
        
        # Time
        time_label = QLabel("00:00:00")
        time_label.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 16px; font-weight: bold; border: none;")
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setFixedWidth(90)
        self.time_labels[name] = time_label
        
        self.update_label(name)

        # Controls
        # Play/Pause
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(28, 28)
        play_btn.setCursor(Qt.PointingHandCursor)
        play_btn.clicked.connect(lambda _, n=name: self.toggle_timer(n))
        play_btn.setStyleSheet(f"color: {self.colors['success']}; background-color: {self.colors['bg']}; border: 1px solid {self.colors['highlight']};")
        self.buttons[name] = play_btn

        # Add Time
        add_time_btn = QPushButton("+T")
        add_time_btn.setFixedSize(28, 28)
        add_time_btn.setCursor(Qt.PointingHandCursor)
        add_time_btn.clicked.connect(lambda _, n=name: self.prompt_add_time(n))
        add_time_btn.setStyleSheet(f"color: {self.colors['fg']}; background-color: {self.colors['bg']}; border: 1px solid {self.colors['highlight']}; font-size: 11px;")
        add_time_btn.setToolTip("Add time (+5m, 1h...)")
        self.add_time_buttons[name] = add_time_btn

        # Reset
        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(28, 28)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(lambda _, n=name: self.reset_timer(n))
        reset_btn.setStyleSheet(f"color: {self.colors['warning']}; background-color: {self.colors['bg']}; border: 1px solid {self.colors['highlight']}; font-size: 16px;")
        reset_btn.setToolTip("Reset to 0")
        self.reset_buttons[name] = reset_btn

        row.addWidget(name_label)
        row.addWidget(time_label)
        row.addWidget(play_btn)
        row.addWidget(add_time_btn)
        row.addWidget(reset_btn)
        
        self.timers_layout.addLayout(row)

    def adjust_window_height(self):
        # dynamic resize
        count = len(self.timer_data)
        # Header ~40px, padding ~30px, each row ~40px
        base_h = 70 
        row_h = 45 
        target_h = base_h + (count * row_h)
        self.setFixedSize(320, target_h)

    def toggle_timer(self, name):
        # Only Pause functionality requested for this toggle?
        # Preserving original logic: Only one timer runs at a time? 
        # Original: "if key == name: running = not running; else: running = False"
        # Let's keep that logic "exclusive timer" as implied by previous code, 
        # but the user didn't explicitly ask to change it, so I stick to it.
        
        current_state = self.timer_data[name]["running"]
        
        # Pause everything first
        for key in self.timer_data:
            self.timer_data[key]["running"] = False
            self.buttons[key].setText("▶")
            self.buttons[key].setStyleSheet(f"color: {self.colors['success']}; background-color: {self.colors['bg']}; border: 1px solid {self.colors['highlight']};")
        
        # If it was paused, start it (exclusive)
        if not current_state:
            self.timer_data[name]["running"] = True
            self.buttons[name].setText("⏸")
            self.buttons[name].setStyleSheet(f"color: {self.colors['warning']}; background-color: {self.colors['highlight']}; border: 1px solid {self.colors['fg']};")

    def reset_timer(self, name):
        self.timer_data[name]["seconds"] = 0
        self.timer_data[name]["running"] = False
        self.buttons[name].setText("▶")
        self.update_label(name)

    def prompt_add_time(self, name):
        text, ok = QInputDialog.getText(self, "Add Time", 
                                      "Time to add (e.g. 5, 10m, 1h, 30s):")
        if ok and text:
            seconds_to_add = self.parse_duration_input(text)
            if seconds_to_add is not None:
                self.timer_data[name]["seconds"] += seconds_to_add
                if self.timer_data[name]["seconds"] < 0:
                     self.timer_data[name]["seconds"] = 0
                self.update_label(name)
            else:
                QMessageBox.warning(self, "Error", "Invalid format. Use numbers (minutes), '1h', '30s'.")

    def update_time(self):
        for name, data in self.timer_data.items():
            if data["running"]:
                data["seconds"] += 1
                self.update_label(name)

    def update_label(self, name):
        seconds = self.timer_data[name]["seconds"]
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        self.time_labels[name].setText(f"{h:02}:{m:02}:{s:02}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


app = QApplication(sys.argv)
window = FloatingTimer()
window.show()
app.exec_()
