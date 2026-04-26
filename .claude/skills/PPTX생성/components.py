"""
WATT PPTX Components — 표준 슬라이드 타입별 컴포넌트.

각 함수는 Deck 인스턴스를 받아 슬라이드 1장을 추가하고, 해당 slide 객체를 반환한다.
"""

from watt_design import (
    Deck, page_frame, card, kpi_box,
    add_rect, add_text, add_bullets,
    NAVY, CYAN, DARK, GRAY, LIGHT_GRAY, SECTION_BG, WHITE,
    ACCENT_RED, ACCENT_GREEN,
    Inches, Pt, Emu, MSO_SHAPE, PP_ALIGN, MSO_ANCHOR,
)


# ═════════════════════════════════════════════════════════
# 1. COVER — 표지
# ═════════════════════════════════════════════════════════
def slide_cover(deck: Deck, *, title: str, subtitle: str = "",
                brand_line: str = "㈜ 와트  |  WATT",
                meta: str = ""):
    """다크(Gray 100) 배경 + Blue 60 액센트 바."""
    s = deck.add_slide()
    add_rect(s, 0, 0, deck.SW, deck.SH, fill=NAVY)
    add_rect(s, 0, Inches(3.3), deck.SW, Emu(76200), fill=CYAN)
    add_text(s, Inches(0.9), Inches(0.8), Inches(5), Inches(0.5),
             brand_line, size=18, bold=True, color=CYAN)
    add_text(s, Inches(0.9), Inches(3.7), Inches(11.5), Inches(1.5),
             title, size=40, bold=True, color=WHITE)
    if subtitle:
        add_text(s, Inches(0.9), Inches(5.6), Inches(11.5), Inches(0.5),
                 subtitle, size=18, color=WHITE)
    if meta:
        add_text(s, Inches(0.9), Inches(6.6), Inches(11.5), Inches(0.4),
                 meta, size=11, color=CYAN)
    return s


# ═════════════════════════════════════════════════════════
# 2. CONTENTS — 목차
# ═════════════════════════════════════════════════════════
def slide_contents(deck: Deck, *, sections: list, title: str = "Contents",
                   subtitle: str = "제안서 목차"):
    """
    sections: [(num, section_title, [(page, page_title), ...]), ...]
    최대 8개 섹션 권장 (2열 4행)
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle)

    col_x = [Inches(0.7), Inches(7.0)]
    row_y = [Inches(1.85), Inches(3.15), Inches(4.45), Inches(5.75)]
    positions = [(col_x[i % 2], row_y[i // 2]) for i in range(8)]

    for i, (num, section_title, pages) in enumerate(sections):
        if i >= len(positions):
            break
        x, y = positions[i]
        w, h = Inches(5.95), Inches(1.2)
        add_rect(s, x, y, w, h, fill=SECTION_BG, line=LIGHT_GRAY)
        add_rect(s, x, y, Inches(0.85), h, fill=NAVY)
        add_text(s, x, y, Inches(0.85), h, num, size=22, bold=True,
                 color=CYAN, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(1.0), y + Inches(0.15), w - Inches(1.1), Inches(0.35),
                 section_title, size=13, bold=True, color=NAVY)
        items = [f"p.{p}  {t}" for p, t in pages]
        add_bullets(s, x + Inches(1.0), y + Inches(0.55),
                    w - Inches(1.1), h - Inches(0.6), items,
                    size=10.5, color=GRAY, bullet="")
    return s


# ═════════════════════════════════════════════════════════
# 3. CARD 3COL — 3열 카드 (회사 개요, 솔루션 개요 등)
# ═════════════════════════════════════════════════════════
def slide_card_3col(deck: Deck, *, title: str, subtitle: str = "",
                    section_tag: str = "",
                    headline: str = "",
                    cards: list):
    """
    cards: [(card_title, [item, ...]), (card_title, [...]), (card_title, [...])]
    headline: 3열 위에 띄우는 강조 문장 (옵션)
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)

    y_cards = Inches(2.0)
    if headline:
        add_rect(s, Inches(0.7), Inches(1.95), Inches(11.9), Inches(0.85), fill=SECTION_BG)
        add_text(s, Inches(0.9), Inches(1.95), Inches(11.5), Inches(0.85),
                 headline, size=17, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        y_cards = Inches(3.1)

    cw = Inches(3.9); gap = Inches(0.15)
    ch = Inches(4.75) if not headline else Inches(3.75)
    x0 = Inches(0.7)
    for i, (ct, items) in enumerate(cards[:3]):
        card(s, x0 + (cw + gap) * i, y_cards, cw, ch, ct, items)
    return s


# ═════════════════════════════════════════════════════════
# 4. CARD 2COL — 좌우 대칭 (기능 | 효과 등)
# ═════════════════════════════════════════════════════════
def slide_card_2col(deck: Deck, *, title: str, subtitle: str = "",
                    section_tag: str = "",
                    left: tuple, right: tuple):
    """left, right: (card_title, [items, ...])"""
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)
    card(s, Inches(0.7), Inches(2.1), Inches(6.0), Inches(4.75),
         left[0], left[1])
    card(s, Inches(6.75), Inches(2.1), Inches(5.95), Inches(4.75),
         right[0], right[1])
    return s


