# 번역팀 구성

이 폴더는 나중에 실제 번역/검수 에이전트를 돌릴 때 사용할 팀 문서를 프로젝트 안에 고정해 둔 곳이다.

## 포함 파일

- [fma_translation_team_common_final_v4_1.md](/Users/user/test/docs/translation_team/fma_translation_team_common_final_v4_1.md)
- [fma_translation_agent_final_v4_1.md](/Users/user/test/docs/translation_team/fma_translation_agent_final_v4_1.md)
- [fma_review_agent_final_v4_1.md](/Users/user/test/docs/translation_team/fma_review_agent_final_v4_1.md)

## 읽는 순서

### 번역 에이전트

1. [fma_translation_team_common_final_v4_1.md](/Users/user/test/docs/translation_team/fma_translation_team_common_final_v4_1.md)
2. [fma_translation_agent_final_v4_1.md](/Users/user/test/docs/translation_team/fma_translation_agent_final_v4_1.md)
3. [index.json](/Users/user/test/confirmed_data/translation_workspace/index.json)
4. 실제 작업 대상 workset JSON

### 검수 에이전트

1. [fma_translation_team_common_final_v4_1.md](/Users/user/test/docs/translation_team/fma_translation_team_common_final_v4_1.md)
2. [fma_review_agent_final_v4_1.md](/Users/user/test/docs/translation_team/fma_review_agent_final_v4_1.md)
3. [index.json](/Users/user/test/confirmed_data/translation_workspace/index.json)
4. 검수 대상 번역 JSON

## 현재 프로젝트 기준 작업 허브

- 전체 기준본: [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json)
- 전체 manifest: [all_extracted_texts_manifest.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_manifest.json)
- 작업 허브 인덱스: [index.json](/Users/user/test/confirmed_data/translation_workspace/index.json)
- 번역 시작 가능 상태 요약: [translation_readiness_report.md](/Users/user/test/confirmed_data/translation_workspace/translation_readiness_report.md)
- workset 메타데이터 인덱스: [workset_metadata_index.md](/Users/user/test/confirmed_data/translation_workspace/workset_metadata_index.md)
- Entry 8 cluster 인덱스: [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)
- 텍스트 성격 분류표: [text_taxonomy_manifest.json](/Users/user/test/confirmed_data/translation_workspace/text_taxonomy_manifest.json)
- 로컬라이제이션 작업대 안내: [localization_workbench.md](/Users/user/test/docs/localization_workbench.md)
- 로컬라이제이션 작업대 데이터: [workbench_dataset.json](/Users/user/test/confirmed_data/localization_workbench/workbench_dataset.json)

## 권장 작업 순서

1. [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json)
2. [translation_workset_gameplay_terms.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_gameplay_terms.json)
3. [translation_workset_registry_d_dialogue.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json)
4. [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)

## 번역팀 실전 사용 경로

1. 번역/검수 지침 문서를 읽는다.
2. [workset_metadata_index.md](/Users/user/test/confirmed_data/translation_workspace/workset_metadata_index.md) 에서 현재 workset 제약을 먼저 본다.
3. [localization_workbench.md](/Users/user/test/docs/localization_workbench.md) 기준으로 GUI 작업대를 연다.
4. 같은 파일명으로 계속 덮어써지는 리뷰 ROM [hnr_localization_review.gba](/Users/user/test/patched_roms/current_review/hnr_localization_review.gba) 으로 화면 확인을 반복한다.

### 작업대 시작 명령

```bash
python3 /Users/user/test/scripts/build_localization_workbench_dataset.py
python3 /Users/user/test/scripts/run_localization_workbench.py
```

### 에이전트 번역 반영 규칙

- 번역 에이전트 팀은 작업대 dataset 의 `translation` 과 `agent_draft` 를 구분해서 써야 한다.
- 사람이 아직 확정하지 않은 항목:
  - 에이전트는 `agent_draft` 를 채운다.
  - 필요하면 `agent_comment` 도 함께 남긴다.
- 사람이 `수동 잠금`을 켠 항목:
  - 에이전트는 `translation` 을 수정하지 않는다.
  - 대신 `agent_draft` 와 `agent_comment` 에 대안을 적는다.
- 사용자는 GUI에서 초안을 보고, 필요하면 `에이전트 초안 → 적용 번역` 버튼으로 옮긴 뒤 `수동 잠금`을 켤 수 있다.

## 화자 정보에 대한 현재 상태

- 현재 추출 JSON에는 `speaker`, `speaker_id` 같은 명시 필드가 없다.
- 대신 [confirmed_data/dialogue_metadata/README.md](/Users/user/test/confirmed_data/dialogue_metadata/README.md) 아래에 `dialogue_state_token` sidecar 를 둔다.
- `dialogue_state_token` 은 confirmed 화자명이 아니라, **같은 active portrait/state 후보를 묶는 객관적 제어 표식**이다.
- 빠르게 볼 요약본은 [dialogue_state_cluster_summary.md](/Users/user/test/confirmed_data/dialogue_metadata/dialogue_state_cluster_summary.md) 이다.
- runtime family 우선순위는 [runtime_family_focus_report.md](/Users/user/test/confirmed_data/text_layout/runtime_family_focus_report.md) 를 본다.
- high-priority dialogue runtime 상세는 [runtime_dialogue_family_report.md](/Users/user/test/confirmed_data/text_layout/runtime_dialogue_family_report.md) 를 본다.
- 따라서 "누구의 대사인지"는 **객관적 메타데이터로 확정된 상태가 아니다**.
- Entry 8의 `cluster_primary_tag`, `cluster_tags` 는 작업 보조용 자동 태그이며, 화자 정보로 취급하면 안 된다.
- 번역팀이 화자를 추정해서 말투를 조절해야 하는 경우가 생길 수는 있지만, 그건 반드시 **추정** 으로 취급해야 한다.

## 재생성

```bash
python3 /Users/user/test/scripts/build_translation_workspace.py
python3 /Users/user/test/scripts/build_text_taxonomy_manifest.py
python3 /Users/user/test/scripts/build_localization_workbench_dataset.py
```
