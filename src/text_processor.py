"""
텍스트 처리 모듈
인식된 텍스트의 중복 제거, 저장 등을 담당합니다.
"""
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from pathlib import Path


class TextProcessor:
    """인식된 텍스트 처리 및 저장"""

    def __init__(self, similarity_threshold: float = 0.8):
        """텍스트 처리기 초기화

        Args:
            similarity_threshold: 중복 판단 유사도 임계값 (0.0 ~ 1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.entries: List[Tuple[datetime, str]] = []  # (타임스탬프, 텍스트)
        self._last_text = ""

    def add_text(self, text: str) -> bool:
        """텍스트 추가 (중복 시 무시)

        Args:
            text: 인식된 텍스트

        Returns:
            True: 새 텍스트로 추가됨
            False: 중복으로 무시됨
        """
        text = text.strip()

        # 빈 텍스트 무시
        if not text:
            return False

        # 중복 체크
        if self._is_duplicate(text):
            return False

        # 새 텍스트 추가
        self.entries.append((datetime.now(), text))
        self._last_text = text
        return True

    def _is_duplicate(self, text: str) -> bool:
        """중복 텍스트인지 확인

        Args:
            text: 비교할 텍스트

        Returns:
            True: 중복임
        """
        if not self._last_text:
            return False

        similarity = SequenceMatcher(
            None,
            self._last_text.lower(),
            text.lower()
        ).ratio()

        return similarity >= self.similarity_threshold

    def get_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트의 유사도 계산

        Returns:
            유사도 (0.0 ~ 1.0)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def get_all_texts(self) -> List[str]:
        """저장된 모든 텍스트 반환"""
        return [text for _, text in self.entries]

    def get_latest_text(self) -> Optional[str]:
        """가장 최근 텍스트 반환"""
        return self._last_text if self._last_text else None

    def clear(self):
        """저장된 텍스트 초기화"""
        self.entries.clear()
        self._last_text = ""

    def save_to_txt(self, filepath: str):
        """일반 텍스트 파일로 저장

        Args:
            filepath: 저장할 파일 경로
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for timestamp, text in self.entries:
                time_str = timestamp.strftime("%H:%M:%S")
                f.write(f"[{time_str}] {text}\n")

    def save_to_srt(self, filepath: str):
        """SRT 자막 파일로 저장

        Args:
            filepath: 저장할 파일 경로 (.srt)
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            for i, (timestamp, text) in enumerate(self.entries, 1):
                # SRT 인덱스
                f.write(f"{i}\n")

                # 타임스탬프 (시작 ~ 시작+2초로 가정)
                start = timestamp
                end = timestamp + timedelta(seconds=2)
                start_str = start.strftime("%H:%M:%S,000")
                end_str = end.strftime("%H:%M:%S,000")
                f.write(f"{start_str} --> {end_str}\n")

                # 텍스트
                f.write(f"{text}\n\n")

    def save(self, filepath: str, format: str = "txt"):
        """파일로 저장

        Args:
            filepath: 저장할 파일 경로
            format: 저장 형식 ("txt" 또는 "srt")
        """
        if format.lower() == "srt":
            self.save_to_srt(filepath)
        else:
            self.save_to_txt(filepath)

    def __len__(self) -> int:
        """저장된 텍스트 개수"""
        return len(self.entries)


if __name__ == "__main__":
    # 테스트용
    processor = TextProcessor()

    # 텍스트 추가 테스트
    texts = [
        "Hello, world!",
        "Hello, world!",  # 중복
        "Hello, World!",  # 유사 (대소문자)
        "This is different.",
        "This is different!",  # 유사
        "Completely new text.",
    ]

    for text in texts:
        added = processor.add_text(text)
        status = "추가됨" if added else "중복"
        print(f"'{text}' -> {status}")

    print(f"\n총 {len(processor)}개 텍스트 저장됨")
    print("저장된 텍스트:", processor.get_all_texts())

    # 파일 저장 테스트
    processor.save("test_output.txt", "txt")
    processor.save("test_output.srt", "srt")
    print("\n파일 저장 완료: test_output.txt, test_output.srt")
