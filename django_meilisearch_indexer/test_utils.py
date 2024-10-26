from time import sleep
from typing import Dict, Generic, List, Type, TypeVar

from django.db.models import Model, Q
from django.test import tag
from meilisearch import Client

from django_meilisearch_indexer.indexer import MeilisearchModelIndexer

M = TypeVar("M", bound=Model)


@tag("integration")
class IndexerBaseTestMixin(Generic[M]):
    """
    Base test mixin for testing MeilisearchModelIndexer subclasses.

    Make sure `index_name` is mocked in the setUp method.

    Provides tests for all methods from MeilisearchModelIndexer
    except `build_object` and `index_name`.
    """

    meilisearch_client: Client

    indexer_class: Type[MeilisearchModelIndexer]
    item_1: M
    item_2: M
    search_attribute: str
    sleep_time: float = 0.1

    def setUp(self) -> None:
        super().setUp()  # type: ignore
        self.meilisearch_client.delete_index(self.indexer_class.index_name())
        sleep(self.sleep_time)

    def tearDown(self) -> None:
        self.meilisearch_client.delete_index(self.indexer_class.index_name())
        super().tearDown()  # type: ignore

    def test_index_exists(self) -> None:
        self.assertFalse(self.indexer_class.index_exists())
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        self.assertTrue(self.indexer_class.index_exists())

    def test_maybe_create_index(self) -> None:
        self.assertFalse(self.indexer_class.index_exists())
        self.indexer_class.maybe_create_index()
        sleep(self.sleep_time)
        self.assertTrue(self.indexer_class.index_exists())

    def test_update_settings(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        self.indexer_class.update_settings()
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).get_settings()
        for key, value in self.indexer_class.SETTINGS.items():
            self.assertEqual(response[key], value)

    def test_index(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [])
        self.indexer_class.index(self.item_1)
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [self.item_1])

    def test_index_multiple(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [])
        self.indexer_class.index_multiple([self.item_1, self.item_2])
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [self.item_1, self.item_2])

    def test_index_from_query(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [])
        self.indexer_class.index_from_query(Q(id=self.item_1.id))
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [self.item_1])

    def test_index_all(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [])
        self.indexer_class.index_all()
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [self.item_1, self.item_2])

    def test_index_all_atomically(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertEqual(response["hits"], [])
        self.indexer_class.index_all_atomically()
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [self.item_1, self.item_2])

    def test_unindex(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        self.indexer_class.index(self.item_1)
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [self.item_1])
        self.indexer_class.unindex(self.item_1.id)
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search(getattr(self.item_1, self.search_attribute))
        self.assertSearchHits(response, [])

    def test_unindex_multiple(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        sleep(self.sleep_time)
        self.indexer_class.index_multiple([self.item_1, self.item_2])
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [self.item_1, self.item_2])
        self.indexer_class.unindex_multiple([self.item_1.id, self.item_2.id])
        sleep(self.sleep_time)
        response = self.meilisearch_client.index(
            self.indexer_class.index_name()
        ).search("")
        self.assertSearchHits(response, [])

    def test_search(self) -> None:
        self.meilisearch_client.create_index(self.indexer_class.index_name())
        search_value = getattr(self.item_1, self.search_attribute)
        sleep(self.sleep_time)
        response = self.indexer_class.search(search_value)
        self.assertSearchHits(response, [])  # type: ignore
        self.indexer_class.index(self.item_1)
        sleep(self.sleep_time)
        response = self.indexer_class.search(search_value)
        self.assertSearchHits(response, [self.item_1])  # type: ignore
        self.assertEqual(response.get("limit"), 20)
        response = self.indexer_class.search(search_value, limit=1)
        self.assertSearchHits(response, [self.item_1])  # type: ignore
        self.assertEqual(response.get("limit"), 1)
        response = self.indexer_class.search(search_value, only_hits=True, limit=1)
        self.assertSearchHits(response, [self.item_1])  # type: ignore
        self.assertNotIn("limit", response)

    def test_meilisearch_client(self) -> None:
        self.assertIsInstance(self.indexer_class.meilisearch_client(), Client)

    def assertSearchHits(self, response: Dict, items: List[M]) -> None:
        ids = {hit["id"] for hit in response["hits"]}
        self.assertSetEqual(
            ids, {getattr(item, self.indexer_class.PRIMARY_KEY) for item in items}
        )
