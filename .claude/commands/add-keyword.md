# 카테고리 키워드 추가

지출 자동 분류를 위한 CATEGORY_KEYWORDS에 새 키워드를 추가합니다.

사용법: /add-keyword [카테고리] [키워드1, 키워드2, ...]

1. index.html에서 `CATEGORY_KEYWORDS` 객체를 찾습니다
2. 해당 카테고리의 키워드 배열에 새 키워드를 추가합니다
3. 중복 키워드가 없는지 확인합니다
4. CLAUDE.md의 키워드 매핑도 함께 업데이트합니다
5. 변경사항을 커밋하고 푸시합니다

$ARGUMENTS
