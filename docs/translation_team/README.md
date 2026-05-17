# Translation Team Setup

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
- Entry 8 cluster 인덱스: [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)
- 텍스트 성격 분류표: [text_taxonomy_manifest.json](/Users/user/test/confirmed_data/translation_workspace/text_taxonomy_manifest.json)

## 권장 작업 순서

1. [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json)
2. [translation_workset_gameplay_terms.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_gameplay_terms.json)
3. [translation_workset_registry_d_dialogue.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json)
4. [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)

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
```
