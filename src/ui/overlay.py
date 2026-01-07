"""
영역 선택 프레임
드래그로 이동하고 크기를 조절할 수 있는 투명한 선택 프레임입니다.
"""
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QPen


class SelectionFrame(QWidget):
    """드래그로 이동/리사이즈 가능한 선택 프레임"""

    # 영역 선택 완료 시그널: (x, y, width, height)
    region_selected = pyqtSignal(int, int, int, int)
    # 선택 취소 시그널
    selection_cancelled = pyqtSignal()

    EDGE_MARGIN = 10  # 리사이즈 감지 영역

    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._resizing = False
        self._resize_edge = None

        self._setup_window()
        self._setup_ui()

    def _setup_window(self):
        """창 설정"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 초기 크기와 위치
        self.setGeometry(100, 100, 400, 100)
        self.setMinimumSize(100, 50)

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 버튼을 상단에 배치
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        self.confirm_btn = QPushButton("OK")
        self.confirm_btn.setFixedSize(50, 25)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.confirm_btn.clicked.connect(self._confirm_selection)

        self.cancel_btn = QPushButton("X")
        self.cancel_btn.setFixedSize(30, 25)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self._cancel_selection)

        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addStretch()

    def paintEvent(self, event):
        """테두리 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 빨간색 테두리
        pen = QPen(QColor(255, 0, 0), 3)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        # 모서리 리사이즈 핸들 표시
        handle_color = QColor(255, 0, 0)
        painter.setBrush(handle_color)
        handle_size = 8

        # 우하단 모서리
        painter.drawRect(
            self.width() - handle_size - 2,
            self.height() - handle_size - 2,
            handle_size, handle_size
        )

    def _get_edge(self, pos):
        """마우스 위치에 따른 리사이즈 방향 반환"""
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        margin = self.EDGE_MARGIN

        on_right = w - margin <= x <= w
        on_bottom = h - margin <= y <= h

        if on_right and on_bottom:
            return "bottom-right"
        elif on_right:
            return "right"
        elif on_bottom:
            return "bottom"
        return None

    def mousePressEvent(self, event):
        """마우스 클릭"""
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge(event.pos())
            if edge:
                self._resizing = True
                self._resize_edge = edge
            else:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """마우스 이동 - 드래그 또는 리사이즈"""
        if self._resizing and self._resize_edge:
            # 리사이즈
            global_pos = event.globalPosition().toPoint()
            geo = self.geometry()

            if "right" in self._resize_edge:
                new_width = max(self.minimumWidth(), global_pos.x() - geo.x())
                geo.setWidth(new_width)
            if "bottom" in self._resize_edge:
                new_height = max(self.minimumHeight(), global_pos.y() - geo.y())
                geo.setHeight(new_height)

            self.setGeometry(geo)

        elif self._drag_pos:
            # 드래그로 이동
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        else:
            # 커서 모양 변경
            edge = self._get_edge(event.pos())
            if edge == "bottom-right":
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edge == "right":
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge == "bottom":
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseReleaseEvent(self, event):
        """마우스 릴리즈"""
        self._drag_pos = None
        self._resizing = False
        self._resize_edge = None

    def _confirm_selection(self):
        """선택 확정"""
        geo = self.geometry()
        self.hide()
        self.region_selected.emit(geo.x(), geo.y(), geo.width(), geo.height())

    def _cancel_selection(self):
        """선택 취소"""
        self.hide()
        self.selection_cancelled.emit()

    def keyPressEvent(self, event):
        """키보드 이벤트"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._confirm_selection()
        elif event.key() == Qt.Key.Key_Escape:
            self._cancel_selection()

    def show_overlay(self):
        """프레임 표시"""
        self.show()
        self.activateWindow()


# 하위 호환성을 위한 별칭
SelectionOverlay = SelectionFrame


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    frame = SelectionFrame()

    def on_selected(x, y, w, h):
        print(f"Selected region: ({x}, {y}) - {w}x{h}")
        app.quit()

    def on_cancelled():
        print("Selection cancelled")
        app.quit()

    frame.region_selected.connect(on_selected)
    frame.selection_cancelled.connect(on_cancelled)
    frame.show_overlay()

    sys.exit(app.exec())
