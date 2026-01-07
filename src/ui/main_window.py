"""
메인 윈도우 UI
자막 OCR 앱의 메인 컨트롤 창입니다.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QTextEdit,
    QFileDialog, QComboBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from .overlay import SelectionOverlay
from ..capture import ScreenCapture
from ..ocr_engine import OCREngine, check_tesseract_installed
from ..text_processor import TextProcessor


class MainWindow(QMainWindow):
    """자막 OCR 메인 윈도우"""

    def __init__(self):
        super().__init__()

        # 컴포넌트 초기화
        self.overlay = SelectionOverlay()
        self.capture = ScreenCapture()
        self.ocr = OCREngine(lang="eng")
        self.processor = TextProcessor()

        # 타이머 (실시간 캡처용)
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._on_capture_tick)

        # 상태
        self.is_running = False
        self.region_set = False

        # UI 초기화
        self._setup_ui()
        self._connect_signals()

        # Tesseract 설치 확인
        self._check_dependencies()

    def _setup_ui(self):
        """UI 구성"""
        self.setWindowTitle("Subtitle OCR")
        self.setMinimumSize(450, 500)

        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # === 영역 선택 그룹 ===
        region_group = QGroupBox("Capture Region")
        region_layout = QVBoxLayout(region_group)

        self.region_label = QLabel("No region selected")
        self.region_label.setStyleSheet("color: gray;")
        region_layout.addWidget(self.region_label)

        self.select_btn = QPushButton("Select Region")
        self.select_btn.setFixedHeight(35)
        region_layout.addWidget(self.select_btn)

        layout.addWidget(region_group)

        # === 컨트롤 그룹 ===
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout(control_group)

        # 시작/정지 버튼
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setFixedHeight(40)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
        """)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QPushButton:hover:!disabled {
                background-color: #da190b;
            }
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        control_layout.addLayout(btn_layout)

        # 캡처 간격 슬라이더
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Capture Interval:"))
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(200)  # 0.2초
        self.interval_slider.setMaximum(2000)  # 2초
        self.interval_slider.setValue(500)  # 기본 0.5초
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.setTickInterval(200)
        interval_layout.addWidget(self.interval_slider)

        self.interval_label = QLabel("0.5s")
        self.interval_label.setMinimumWidth(40)
        interval_layout.addWidget(self.interval_label)
        control_layout.addLayout(interval_layout)

        # 밝기 임계값 슬라이더 (자막 필터링용)
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(QLabel("Brightness Filter:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(150)  # 낮으면 더 많은 텍스트 인식
        self.brightness_slider.setMaximum(255)  # 높으면 흰색만 인식
        self.brightness_slider.setValue(240)  # 기본값
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(20)
        brightness_layout.addWidget(self.brightness_slider)

        self.brightness_label = QLabel("240")
        self.brightness_label.setMinimumWidth(40)
        brightness_layout.addWidget(self.brightness_label)
        control_layout.addLayout(brightness_layout)

        # 안내 라벨
        hint_label = QLabel("↑ 높이면 흰색만, 낮추면 더 많이 인식")
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        control_layout.addWidget(hint_label)

        layout.addWidget(control_group)

        # === 결과 표시 그룹 ===
        result_group = QGroupBox("Recognized Subtitles")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Menlo", 12))
        self.result_text.setMinimumHeight(150)
        result_layout.addWidget(self.result_text)

        # 통계 라벨
        self.stats_label = QLabel("0 subtitles captured")
        self.stats_label.setStyleSheet("color: gray;")
        result_layout.addWidget(self.stats_label)

        # 클리어 버튼
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_results)
        result_layout.addWidget(self.clear_btn)

        layout.addWidget(result_group)

        # === 저장 그룹 ===
        save_group = QGroupBox("Save")
        save_layout = QVBoxLayout(save_group)

        # 형식 선택
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["txt", "srt"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        save_layout.addLayout(format_layout)

        # 저장 버튼
        self.save_btn = QPushButton("Save to File...")
        self.save_btn.setFixedHeight(35)
        save_layout.addWidget(self.save_btn)

        layout.addWidget(save_group)

        # 상태바
        self.statusBar().showMessage("Ready")

    def _connect_signals(self):
        """시그널 연결"""
        # 버튼
        self.select_btn.clicked.connect(self._select_region)
        self.start_btn.clicked.connect(self._start_capture)
        self.stop_btn.clicked.connect(self._stop_capture)
        self.save_btn.clicked.connect(self._save_to_file)

        # 슬라이더
        self.interval_slider.valueChanged.connect(self._on_interval_changed)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)

        # 오버레이
        self.overlay.region_selected.connect(self._on_region_selected)
        self.overlay.selection_cancelled.connect(self._on_selection_cancelled)

    def _check_dependencies(self):
        """의존성 확인"""
        if not check_tesseract_installed():
            QMessageBox.warning(
                self,
                "Tesseract Not Found",
                "Tesseract OCR is not installed.\n\n"
                "Please install it:\n"
                "  macOS: brew install tesseract\n"
                "  Ubuntu: sudo apt install tesseract-ocr\n\n"
                "The app will not work without Tesseract."
            )

    def _select_region(self):
        """영역 선택 오버레이 표시"""
        self.hide()  # 메인 창 숨기기
        QTimer.singleShot(100, self.overlay.show_overlay)

    def _on_region_selected(self, x: int, y: int, w: int, h: int):
        """영역 선택 완료"""
        self.capture.set_region(x, y, w, h)
        self.region_set = True

        self.region_label.setText(f"Region: ({x}, {y}) - {w}x{h}")
        self.region_label.setStyleSheet("color: green; font-weight: bold;")

        self.start_btn.setEnabled(True)
        self.statusBar().showMessage(f"Region selected: {w}x{h}")

        self.show()  # 메인 창 다시 표시

    def _on_selection_cancelled(self):
        """영역 선택 취소"""
        self.show()
        self.statusBar().showMessage("Selection cancelled")

    def _on_interval_changed(self, value: int):
        """캡처 간격 변경"""
        seconds = value / 1000
        self.interval_label.setText(f"{seconds:.1f}s")

        # 실행 중이면 타이머 업데이트
        if self.is_running:
            self.capture_timer.setInterval(value)

    def _on_brightness_changed(self, value: int):
        """밝기 임계값 변경"""
        self.brightness_label.setText(str(value))
        self.ocr.set_subtitle_mode(True, value)

    def _start_capture(self):
        """실시간 캡처 시작"""
        if not self.region_set:
            return

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_btn.setEnabled(False)

        interval = self.interval_slider.value()
        self.capture_timer.start(interval)

        self.statusBar().showMessage("Capturing...")

    def _stop_capture(self):
        """캡처 중지"""
        self.is_running = False
        self.capture_timer.stop()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)

        self.statusBar().showMessage("Stopped")

    def _on_capture_tick(self):
        """캡처 타이머 틱"""
        # 스크린샷 캡처
        image = self.capture.capture()
        if image is None:
            return

        # OCR 수행
        text = self.ocr.extract_text(image)

        # 텍스트 추가 (중복 제거됨)
        if self.processor.add_text(text):
            # 새 텍스트가 추가됨
            self.result_text.append(text)
            self._update_stats()

    def _update_stats(self):
        """통계 업데이트"""
        count = len(self.processor)
        self.stats_label.setText(f"{count} subtitle(s) captured")

    def _clear_results(self):
        """결과 초기화"""
        self.processor.clear()
        self.result_text.clear()
        self._update_stats()
        self.statusBar().showMessage("Cleared")

    def _save_to_file(self):
        """파일로 저장"""
        if len(self.processor) == 0:
            QMessageBox.information(
                self,
                "Nothing to Save",
                "No subtitles have been captured yet."
            )
            return

        # 형식에 따른 필터
        format_type = self.format_combo.currentText()
        if format_type == "srt":
            file_filter = "SRT Files (*.srt)"
            default_name = "subtitles.srt"
        else:
            file_filter = "Text Files (*.txt)"
            default_name = "subtitles.txt"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Subtitles",
            default_name,
            file_filter
        )

        if filepath:
            self.processor.save(filepath, format_type)
            self.statusBar().showMessage(f"Saved to {filepath}")
            QMessageBox.information(
                self,
                "Saved",
                f"Subtitles saved to:\n{filepath}"
            )

    def closeEvent(self, event):
        """창 닫기 이벤트"""
        self._stop_capture()
        self.capture.close()
        event.accept()
