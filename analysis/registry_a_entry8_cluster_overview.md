# Registry A Entry 8 Cluster Overview

대형 mixed script bank `0x6B594C..0x773248` 의 작업용 요약.

상세 전수 목록은 아래를 본다.

- [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json)
- [registry_a_entry8_cluster_catalog.md](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.md)
- [registry_a_entry8_cluster_tag_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_tag_summary.json)

## 핵심 판단

- entry `8` 은 단일 스토리 덩어리가 아니라, **여러 장면/도시/서브이벤트가 한 bank 안에 섞인 구조**다.
- `72`개 cluster 로 나누면 접근성이 크게 좋아진다.
- 자동 태그는 완벽한 장면 라벨이 아니라 **빠른 탐색용 힌트**로 써야 한다.

## 눈에 띄는 묶음

### 초반 리오르/코넬로 흐름 후보

- cluster `0..4`
- 근거:
  - `医者になりたいんだけど、`
  - `ごていねいにお出迎えかよ`
  - `あんたの嘘は`
  - `コーネロを追いかけないの？`
- 해석:
  - 리오르 초반 NPC / 코넬로 추적 / 초반 전투 대사 / 이동 제한 문구가 섞인 흐름 후보

### 은행/동부도시 초반 흐름 후보

- cluster `5..10`
- 근거:
  - `お預け入れですか？`
  - `あなたが銀行強盗さんですね？`
  - `猫ゲ～ット♪`
  - `この街に何かご用でも`
- 해석:
  - 은행 강도 / 동부도시 이동 / 고양이 관련 분기가 함께 보이는 초중반 이벤트 후보

### 센트럴/병원/에리시아/알 파츠 탐색 축

- cluster `11..17`
- 근거:
  - `相手は子供だ。`
  - `セントラルシティ　中央区画`
  - `あら、二人ともお久しぶりね`
  - `鋼の錬金術師殿、`
  - `ロイじゃねえか！`
- 해석:
  - 센트럴 시티, 병원, 에리시아, 알의 파츠/서류/회복 계열 탐색이 많이 섞인 구간

### 국가연금술사 시험/도시 후속 이벤트 축

- cluster `18..27`
- 근거:
  - `これより、`
  - `国家錬金術師資格試験を始める`
  - `さっき上でドカーンって`
  - `患者さんが元気に`
  - `鎧のパーツ？`
- 해석:
  - 국가연금술사 시험, 병원 후속, 파츠 수집/도서관 루머가 이어지는 구간 후보

### 후기 동부/군 관련 대형 이벤트 묶음 후보

- cluster `41`, `55`, `62`
- 근거:
  - `大佐ぁ。`
  - `誰を探してるんですか？`
  - `ダイムラーのヤツを`
  - `やっぱり「賢者の石」って`
- 해석:
  - 대령/군 인물, 추적 대상, 현자의 돌 루머가 섞인 중후반 이벤트 구간 후보

### 엔드게임/진행 허브 + 세이브 메뉴 혼합 구간

- cluster `71`
- 근거:
  - `このまま旅を続けるか？`
  - `フードショップのおじさんに`
  - `広場でなにかあるみたいだね`
- 해석:
  - 진행 유도, 도시별 대화, save/menu prompt 가 함께 뒤섞인 **후기 mixed hub** 후보
- 주의:
  - 이 cluster 는 `save_menu` 태그가 붙지만, **세이브 메뉴 전용 구간은 아니다.**
  - 실제로는 `0x772E00` 기준으로 일반 이벤트/진행 힌트 `228`건과 save/menu `12`건으로 분리할 수 있다.
  - 분리본:
    - [registry_a_entry8_cluster71_pre_save_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_pre_save_texts.json)
    - [registry_a_entry8_cluster71_save_segment_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_save_segment_texts.json)

## 지금 이 문서의 용도

- "entry `8` 전체"를 통째로 보는 대신, 우선 어느 cluster 가 어느 장면 축인지 빠르게 감 잡기
- 번역/검수/재삽입 단위를 cluster 기준으로 끊기
- 아직 미추출이 남았는지, 아니면 이미 추출했지만 장면 정리가 안 된 것인지 구분하기

## 다음 권장 작업

1. cluster `0..20` 정도까지는 수동으로 장면 라벨을 더 정밀하게 붙인다.
2. cluster `71` 안에서 save/menu prompt 와 일반 이벤트 대사를 다시 나눌지 검토한다.
3. 실제 플레이 흐름과 cluster index 를 대조해 "새 일본어가 나오면 어느 cluster 밖인지"를 기록한다.
