import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, QPoint


class FloatingTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Work Timer")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(250, 110)
        self.setStyleSheet("background-color: #2E3440; color: #D8DEE9; font-size: 14px;")
        self.setWindowOpacity(0.8)

        # Agora timers dinâmicos!
        self.timer_data = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Header: botão fechar + botão adicionar
        header = QHBoxLayout()

        header.addStretch()  # Isso empurra tudo pra direita

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(30)
        add_btn.clicked.connect(self.add_timer)
        add_btn.setStyleSheet("background: none; color: #A3BE8C; border: none; font-size: 22px;")
        header.addWidget(add_btn)

        btn_close = QPushButton("❌")
        btn_close.setFixedWidth(30)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("background: none; color: #D8DEE9; border: none; font-size: 16px;")
        header.addWidget(btn_close)

        self.layout.addLayout(header)
        self.layout.setAlignment(header, Qt.AlignTop)

        # Container for the timers
        self.timers_layout = QVBoxLayout()
        self.layout.addLayout(self.timers_layout)

        self.name_labels = {}
        self.time_labels = {}
        self.buttons = {}
        self.reset_buttons = {}

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

    def add_timer(self, name=None, auto=False):
        if len(self.timer_data) >= 2:
            QMessageBox.warning(self, "Maximo", "Você já tem 2 timers. Por favor, remova um antes de adicionar outro.")
            return
        if not auto:
            name, ok = QInputDialog.getText(self, "Adicionar Timer", "Nome do Timer:")
            if not ok or not name.strip():
                return
            name = name.strip().lower()
            
            # Diálogo para o valor inicial (opcional)
            initial_time, ok = QInputDialog.getText(self, "Valor Inicial (Opcional)", "Tempo inicial (formato: HH:MM:SS ou MM:SS) - deixe vazio para 00:00:00:")
            if not ok:
                return
            # Se não informou nada, usa 00:00:00
            if not initial_time.strip():
                initial_time = "00:00:00"
        else:
            name = name.strip().lower()
            initial_time = "00:00:00"

        if name in self.timer_data:
            return  # evita duplicatas

        # Converter o tempo inicial para segundos
        initial_seconds = self.parse_time_input(initial_time)
        if initial_seconds is None:
            QMessageBox.warning(self, "Formato Inválido", "Use o formato HH:MM:SS ou MM:SS")
            return

        self.timer_data[name] = {"seconds": initial_seconds, "running": False}

        # Layout horizontal para tudo na mesma linha
        hbox = QHBoxLayout()
        
        # Label do nome
        name_label = QLabel(f"{name.upper()}")
        name_label.setStyleSheet("font-weight: bold; color: #81A1C1;")
        name_label.setFixedWidth(70)
        self.name_labels[name] = name_label
        
        # Label do tempo
        time_label = QLabel("00:00:00")
        time_label.setStyleSheet("font-family: 'Courier New', monospace; font-size: 16px;")
        time_label.setFixedWidth(80)
        self.time_labels[name] = time_label
        
        # Atualizar a label com o tempo inicial
        self.update_label(name)

        play_pause = QPushButton("▶️")
        play_pause.setFixedWidth(30)
        play_pause.clicked.connect(lambda _, n=name: self.toggle_timer(n))
        self.buttons[name] = play_pause

        reset = QPushButton("⏹")
        reset.setFixedWidth(30)
        reset.clicked.connect(lambda _, n=name: self.reset_timer(n))
        self.reset_buttons[name] = reset

        hbox.addWidget(name_label)
        hbox.addWidget(time_label)
        hbox.addWidget(play_pause)
        hbox.addWidget(reset)
        
        self.timers_layout.addLayout(hbox)

    def toggle_timer(self, name):
        for key in self.timer_data:
            if key == name:
                self.timer_data[key]["running"] = not self.timer_data[key]["running"]
                self.buttons[key].setText("⏸" if self.timer_data[key]["running"] else "▶️")
            else:
                self.timer_data[key]["running"] = False
                self.buttons[key].setText("▶️")

    def reset_timer(self, name):
        self.timer_data[name]["seconds"] = 0
        self.update_label(name)

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
