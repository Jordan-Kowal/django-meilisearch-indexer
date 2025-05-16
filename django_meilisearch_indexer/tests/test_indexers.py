from time import sleep
from typing import Any, Dict, List, Union
from unittest import TestCase

import django
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.db.models import Q
from meilisearch import Client

from django_meilisearch_indexer.indexers import MeilisearchModelIndexer
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
    MEILISEARCH_API_KEY="meilisearch_local_master_key",
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
            "id": instance.id,  # ty: ignore
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
        cls.user_1 = User.objects.create(  # ty: ignore
            first_name="John",
            last_name="Doe",
            email="a@a.com",
            is_active=True,
            age=30,
        )
        cls.user_2 = User.objects.create(  # ty: ignore
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
        response: Union[MeilisearchSearchHits, MeilisearchSearchResults],
        items: List[User],
    ) -> None:
        ids = {hit["id"] for hit in response["hits"]}
        self.assertSetEqual(
            ids, {getattr(item, UserIndexer.PRIMARY_KEY) for item in items}
        )


class BuildSearchFilterTestCase(TestCase):
    def test_empty(self) -> None:
        self.assertEqual(UserIndexer._build_search_filter(), "")

    def test_is_empty(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(is_empty=["field_1", "field_2"]),
            "field_1 IS EMPTY AND field_2 IS EMPTY",
        )

    def test_is_not_empty(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(is_not_empty=["field_1", "field_2"]),
            "field_1 IS NOT EMPTY AND field_2 IS NOT EMPTY",
        )

    def test_is_null(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(is_null=["field_1", "field_2"]),
            "field_1 IS NULL AND field_2 IS NULL",
        )

    def test_is_not_null(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(is_not_null=["field_1", "field_2"]),
            "field_1 IS NOT NULL AND field_2 IS NOT NULL",
        )

    def test_one_of(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(
                one_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 IN [1, 2, 3] AND field_2 IN [a, b, c]",
        )

    def test_none_of(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(
                none_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 NOT IN [1, 2, 3] AND field_2 NOT IN [a, b, c]",
        )

    def test_all_of(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(
                all_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 = 1 AND field_1 = 2 AND field_1 = 3 AND field_2 = a AND field_2 = b AND field_2 = c",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(eq=[("field_1", 1), ("field_2", "a")]),
            "field_1 = 1 AND field_2 = a",
        )

    def test_neq(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(neq=[("field_1", 1), ("field_2", "a")]),
            "field_1 != 1 AND field_2 != a",
        )

    def test_gt(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(gt=[("field_1", 1), ("field_2", "a")]),
            "field_1 > 1 AND field_2 > a",
        )

    def test_gte(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(gte=[("field_1", 1), ("field_2", "a")]),
            "field_1 >= 1 AND field_2 >= a",
        )

    def test_lt(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(lt=[("field_1", 1), ("field_2", "a")]),
            "field_1 < 1 AND field_2 < a",
        )

    def test_lte(self) -> None:
        self.assertEqual(
            UserIndexer._build_search_filter(lte=[("field_1", 1), ("field_2", "a")]),
            "field_1 <= 1 AND field_2 <= a",
        )

    def test_complex(self) -> None:
        result = UserIndexer._build_search_filter(
            is_empty=["field_1"],
            is_not_empty=["field_2"],
            is_null=["field_3"],
            is_not_null=["field_4"],
            one_of=[("field_5", [1, 2, 3])],
            none_of=[("field_6", [4, 5, 6])],
            all_of=[("field_7", [7, 8, 9])],
            eq=[("field_10", 10)],
            neq=[("field_11", 11)],
            gt=[("field_12", 12)],
            gte=[("field_13", 13)],
            lt=[("field_14", 14)],
            lte=[("field_15", 15)],
        )
        self.assertEqual(
            result,
            "field_1 IS EMPTY "
            + "AND field_2 IS NOT EMPTY "
            + "AND field_3 IS NULL "
            + "AND field_4 IS NOT NULL "
            + "AND field_5 IN [1, 2, 3] "
            + "AND field_6 NOT IN [4, 5, 6] "
            + "AND field_7 = 7 "
            + "AND field_7 = 8 "
            + "AND field_7 = 9 "
            + "AND field_10 = 10 "
            + "AND field_11 != 11 "
            + "AND field_12 > 12 "
            + "AND field_13 >= 13 "
            + "AND field_14 < 14 "
            + "AND field_15 <= 15",
        )


# --------------------------------------------------
# Django migrations
# --------------------------------------------------
call_command("makemigrations", "tests")
call_command("migrate")