# ═════════════════════════════════════════════════════════
# 5. KPI 3 — 3개 KPI 박스 (정량 효과)
# ═════════════════════════════════════════════════════════
def slide_kpi_3(deck: Deck, *, title: str, subtitle: str = "",
                section_tag: str = "",
                kpis: list, bottom_table: list = None):
    """
    kpis: [(big_number, unit, label, accent_color_name), ...] × 3
        accent_color_name ∈ {"green", "cyan", "red"} (기본 cyan)
    bottom_table: [headers, row1, row2, ...] 옵션 (AS-IS vs TO-BE 등)
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)

    color_map = {"green": ACCENT_GREEN, "cyan": CYAN, "red": ACCENT_RED}
    y = Inches(2.1); w = Inches(3.9); h = Inches(3.1)
    xs = [Inches(0.7), Inches(4.75), Inches(8.8)]
    for i, (big, unit, lab, *rest) in enumerate(kpis[:3]):
        acc = color_map.get(rest[0] if rest else "cyan", CYAN)
        kpi_box(s, xs[i], y, w, h, big, unit, lab, accent=acc)

    if bottom_table:
        y2 = Inches(5.45)
        add_rect(s, Inches(0.7), y2, Inches(11.9), Inches(1.55),
                 fill=SECTION_BG, line=LIGHT_GRAY)
        headers, *rows = bottom_table
        n = len(headers)
        # 균등 분할 좌표 (간단)
        col_w_total = Inches(11.5)
        col_w_each = Inches(11.5 / n)
        col_x_start = Inches(0.9)
        yy = y2 + Inches(0.1)
        add_text(s, Inches(0.9), yy, Inches(11.5), Inches(0.35),
                 "AS-IS → TO-BE", size=13, bold=True, color=NAVY)
        yy += Inches(0.4)
        for i, h_cell in enumerate(headers):
            add_text(s, col_x_start + col_w_each * i, yy, col_w_each, Inches(0.3),
                     h_cell, size=11, bold=True, color=CYAN)
        yy += Inches(0.32)
        for row in rows:
            for i, cell in enumerate(row):
                add_text(s, col_x_start + col_w_each * i, yy, col_w_each, Inches(0.3),
                         cell, size=11, color=DARK)
            yy += Inches(0.28)
    return s


# ═════════════════════════════════════════════════════════
# 6. MATRIX — 매트릭스 (Fit Matrix 등)
# ═════════════════════════════════════════════════════════
def slide_matrix(deck: Deck, *, title: str, subtitle: str = "",
                 section_tag: str = "",
                 row_label_header: str = "",
                 col_labels: list, row_labels: list,
                 matrix: list,
                 legend: str = "●  직접       ◐  간접       ○  미해당",
                 conclusion: str = ""):
    """
    matrix: [[val, val, ...], ...] — row × col, 값은 "●"/"◐"/"○"
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)

    # 범례
    add_text(s, Inches(7.8), Inches(1.95), Inches(4.8), Inches(0.3),
             legend, size=11, color=GRAY, align=PP_ALIGN.RIGHT)

    table_x = Inches(0.7); table_y = Inches(2.4)
    label_w = Inches(2.5)
    n_cols = len(col_labels)
    cell_w = Inches((13.333 - 0.7 - 0.7 - 2.5) / max(n_cols, 1))
    header_h = Inches(0.75); row_h = Inches(0.58)

    # 좌상단
    add_rect(s, table_x, table_y, label_w, header_h, fill=NAVY)
    add_text(s, table_x, table_y, label_w, header_h, row_label_header,
             size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # 상단 헤더
    for j, col in enumerate(col_labels):
        x = table_x + label_w + cell_w * j
        add_rect(s, x, table_y, cell_w, header_h, fill=NAVY, line=WHITE)
        add_text(s, x, table_y, cell_w, header_h, col,
                 size=10, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # 본문
    for i, label in enumerate(row_labels):
        y = table_y + header_h + row_h * i
        fill = SECTION_BG if i % 2 == 0 else WHITE
        add_rect(s, table_x, y, label_w, row_h, fill=fill, line=LIGHT_GRAY)
        add_text(s, table_x + Inches(0.2), y, label_w - Inches(0.25), row_h, label,
                 size=11, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE)
        for j, val in enumerate(matrix[i]):
            x = table_x + label_w + cell_w * j
            add_rect(s, x, y, cell_w, row_h, fill=fill, line=LIGHT_GRAY)
            color = NAVY if val == "●" else (CYAN if val == "◐" else GRAY)
            add_text(s, x, y, cell_w, row_h, val,
                     size=18, bold=True, color=color,
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    if conclusion:
        concl_y = Inches(6.4)
        add_rect(s, Inches(0.7), concl_y, Inches(11.9), Inches(0.65), fill=NAVY)
        add_text(s, Inches(0.9), concl_y, Inches(11.5), Inches(0.65),
                 conclusion, size=11, bold=True, color=WHITE,
                 anchor=MSO_ANCHOR.MIDDLE)
    return s


# ═════════════════════════════════════════════════════════
# 7. TIMELINE — 성장 로드맵 가로 타임라인
# ═════════════════════════════════════════════════════════
def slide_timeline(deck: Deck, *, title: str, subtitle: str = "",
                   section_tag: str = "",
                   top_grid: list = None,
                   timeline_title: str = "성장 로드맵",
                   stages: list):
    """
    top_grid: [(badge, header, body), ...] 최대 7개 (위 그리드 카드)
    stages: [(year, label), ...] 하단 타임라인
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)

    y_road_start = Inches(2.1)
    if top_grid:
        # 4×2 그리드
        add_text(s, Inches(0.7), Inches(1.95), Inches(11.9), Inches(0.3),
                 "", size=13, bold=True, color=NAVY)
        x0 = Inches(0.7); y0 = Inches(2.3)
        cw = Inches(2.95); ch = Inches(1.4); gap = Inches(0.1)
        for i, (badge, name, desc) in enumerate(top_grid[:8]):
            col = i % 4; row = i // 4
            x = x0 + (cw + gap) * col
            y = y0 + (ch + gap) * row
            add_rect(s, x, y, cw, ch, fill=WHITE, line=LIGHT_GRAY)
            add_rect(s, x, y, Inches(0.6), ch, fill=CYAN)
            add_text(s, x, y, Inches(0.6), ch, badge,
                     size=13, bold=True, color=WHITE,
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            add_text(s, x + Inches(0.75), y + Inches(0.2), cw - Inches(0.9), Inches(0.45),
                     name, size=14, bold=True, color=NAVY)
            add_text(s, x + Inches(0.75), y + Inches(0.7), cw - Inches(0.9), Inches(0.6),
                     desc, size=11, color=GRAY)
        y_road_start = Inches(5.35)

    # 타임라인
    y_road = y_road_start
    add_rect(s, Inches(0.7), y_road, Inches(11.9), Inches(1.6),
             fill=SECTION_BG, line=LIGHT_GRAY)
    add_text(s, Inches(0.9), y_road + Inches(0.1), Inches(11.5), Inches(0.3),
             timeline_title, size=13, bold=True, color=NAVY)

    nx = len(stages)
    line_y = y_road + Inches(1.0)
    add_rect(s, Inches(1.2), line_y, Inches(10.9), Emu(25400), fill=GRAY)
    w_stage = Inches(10.9) / max(nx - 1, 1)
    for i, (year, label) in enumerate(stages):
        cx = Inches(1.2) + w_stage * i
        r = Inches(0.14)
        circle = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                    cx - r, line_y - r + Emu(12700),
                                    r * 2, r * 2)
        circle.shadow.inherit = False
        circle.fill.solid()
        circle.fill.fore_color.rgb = CYAN if i >= nx * 0.6 else NAVY
        circle.line.fill.background()
        add_text(s, cx - Inches(0.9), y_road + Inches(0.45), Inches(1.8), Inches(0.3),
                 year, size=11, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
        add_text(s, cx - Inches(1.0), line_y + Inches(0.2), Inches(2.0), Inches(0.3),
                 label, size=11, color=DARK, align=PP_ALIGN.CENTER)
    return s


# ═════════════════════════════════════════════════════════
# 8. PHASES — 단계별 카드 (POC → 파일럿 → 롤아웃)
# ═════════════════════════════════════════════════════════
def slide_phases(deck: Deck, *, title: str, subtitle: str = "",
                 section_tag: str = "",
                 phases: list):
    """
    phases: [(tag, title, [items, ...]), ...] 보통 3개
    """
    s = deck.add_slide()
    page_frame(deck, s, title, subtitle, section_tag=section_tag)

    n = len(phases)
    x0 = Inches(0.7); y = Inches(2.15)
    w = Inches(11.9 / n - 0.1); h = Inches(4.7)
    gap = Inches(0.1)
    for i, (tag, ph_title, items) in enumerate(phases):
        x = x0 + (w + gap) * i
        add_rect(s, x, y, w, h, fill=SECTION_BG, line=LIGHT_GRAY)
        add_rect(s, x, y, w, Inches(0.55),
                 fill=NAVY if i % 2 == 0 else CYAN)
        add_text(s, x, y, w, Inches(0.55), tag, size=13, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x + Inches(0.25), y + Inches(0.8), w - Inches(0.5), Inches(0.5),
                 ph_title, size=16, bold=True, color=NAVY)
        add_bullets(s, x + Inches(0.25), y + Inches(1.45),
                    w - Inches(0.5), h - Inches(1.6), items, size=12)
    return s


# ═════════════════════════════════════════════════════════
# 9. CLOSE — 종료 슬라이드 (Thank You + 컨택)
# ═════════════════════════════════════════════════════════
def slide_close(deck: Deck, *, headline: str = "Thank You",
                message: str = "함께 산업 현장의 미래를 만들어갑니다.",
                contacts_left: list = None,
                contacts_right: list = None):
    """contacts_*: [(label, value), ...]"""
    s = deck.add_slide()
    add_rect(s, 0, 0, deck.SW, deck.SH, fill=NAVY)
    add_rect(s, 0, Inches(3.3), deck.SW, Emu(76200), fill=CYAN)

    add_text(s, Inches(0.9), Inches(1.0), Inches(11.5), Inches(0.5),
             headline, size=20, bold=True, color=CYAN)
    add_text(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(1.2),
             message, size=32, bold=True, color=WHITE)

    def info_block(x, y, items):
        yy = y
        for k, v in items:
            add_text(s, x, yy, Inches(1.6), Inches(0.35),
                     k, size=11, bold=True, color=CYAN)
            add_text(s, x + Inches(1.6), yy, Inches(4.5), Inches(0.35),
                     v, size=13, color=WHITE)
            yy += Inches(0.5)

    if contacts_left:
        info_block(Inches(0.9), Inches(4.3), contacts_left)
    if contacts_right:
        info_block(Inches(7.0), Inches(4.3), contacts_right)
    return s


__all__ = [
    "slide_cover", "slide_contents",
    "slide_card_3col", "slide_card_2col",
    "slide_kpi_3", "slide_matrix",
    "slide_timeline", "slide_phases",
    "slide_close",
]
