"""
화면 캡처 모듈
mss를 사용하여 지정된 영역의 스크린샷을 캡처합니다.
"""
import mss
import mss.tools
from PIL import Image
from typing import Optional, Tuple


class ScreenCapture:
    """화면 특정 영역을 캡처하는 클래스"""

    def __init__(self):
        self.sct = mss.mss()
        self._region: Optional[Tuple[int, int, int, int]] = None

    def set_region(self, x: int, y: int, width: int, height: int):
        """캡처할 영역 설정

        Args:
            x: 영역 좌상단 x 좌표
            y: 영역 좌상단 y 좌표
            width: 영역 너비
            height: 영역 높이
        """
        self._region = (x, y, width, height)

    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """현재 설정된 영역 반환"""
        return self._region

    def capture(self) -> Optional[Image.Image]:
        """설정된 영역을 캡처하여 PIL Image로 반환

        Returns:
            PIL Image 객체 또는 영역 미설정 시 None
        """
        if not self._region:
            return None

        x, y, width, height = self._region

        # mss 캡처 영역 형식
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }

        # 스크린샷 캡처
        screenshot = self.sct.grab(monitor)

        # PIL Image로 변환
        img = Image.frombytes(
            "RGB",
            (screenshot.width, screenshot.height),
            screenshot.rgb
        )

        return img

    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """지정된 영역을 즉시 캡처

        Args:
            x, y: 좌상단 좌표
            width, height: 영역 크기

        Returns:
            PIL Image 객체
        """
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }

        screenshot = self.sct.grab(monitor)

        return Image.frombytes(
            "RGB",
            (screenshot.width, screenshot.height),
            screenshot.rgb
        )

    def close(self):
        """리소스 해제"""
        self.sct.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # 테스트용
    with ScreenCapture() as capture:
        # 화면 좌상단 200x100 영역 캡처
        img = capture.capture_region(0, 0, 200, 100)
        img.save("test_capture.png")
        print(f"Captured: {img.size}")
