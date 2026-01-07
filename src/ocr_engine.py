"""
OCR 엔진 모듈
pytesseract를 사용하여 이미지에서 텍스트를 추출합니다.
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional
import numpy as np


class OCREngine:
    """Tesseract OCR 엔진 래퍼"""

    def __init__(self, lang: str = "eng"):
        """OCR 엔진 초기화

        Args:
            lang: OCR 언어 설정 (eng, kor, eng+kor 등)
        """
        self.lang = lang
        # Tesseract 설정: 자막에 최적화
        self.config = "--psm 6 --oem 3"
        # psm 6: 균일한 텍스트 블록으로 가정
        # oem 3: 기본 LSTM 엔진

        # 자막 필터링 모드 (밝은 텍스트만 추출)
        self.subtitle_mode = True
        self.brightness_threshold = 240  # 이 값 이상의 밝기만 텍스트로 인식 (거의 흰색만)

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """OCR 정확도 향상을 위한 이미지 전처리

        Args:
            image: 원본 PIL Image

        Returns:
            전처리된 PIL Image
        """
        # 자막 모드: 밝은 텍스트만 추출
        if self.subtitle_mode:
            image = self._extract_bright_text(image)

        # 그레이스케일 변환
        if image.mode != "L":
            image = image.convert("L")

        # 대비 향상
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # 샤프닝
        image = image.filter(ImageFilter.SHARPEN)

        # 이미지 크기 확대 (OCR 정확도 향상)
        width, height = image.size
        if width < 300:
            scale = 300 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def _extract_bright_text(self, image: Image.Image) -> Image.Image:
        """밝은 텍스트(자막)만 추출하고 나머지는 검은색으로

        자막은 보통 흰색/밝은색이므로 밝은 픽셀만 남김
        """
        # RGB로 변환
        if image.mode != "RGB":
            image = image.convert("RGB")

        # numpy 배열로 변환
        img_array = np.array(image)

        # 각 픽셀의 최대 밝기 (R, G, B 중 최대값)
        brightness = np.max(img_array, axis=2)

        # 밝은 픽셀만 남기고 나머지는 검은색
        mask = brightness >= self.brightness_threshold

        # 결과 이미지 생성 (흰 텍스트 on 검은 배경)
        result = np.zeros_like(img_array)
        result[mask] = img_array[mask]

        return Image.fromarray(result)

    def set_subtitle_mode(self, enabled: bool, threshold: int = 200):
        """자막 모드 설정

        Args:
            enabled: 자막 모드 활성화 여부
            threshold: 밝기 임계값 (0-255, 높을수록 더 밝은 텍스트만 인식)
        """
        self.subtitle_mode = enabled
        self.brightness_threshold = threshold

    def extract_text(self, image: Image.Image, preprocess: bool = True) -> str:
        """이미지에서 텍스트 추출

        Args:
            image: PIL Image 객체
            preprocess: 전처리 적용 여부

        Returns:
            추출된 텍스트 문자열
        """
        if preprocess:
            image = self.preprocess_image(image)

        try:
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=self.config
            )
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract가 설치되어 있지 않습니다.\n"
                "macOS: brew install tesseract\n"
                "Ubuntu: sudo apt install tesseract-ocr"
            )

    def set_language(self, lang: str):
        """OCR 언어 변경

        Args:
            lang: 언어 코드 (eng, kor, jpn 등)
        """
        self.lang = lang

    def get_confidence(self, image: Image.Image) -> float:
        """OCR 신뢰도 반환

        Args:
            image: PIL Image 객체

        Returns:
            평균 신뢰도 (0-100)
        """
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            confidences = [
                int(conf) for conf in data["conf"]
                if conf != "-1"
            ]
            return sum(confidences) / len(confidences) if confidences else 0
        except Exception:
            return 0


def check_tesseract_installed() -> bool:
    """Tesseract 설치 여부 확인"""
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        return False


if __name__ == "__main__":
    # 테스트용
    if not check_tesseract_installed():
        print("Tesseract가 설치되어 있지 않습니다.")
        print("설치 방법: brew install tesseract")
    else:
        print(f"Tesseract 버전: {pytesseract.get_tesseract_version()}")

        # 테스트 이미지가 있다면 테스트
        try:
            test_img = Image.open("test_capture.png")
            ocr = OCREngine()
            text = ocr.extract_text(test_img)
            print(f"추출된 텍스트: {text}")
        except FileNotFoundError:
            print("테스트 이미지가 없습니다.")
