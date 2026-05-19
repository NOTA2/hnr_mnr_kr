# Translation Workspace

이 폴더는 현재까지 확보한 번역 작업 기준본을 모아 둔 작업 허브다.

## 핵심 파일

- [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json)
- [all_extracted_texts_manifest.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_manifest.json)
- [extraction_audit_status.json](/Users/user/test/confirmed_data/translation_workspace/extraction_audit_status.json)
- [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)
- [index.json](/Users/user/test/confirmed_data/translation_workspace/index.json)
- [workset_metadata_index.json](/Users/user/test/confirmed_data/translation_workspace/workset_metadata_index.json)
- [workset_metadata_index.md](/Users/user/test/confirmed_data/translation_workspace/workset_metadata_index.md)
- [text_category_capability_matrix.md](/Users/user/test/confirmed_data/translation_workspace/text_category_capability_matrix.md)
- [entry8_runtime_stability_notes.md](/Users/user/test/confirmed_data/translation_workspace/entry8_runtime_stability_notes.md)

## 권장 시작 순서

1. [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json)
2. [translation_workset_gameplay_terms.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_gameplay_terms.json)
3. [translation_workset_registry_d_dialogue.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json)
4. [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json)

## 사용자 QA 안내

- [user_qa_guide.md](/Users/user/test/docs/user_qa_guide.md)

## 현재 안정 빌드 메모

- Entry8 structural segment repoint 는 메인 review ROM에서 비활성화한다.
- Entry8 은 현재 원본 슬롯/record 길이 보존 방식으로만 적용한다.
- 긴 Entry8 문장을 다시 허용하는 작업은 별도 실험 ROM과 runtime 검증을 통과한 뒤에만 재개한다.

## 재생성

```bash
python3 scripts/build_translation_workspace.py
```
