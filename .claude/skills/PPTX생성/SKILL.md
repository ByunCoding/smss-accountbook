---
name: PPTX생성
description: 와트 브랜드 디자인(IBM Carbon 기반)을 적용한 .pptx 파일을 생성한다. 제안서·회사소개서·내부보고·교육자료 등 용도별 템플릿 지원. "PPT 만들어줘", "슬라이드", "제안서 써줘", "회사소개 자료", ".pptx 필요", "프레젠테이션" 등 표현 시 자동 실행.
---

# PPTX 생성 스킬

> 와트의 정체성(화이트 여백 + IBM Blue 60 + 미니멀 엔터프라이즈)을 모든 PPTX에 일관 적용.

## 트리거 키워드
- PPT 만들어줘 / 슬라이드 만들어 / 프레젠테이션 / 발표 자료
- 제안서 써줘 / 회사소개 자료 / 내부 보고 슬라이드
- .pptx 생성 / 파워포인트 / PPT 초안

## 디자인 정체성 (고정)
- **색상**: IBM Blue 60 `#0F62FE` (단일 액센트) + Gray 100/70/20/10 + White
- **폰트**: 맑은 고딕 (IBM Plex Sans 한국어 대체)
- **철칙**: 0px radius · 그림자 없음 · 배경 컬러 레이어링 · 이모지 금지
- **근거**: `.claude/design_md/ibm/DESIGN.md` (IBM Carbon Design System)
- **와트 홈페이지 매칭**: www.wattsolution.co.kr 톤과 동일

## 워크플로우 (협업형)

### 1단계 — 방향 질문
사용자에게 확인:
- 용도 (제안서 / 회사소개 / 내부보고 / 기타)
- 분량 (대략 페이지 수)
- 핵심 메시지 1~3줄
- 고객 레퍼런스 공개 여부 (제안서인 경우)
- 저장 경로 (기본: `..private/제안서/[고객사]/` or `..private/PPT/[주제]/`)

### 2단계 — 구조 설계
용도별 기본 구조 제안 → 합의:
- **제안서** (14~16p): 표지·목차·회사·실적·통증·솔루션·적합·가치·효과·신뢰·협업·컨택
- **회사소개서** (8~10p): 표지·목차·회사·제품·실적·기술·컨택
- **내부보고** (5~7p): 표지·현황·분석·결론·액션

### 3단계 — 빌드 스크립트 생성
`watt_design.py` + `components.py` 임포트해서 `build_xxx.py` 작성:
```python
from watt_design import Deck, TOKENS
from components import slide_cover, slide_contents, slide_card_3col, ...

deck = Deck(total_pages=12)
slide_cover(deck, title=..., subtitle=..., tag=...)
slide_contents(deck, sections=[...])
# ... 필요한 컴포넌트 조합
deck.save("제안서.pptx")
```

### 4단계 — 실행·검증
1. 스크립트 실행 → .pptx 생성
2. 전체 슬라이드 텍스트 덤프로 교차 검증 (CLAUDE.md 검증 규칙)
3. Contents 매핑 ↔ 실제 페이지 번호 일치 확인
4. 사용자에게 확인 요청

## 파일 구조

```
.claude/skills/PPTX생성/
├── SKILL.md              이 파일
├── watt_design.py        디자인 토큰 + 공통 헬퍼 (add_rect, add_text, page_frame, card 등)
├── components.py         슬라이드 컴포넌트 (cover, contents, card_3col, kpi_3, matrix, timeline, close)
└── templates/
    ├── 제안서.py         제안서 템플릿 샘플 (build_pptx.py 구조 재사용)
    ├── 회사소개서.py     회사소개 템플릿
    └── 내부보고.py       간단 보고 템플릿
```

## 핵심 원칙

- **고정 디자인**: IBM Carbon 톤을 임의로 변경 금지 (브랜드 일관성)
- **상사 편집 전제**: 모든 요소 네이티브 PPT 객체 — 이미지 삽입 금지
- **자동 완결성**: 생성 후 build 스크립트·pptx·노트(.md) 3개 세트 자동 저장
- **검증 의무**: 저장 후 슬라이드 개수·Contents 매핑·페이지 번호 정합성 재확인 (CLAUDE.md 검증 규칙)

## 저장 구조

```
..private/제안서/[고객사]/
├── 제안서.pptx
├── build_pptx.py
└── 초안노트.md
```

내부 보고·회사소개는 `..private/PPT/[주제]/`에 동일 구조.

## 레퍼런스 구현
첫 구현 예시: `..private/제안서/코카콜라/build_pptx.py` (16p 제안서, IBM Carbon 적용, Value Chain 매트릭스 포함)
