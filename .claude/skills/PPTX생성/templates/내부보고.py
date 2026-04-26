"""
내부 보고 템플릿 — 6p 간단 뼈대.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from watt_design import Deck
from components import (
    slide_cover, slide_card_3col, slide_card_2col, slide_kpi_3, slide_close,
)

deck = Deck(total_pages=6)

slide_cover(deck, title="[보고 주제]",
            subtitle="[한 줄 요약]", meta="YYYY.MM.DD")

slide_card_3col(deck, title="현황 요약", section_tag="01  현황",
    cards=[
        ("영역 A", ["현황 1", "현황 2"]),
        ("영역 B", ["현황 1", "현황 2"]),
        ("영역 C", ["현황 1", "현황 2"]),
    ])

slide_kpi_3(deck, title="주요 지표", section_tag="02  지표",
    kpis=[
        ("A", "지표명", "설명", "green"),
        ("B", "지표명", "설명", "cyan"),
        ("C", "지표명", "설명", "red"),
    ])

slide_card_2col(deck, title="분석·원인", section_tag="03  분석",
    left=("잘된 점", ["포인트"]),
    right=("개선 필요", ["포인트"]))

slide_card_3col(deck, title="결론 및 다음 액션", section_tag="04  액션",
    cards=[
        ("결론", ["요약"]),
        ("단기 액션", ["1주~1개월"]),
        ("장기 액션", ["1~3개월"]),
    ])

slide_close(deck, headline="Thank You",
    message="질문 · 피드백 환영합니다.")

out = Path(__file__).parent / "내부보고_샘플.pptx"
deck.save(out)
print(f"OK: {out}")
