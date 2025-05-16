# Changelog

## Legend

- 🚀 Features
- ✨ Improvements
- 🐞 Bugfixes
- 🔧 Others

## TBD

- 🔧 Added `CODEOWNERS` file and removed reviewers from dependabot
- 🔧 Migrated from `mypy` to `ty` for our type checker

## 1.0.3 - 2025-04-18

- 🔧 Removed `update_deps` action
- 🔧 Added `dependabot` config for `uv` deps updates
- 🔧 Updated CI to use python 3.13
- 🔧 Upgraded deps

## 1.0.2 - 2024-12-31

- 🐞 Fixed the workflow to publish the package as PyPi no longer supports username auth
- 🔧 Upgraded production and development deps

## 1.0.1 - 2024-11-02

- ✨ Official support for Python `3.13`
- 🐞 No longer imports everything at the first level. Instead, use `indexers`, `serializers`, and `types` submodules
- 🔧 `build_search_filter` standalone function has been replaced with `MeilisearchModelIndexer._build_search_filter` classmethod

## 1.0.0 - 2024-11-02

✨ Official release of the `django_meilisearch_indexer` library ✨
