"""
제안서 템플릿 예시 — 14p 기본 뼈대.

사용: 이 파일을 고객사 폴더에 복사한 뒤 콘텐츠만 수정하고 실행.
부모 경로에 watt_design.py, components.py가 있어야 import 가능.
"""

import sys
from pathlib import Path

# watt_design.py, components.py 경로 등록
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from watt_design import Deck  # noqa: E402
from components import (      # noqa: E402
    slide_cover, slide_contents, slide_card_3col, slide_card_2col,
    slide_kpi_3, slide_matrix, slide_timeline, slide_phases, slide_close,
)

# ─── 설정 ─────────────────────────────────────────────────
deck = Deck(total_pages=14)

# ─── S1 표지 ─────────────────────────────────────────────
slide_cover(
    deck,
    title="[제안 주제]\n[서브 주제]",
    subtitle="[한 줄 설명]",
    meta="[고객사] 제출용  |  [응모분야]  |  YYYY.MM",
)

# ─── S2 목차 ─────────────────────────────────────────────
slide_contents(
    deck,
    sections=[
        ("01", "WHO WE ARE",
         [("03", "회사 개요"), ("04", "Track Record · 성장 로드맵")]),
        ("02", "WHY NOW",
         [("05", "고객 통증 포인트")]),
        ("03", "WHAT WE OFFER",
         [("06", "핵심 솔루션"), ("07", "기술 검증 데이터")]),
        ("04", "FIT FOR RFP",
         [("08", "적합 ①"), ("09", "적합 ②")]),
        ("05", "WHY US · IMPACT",
         [("10", "통합 가치"), ("11", "정량 효과")]),
        ("06", "RELIABILITY",
         [("12", "기술 차별점 + 인증")]),
        ("07", "ENGAGEMENT",
         [("13", "협업 모델")]),
    ],
)

# ─── S3 회사 개요 ────────────────────────────────────────
slide_card_3col(
    deck,
    title="회사 개요", subtitle="Who We Are", section_tag="01  WHO WE ARE",
    headline="\u201C한 줄 가치 제안\u201D",
    cards=[
        ("기업 기본 정보", ["회사명", "설립", "임직원", "본사", "홈페이지"]),
        ("대표 프로필", ["前 경력", "현장 경험", "전문성", "역할"]),
        ("기술 중심 조직", ["개발인력 비중", "전문 영역", "핵심 노하우"]),
    ],
)

# ─── S4 Track Record ─────────────────────────────────────
slide_timeline(
    deck,
    title="Track Record + 성장 로드맵", section_tag="01  WHO WE ARE",
    top_grid=[
        ("2020", "고객사 A", "주요 성과"),
        ("2023", "고객사 B", "솔루션 납품"),
        # ... 최대 8개
    ],
    stages=[
        ("2020", "창업"),
        ("2025", "성장"),
        ("2029", "IPO"),
    ],
)

# ─── S5 통증 포인트 ───────────────────────────────────────
slide_card_3col(
    deck,
    title="고객 통증 포인트", subtitle="공통 문제 3가지",
    section_tag="02  WHY NOW",
    cards=[
        ("01  문제 A", ["원인", "영향", "현 한계"]),
        ("02  문제 B", ["원인", "영향", "현 한계"]),
        ("03  문제 C", ["원인", "영향", "현 한계"]),
    ],
)

# ─── S6 핵심 솔루션 ──────────────────────────────────────
slide_card_3col(
    deck,
    title="핵심 솔루션 개요", subtitle="HW + SW + AI",
    section_tag="03  WHAT WE OFFER",
    cards=[
        ("HARDWARE", ["스펙 1", "스펙 2", "스펙 3"]),
        ("SOFTWARE", ["제품 1", "제품 2", "제품 3"]),
        ("AI ENGINE", ["엔진 1", "엔진 2"]),
    ],
)

# ─── S7 기술 검증 ───────────────────────────────────────
slide_card_2col(
    deck,
    title="기술 검증 데이터", section_tag="03  WHAT WE OFFER",
    left=("검증 지표 A", ["수치 1", "수치 2", "수치 3"]),
    right=("검증 지표 B", ["수치 1", "수치 2", "수치 3"]),
)

# ─── S8·9 적합 ①② ──────────────────────────────────────
slide_card_2col(
    deck, title="적합 ① [분야명]", section_tag="04  FIT FOR RFP",
    left=("주요 기능", ["기능 1", "기능 2"]),
    right=("도입 효과", ["효과 1", "효과 2"]),
)
slide_card_2col(
    deck, title="적합 ② [분야명]", section_tag="04  FIT FOR RFP",
    left=("주요 기능", ["기능 1", "기능 2"]),
    right=("도입 효과", ["효과 1", "효과 2"]),
)

# ─── S10 통합 가치 ──────────────────────────────────────
slide_card_3col(
    deck, title="통합 가치 — Why Us",
    section_tag="05  WHY US · IMPACT",
    cards=[
        ("가치 A", ["포인트"]),
        ("가치 B", ["포인트"]),
        ("가치 C", ["포인트"]),
    ],
)

# ─── S11 정량 효과 ───────────────────────────────────────
slide_kpi_3(
    deck, title="도입 효과 — AS-IS vs TO-BE",
    section_tag="05  WHY US · IMPACT",
    kpis=[
        ("15×", "생산성", "기존 → 개선 설명", "green"),
        ("9×", "디지털화", "기존 → 개선 설명", "cyan"),
        ("-100%", "누락률", "기존 → 개선 설명", "red"),
    ],
    bottom_table=[
        ["항목", "AS-IS", "TO-BE", "개선"],
        ["지표 1", "기존", "개선", "수치"],
        ["지표 2", "기존", "개선", "수치"],
    ],
)

# ─── S12 기술 차별점 + 인증 ─────────────────────────────
slide_card_3col(
    deck, title="기술 차별점 + 인증", section_tag="06  RELIABILITY",
    cards=[
        ("차별점 A", ["근거 1", "근거 2"]),
        ("차별점 B", ["근거 1", "근거 2"]),
        ("인증 이력", ["TIPS", "ISO 9001", "특허"]),
    ],
)

# ─── S13 협업 모델 ───────────────────────────────────────
slide_phases(
    deck, title="협업 모델 제안", section_tag="07  ENGAGEMENT",
    phases=[
        ("PHASE 1", "POC (1~2개월)", ["세부 1", "세부 2"]),
        ("PHASE 2", "파일럿 (3~6개월)", ["세부 1", "세부 2"]),
        ("PHASE 3", "롤아웃 (6개월~)", ["세부 1", "세부 2"]),
    ],
)

# ─── S14 컨택 ────────────────────────────────────────────
slide_close(
    deck,
    contacts_left=[("회사", "㈜와트"), ("주소", "경기도 성남 판교이노베이션랩")],
    contacts_right=[
        ("영업 문의", "wgkim@wattsolution.co.kr"),
        ("홈페이지", "www.wattsolution.co.kr"),
    ],
)

# ─── 저장 ────────────────────────────────────────────────
out = Path(__file__).parent / "제안서_샘플.pptx"
deck.save(out)
print(f"OK: {out}")
