from time import sleep
from typing import Any, Dict, List
from unittest import TestCase

import django
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.db.models import Q
from meilisearch import Client

from django_meilisearch_indexer.model_indexer import MeilisearchModelIndexer
from django_meilisearch_indexer.types import (
    MeilisearchSearchHits,
    MeilisearchSearchResults,
)

# --------------------------------------------------
# Django setup
# --------------------------------------------------
settings.configure(
    INSTALLED_APPS=[
        "django_meilisearch_indexer.tests",
    ],
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    DEFAULT_AUTO_FIELD="django.db.models.AutoField",
    MEILISEARCH_HOST="http://localhost:7700",
    MEILISEARCH_API_KEY="nje#_zn0wfh49m9_&8sd10cr&i51^na3fn61fkdbs*ol21doz(",
)
django.setup()


# --------------------------------------------------
# App setup
# --------------------------------------------------
class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    is_active = models.BooleanField()
    age = models.IntegerField()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        app_label = "tests"


class UserIndexer(MeilisearchModelIndexer[User]):
    MODEL_CLASS = User
    PRIMARY_KEY = "id"
    SETTINGS = {
        "filterableAttributes": ["is_active"],
        "searchableAttributes": ["full_name"],
        "sortableAttributes": ["age"],
    }

    @classmethod
    def build_object(cls, instance: User) -> Dict[str, Any]:
        return {
            "id": instance.id,
            "full_name": instance.full_name,
            "is_active": instance.is_active,
            "age": instance.age,
        }

    @classmethod
    def index_name(cls) -> str:
        return "test_users"


# --------------------------------------------------
# Tests
# --------------------------------------------------
SLEEP_TIME = 0.1


class UserIndexerTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.meilisearch_client = Client(
            settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY
        )
        cls.user_1 = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="a@a.com",
            is_active=True,
            age=30,
        )
        cls.user_2 = User.objects.create(
            first_name="Jane",
            last_name="Doe",
            email="b@b.com",
            is_active=False,
            age=25,
        )
        return super().setUpClass()

    def setUp(self) -> None:
        super().setUp()
        self.meilisearch_client.delete_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)

    def tearDown(self) -> None:
        self.meilisearch_client.delete_index(UserIndexer.index_name())
        super().tearDown()

    def test_index_exists(self) -> None:
        self.assertFalse(UserIndexer.index_exists())
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        self.assertTrue(UserIndexer.index_exists())

    def test_maybe_create_index(self) -> None:
        self.assertFalse(UserIndexer.index_exists())
        UserIndexer.maybe_create_index()
        sleep(SLEEP_TIME)
        self.assertTrue(UserIndexer.index_exists())

    def test_update_settings(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        UserIndexer.update_settings()
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(
            UserIndexer.index_name()
        ).get_settings()
        for key, value in UserIndexer.SETTINGS.items():
            self.assertEqual(response[key], value)

    def test_index(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [])
        UserIndexer.index(self.user_1)
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [self.user_1])

    def test_index_multiple(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [])
        UserIndexer.index_multiple([self.user_1, self.user_2])
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [self.user_1, self.user_2])

    def test_index_from_query(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [])
        UserIndexer.index_from_query(Q(id=self.user_1.id))
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [self.user_1])

    def test_index_all(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [])
        UserIndexer.index_all()
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [self.user_1, self.user_2])

    def test_index_all_atomically(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertEqual(response["hits"], [])
        UserIndexer.index_all_atomically()
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [self.user_1, self.user_2])

    def test_unindex(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        UserIndexer.index(self.user_1)
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [self.user_1])
        UserIndexer.unindex(self.user_1.id)
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search(
            self.user_1.full_name
        )
        self.assertSearchHits(response, [])

    def test_unindex_multiple(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        sleep(SLEEP_TIME)
        UserIndexer.index_multiple([self.user_1, self.user_2])
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [self.user_1, self.user_2])
        UserIndexer.unindex_multiple([self.user_1.id, self.user_2.id])
        sleep(SLEEP_TIME)
        response = self.meilisearch_client.index(UserIndexer.index_name()).search("")
        self.assertSearchHits(response, [])

    def test_search(self) -> None:
        self.meilisearch_client.create_index(UserIndexer.index_name())
        search_value = self.user_1.full_name
        sleep(SLEEP_TIME)
        response = UserIndexer.search(search_value)
        self.assertSearchHits(response, [])
        UserIndexer.index(self.user_1)
        sleep(SLEEP_TIME)
        response = UserIndexer.search(search_value)
        self.assertSearchHits(response, [self.user_1])
        self.assertEqual(response.get("limit"), 20)
        response = UserIndexer.search(search_value, limit=1)
        self.assertSearchHits(response, [self.user_1])
        self.assertEqual(response.get("limit"), 1)
        response = UserIndexer.search(search_value, only_hits=True, limit=1)
        self.assertSearchHits(response, [self.user_1])
        self.assertNotIn("limit", response)

    def test_meilisearch_client(self) -> None:
        self.assertIsInstance(UserIndexer.meilisearch_client(), Client)

    def assertSearchHits(
        self,
        response: MeilisearchSearchHits | MeilisearchSearchResults,
        items: List[User],
    ) -> None:
        ids = {hit["id"] for hit in response["hits"]}
        self.assertSetEqual(
            ids, {getattr(item, UserIndexer.PRIMARY_KEY) for item in items}
        )


# --------------------------------------------------
# Django migrations
# --------------------------------------------------
call_command("makemigrations", "tests")
call_command("migrate")
