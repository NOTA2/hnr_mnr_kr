# Translation Workspace

이 폴더는 현재까지 확보한 번역 작업 기준본을 모아 둔 작업 허브다.

## 핵심 파일

- [all_extracted_texts_master.json](/Users/user/test/analysis/translation_workspace/all_extracted_texts_master.json)
- [all_extracted_texts_manifest.json](/Users/user/test/analysis/translation_workspace/all_extracted_texts_manifest.json)
- [registry_a_entry8_clusters_manifest.json](/Users/user/test/analysis/translation_workspace/registry_a_entry8_clusters_manifest.json)
- [index.json](/Users/user/test/analysis/translation_workspace/index.json)

## 권장 시작 순서

1. [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json)
2. [translation_workset_gameplay_terms.json](/Users/user/test/analysis/translation_workset_gameplay_terms.json)
3. [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json)
4. [registry_a_entry8_clusters_manifest.json](/Users/user/test/analysis/translation_workspace/registry_a_entry8_clusters_manifest.json)

## 재생성

```bash
python3 scripts/build_translation_workspace.py
```
