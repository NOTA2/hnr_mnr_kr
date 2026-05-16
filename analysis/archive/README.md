# Analysis Archive

이 아래는 **현재 hot path 에서 직접 읽지 않는 증거 보관 구역**이다.

원칙:

- 삭제 대신 archive 로 내린다.
- 루트 `analysis/` 에 다시 올리는 경우는, 그 파일이 현재 작업에서 반복 참조될 때만이다.
- archive 파일은 필요할 때만 연다.

## 현재 구조

- raw 구조 분석 증거: [data_structure_raw](/Users/user/test/analysis/archive/data_structure_raw)

## 언제 archive 를 여는가

- 최신 요약 문서만으로 결론이 부족할 때
- 과거 구조 가설의 근거 바이트/디스어셈블리를 다시 확인해야 할 때
- 같은 실수를 반복하지 않기 위해 원증거를 재대조해야 할 때
