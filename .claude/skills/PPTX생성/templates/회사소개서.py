"""
회사소개서 템플릿 — 8p 기본 뼈대.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from watt_design import Deck
from components import (
    slide_cover, slide_contents, slide_card_3col, slide_card_2col,
    slide_timeline, slide_close,
)

deck = Deck(total_pages=8)

slide_cover(deck, title="㈜와트 회사소개",
            subtitle="산업용 AR 스마트글라스 전문기업",
            meta="YYYY.MM")

slide_contents(deck, sections=[
    ("01", "회사 소개", [("03", "기업 개요")]),
    ("02", "핵심 기술", [("04", "하드웨어·소프트웨어·AI")]),
    ("03", "Track Record", [("05", "주요 고객"), ("06", "성장 로드맵")]),
    ("04", "기술 차별점", [("07", "인증·수상")]),
])

slide_card_3col(deck, title="기업 개요", section_tag="01  회사 소개",
    cards=[
        ("기본 정보", ["㈜와트 (WATT)", "설립 2020", "임직원 16명"]),
        ("대표", ["김진명", "파워플랜트 16년", "AI 컨설턴트"]),
        ("조직", ["개발자 71%", "AR · Big Data", "플랜트 노하우"]),
    ])

slide_card_3col(deck, title="핵심 기술", section_tag="02  핵심 기술",
    cards=[
        ("HARDWARE", ["RealWear Navigator 520", "IP66 / MIL-STD-810H", "48MP 카메라"]),
        ("SOFTWARE", ["WATT TALK·MEMO", "AR Post-it·Checker", "Smart Report·TBM"]),
        ("AI ENGINE", ["Keeby 2.0 — 95%", "100dB 실증", "AR Hands 모션"]),
    ])

slide_timeline(deck, title="주요 고객",
    section_tag="03  Track Record",
    top_grid=[
        ("2020", "삼성엔지니어링", "영상화질평가 1위"),
        ("2023", "현대자동차", "솔루션 납품"),
        ("2023", "DL케미칼", "솔루션 납품"),
        ("2024", "한일시멘트", "스마트팩토리"),
        ("2025", "코오롱", "솔루션 납품"),
        ("2025", "효성중공업", "솔루션 납품"),
    ],
    stages=[])  # 타임라인 영역 비움

slide_timeline(deck, title="성장 로드맵",
    section_tag="03  Track Record",
    stages=[
        ("2020", "창업"),
        ("2021~22", "TIPS · 벤처"),
        ("2023~25", "대기업 확산"),
        ("2026", "Series A"),
        ("2029", "IPO 목표"),
    ])

slide_card_3col(deck, title="기술 차별점 + 인증",
    section_tag="04  기술 차별점",
    cards=[
        ("극한 환경", ["IP66", "MIL-STD-810H", "100dBA 음성인식"]),
        ("산업 AI", ["Keeby 95% 인증", "발전소·교량 실증", "다국어 확장"]),
        ("외부 검증", ["TIPS 선정", "ISO 9001", "특허 4건"]),
    ])

slide_close(deck,
    contacts_left=[
        ("회사", "㈜와트 (WATT CO. LTD.)"),
        ("주소", "경기도 성남 판교이노베이션랩"),
    ],
    contacts_right=[
        ("영업 문의", "wgkim@wattsolution.co.kr"),
        ("고객센터", "070-7124-2588"),
        ("홈페이지", "www.wattsolution.co.kr"),
    ])

out = Path(__file__).parent / "회사소개서_샘플.pptx"
deck.save(out)
print(f"OK: {out}")
