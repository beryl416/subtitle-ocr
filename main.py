#!/usr/bin/env python3
"""
Subtitle OCR - 화면 자막 실시간 인식 앱

화면의 특정 영역을 드래그로 선택하면,
해당 영역의 자막을 실시간으로 OCR 인식하여 파일로 저장합니다.

사용법:
    python main.py

사전 요구사항:
    1. Tesseract OCR 설치:
       macOS: brew install tesseract
       Ubuntu: sudo apt install tesseract-ocr

    2. Python 패키지 설치:
       pip install -r requirements.txt

    3. macOS: 시스템 환경설정 > 개인정보 보호 및 보안 > 화면 녹화
       에서 터미널 또는 Python에 권한 부여
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow


def main():
    # macOS에서 높은 DPI 지원
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Subtitle OCR")

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
