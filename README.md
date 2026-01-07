# Subtitle OCR

화면의 특정 영역을 선택하면 실시간으로 자막을 인식하여 텍스트로 변환하는 macOS 데스크톱 앱입니다.

## Features

- **영역 선택**: 드래그로 자막 영역 지정
- **실시간 OCR**: 선택한 영역을 주기적으로 캡처하여 텍스트 인식
- **밝기 필터**: 슬라이더로 자막만 인식하도록 조절 (배경 텍스트 무시)
- **중복 제거**: 같은 자막이 반복 저장되지 않음
- **파일 저장**: txt 또는 srt 형식으로 내보내기

## Installation

### 1. Tesseract OCR 설치

```bash
brew install tesseract
```

### 2. Python 패키지 설치

```bash
pip3 install -r requirements.txt
```

### 3. macOS 권한 설정

시스템 설정 > 개인정보 보호 및 보안 > 화면 녹화에서 터미널(또는 Python)에 권한을 허용하세요.

## Usage

```bash
python3 main.py
```

1. **Select Region** 클릭 → 빨간 프레임을 자막 위치로 드래그
2. 프레임 크기 조절 후 **OK** 클릭
3. **Brightness Filter** 슬라이더로 자막만 인식되도록 조절
   - 높이면 (250~255): 거의 흰색만 인식
   - 낮추면 (150~200): 더 많은 텍스트 인식
4. **Start** 클릭 → 실시간 자막 인식 시작
5. **Stop** → **Save to File** 클릭하여 저장

## Requirements

- Python 3.8+
- macOS (화면 캡처 기능)
- Tesseract OCR

## Tech Stack

- **UI**: PyQt6
- **Screen Capture**: mss
- **OCR**: pytesseract (Tesseract)
- **Image Processing**: Pillow, NumPy
