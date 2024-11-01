# ✨ Django Meilisearch Indexer ✨

![Code quality](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/code_quality.yml/badge.svg?branch=main)
![Tests](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/tests.yml/badge.svg?branch=main)
![Build](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/publish_package.yml/badge.svg?event=release)
![Coverage](https://badgen.net/badge/coverage/%3E90%25/pink)
![Tag](https://badgen.net/badge/tag/1.0.0/orange)
![Python](https://badgen.net/badge/python/3.9%20|%203.10%20|%203.11%20|%203.12)
![Licence](https://badgen.net/badge/licence/MIT)

- [✨ Django Meilisearch Indexer ✨](#-django-meilisearch-indexer-)
  - [💻 How to install](#-how-to-install)
  - [⚡ Quick start](#-quick-start)
  - [📕 Available modules](#-available-modules)
  - [🍜 Recipes](#-recipes)
    - [Create index on boot](#create-index-on-boot)
    - [Async actions with celery](#async-actions-with-celery)
    - [Mock for testing](#mock-for-testing)
  - [🔗 Useful links](#-useful-links)

Provides a `MeilisearchModelIndexer` class to easily index django models in Meilisearch.

## 💻 How to install

The package is available on PyPi with the name `django_meilisearch_indexer`.
Simply run:

```shell
pip install django_meilisearch_indexer
```

## ⚡ Quick start

Here's a basic example:

```python
# Imports
from typing import Any, Dict
from django.db import models
from django_meilisearch_indexer import MeilisearchModelIndexer

# Model
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=100)
    is_disabled = models.BooleanField(default=False)

# Indexer
class TagIndexer(MeilisearchModelIndexer[Tag]):
    MODEL_CLASS = Tag
    PRIMARY_KEY = "id"
    SETTINGS = {
        "filterableAttributes": ["is_disabled"],
        "searchableAttributes": ["name"],
        "sortableAttributes": ["name", "color"],
    }

    @classmethod
    def build_object(cls, instance: Tag) -> Dict[str, Any]:
        return {
            "id": instance.id,
            "name": instance.name,
            "color": instance.color,
            "is_disabled": instance.is_disabled,
        }

    @classmethod
    def index_name(cls) -> str:
        return "tags"

# Call
TagIndexer.maybe_create_index()
```

## 📕 Available modules

This library contains the following importable modules:

```python
# The main indexer
MeilisearchModelIndexer

# Some serializers for your API
MeilisearchOnlyHitsResponseSerializer
MeilisearchSearchResultsSerializer
MeilisearchSimpleSearchSerializer

# Lots of typing classes
Faceting
MeilisearchFilters
MeilisearchFilterValue
MeilisearchSearchHits
MeilisearchSearchParameters
MeilisearchSearchResults
MeilisearchSettings
MinWordSizeForTypos
Pagination
Precision
RankingRule
TypoTolerance
```

## 🍜 Recipes

### Create index on boot

### Async actions with celery

### Mock for testing

## 🔗 Useful links

- [Want to contribute?](CONTRIBUTING.md)
- [See what's new!](CHANGELOG.md)
