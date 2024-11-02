# ✨ Django Meilisearch Indexer ✨

![Code quality](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/code_quality.yml/badge.svg?branch=main)
![Tests](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/tests.yml/badge.svg?branch=main)
![Build](https://github.com/Jordan-Kowal/django-meilisearch-indexer/actions/workflows/publish_package.yml/badge.svg?event=release)
![Coverage](https://badgen.net/badge/coverage/%3E90%25/pink)
![Tag](https://badgen.net/badge/tag/1.0.1/orange)
![Python](https://badgen.net/badge/python/3.9%20|%203.10%20|%203.11%20|%203.12|%203.13)
![Licence](https://badgen.net/badge/licence/MIT)

- [✨ Django Meilisearch Indexer ✨](#-django-meilisearch-indexer-)
  - [💻 How to install](#-how-to-install)
  - [⚡ Quick start](#-quick-start)
  - [📕 Available modules](#-available-modules)
  - [🍜 Recipes](#-recipes)
    - [Create indexes on boot](#create-indexes-on-boot)
    - [Async actions with celery](#async-actions-with-celery)
    - [Mock for testing](#mock-for-testing)
    - [Admin actions](#admin-actions)
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
from django_meilisearch_indexer.indexers import MeilisearchModelIndexer

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
from django_meilisearch_indexer.indexers import MeilisearchModelIndexer

# Some serializers for your API
from django_meilisearch_indexer.serializers import (
    MeilisearchOnlyHitsResponseSerializer,
    MeilisearchSearchResultsSerializer,
    MeilisearchSimpleSearchSerializer,
)

# Lots of typing classes
from django_meilisearch_indexer.types import (
    Faceting,
    MeilisearchFilters,
    MeilisearchFilterValue,
    MeilisearchSearchHits,
    MeilisearchSearchParameters,
    MeilisearchSearchResults,
    MeilisearchSettings,
    MinWordSizeForTypos,
    Pagination,
    Precision,
    RankingRule,
    TypoTolerance,
)
```

## 🍜 Recipes

### Create indexes on boot

Generate your indexes on boot using `AppConfig.ready()`.

```python
class TagConfig(AppConfig):
    name = "tags"

    def ready(self) -> None:
        from django.conf import settings
        from tags.indexers import TagIndexer

        if settings.IS_RUNNING_MYPY or settings.ENVIRONMENT == "test":
            return

        TagIndexer.maybe_create_index()
```

### Async actions with celery

Make your indexation asynchronous using `celery` and `rabbitmq`.

```python
from typing import Dict, List
from celery import shared_task
from django.conf import settings
from django.db.models import Q

@shared_task(queue=settings.RABBITMQ_USER_QUEUE)
def index_tags(ids: List[int]) -> Dict[str, str]:
    from tags.indexers import TagIndexer

    TagIndexer.index_from_query(Q(pk__in=ids))
    return {"result": "ok"}

# ...
index_tags.s(ids).apply_async(countdown=5)
```

### Mock for testing

For testing, you'll need to mock the following tasks:

```python
from unittest import TestCase
from unittest.mock import patch

class TagTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._mock_indexers()
        self._mock_celery_tasks()

    def _mock_indexers(self) -> None:
        """
        Patches the `index_name` functions of all indexers.
        This allows running tests against a Meilisearch server
        without overwriting the actual index.
        """
        self.indexer_mocks = [
            patch(
                "tags.indexers.TagIndexer.index_name",
                return_value="test_tags",
            ).start(),
        ]

    # If you are using celery tasks
    def _mock_celery_tasks(self) -> None:
        """Patches the celery tasks in both forms: `delay` and `apply_async`."""
        names = [
            "tags.tasks.index_tags.delay",
            "tags.tasks.index_tags.apply_async",
        ]
        self.celery_task_mocks = {name: patch(name).start() for name in names}

    def test_something(self):
        # ...
        self.celery_task_mocks[
            "tags.tasks.index_tags.apply_async"
        ].assert_called_once_with(([recipe.id],), {}, countdown=5)
        # ...
```

### Admin actions

To trigger your indexations through the django admin interface,
you can add a custom action like so:

```python
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from tags import tasks
from tags.models import Tag

@admin.action(description="[Meilisearch] Index selected item(s)")
def index_multiple(
    model_admin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> HttpResponseRedirect:
    ids = list(queryset.values_list("id", flat=True))
    model_admin.index_task.s(ids).apply_async(countdown=5)
    model_admin.message_user(request, f"Indexing {len(ids)} items(s) on Meilisearch")
    return HttpResponseRedirect(request.get_full_path())


class TagAdmin(admin.ModelAdmin):
    index_task = tasks.index_tags
    extra_actions = [index_multiple]
    # ...
```

## 🔗 Useful links

- [Want to contribute?](CONTRIBUTING.md)
- [See what's new!](CHANGELOG.md)
