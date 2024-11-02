from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from meilisearch import Client
from typing_extensions import Unpack

from django_meilisearch_indexer.types import (
    MeilisearchFilters,
    MeilisearchFilterValue,
    MeilisearchSearchHits,
    MeilisearchSearchParameters,
    MeilisearchSearchResults,
    MeilisearchSettings,
)

if TYPE_CHECKING:
    from django.db.models import Model


M = TypeVar("M", bound="Model")


class MeilisearchModelIndexer(ABC, Generic[M]):
    _meilisearch_client: Optional[Client] = None

    MODEL_CLASS: Type[M]
    PRIMARY_KEY = "id"
    SETTINGS: MeilisearchSettings

    @classmethod
    @abstractmethod
    def build_object(cls, instance: M) -> Dict[str, Any]:
        """
        Required. Should return the object to be indexed.

        Args:
            instance (M): A model instance

        Returns:
            Dict[str, Any]: A dictionary representing the object to be indexed
        """

    @classmethod
    @abstractmethod
    def index_name(cls) -> str:
        """
        Required. Should return the name of the index.

        Returns:
            str: The name of the index
        """

    # --------------------------------------------------
    # Index management
    # --------------------------------------------------
    @classmethod
    def index_exists(cls) -> bool:
        """Indicates whether the index exists or not."""
        try:
            cls.meilisearch_client().get_index(cls.index_name())
            return True
        except Exception:  # noqa
            return False

    @classmethod
    def maybe_create_index(cls) -> None:
        """Creates the index if it doesn't exist."""
        client = cls.meilisearch_client()
        if not cls.index_exists():
            client.create_index(cls.index_name(), {"primaryKey": cls.PRIMARY_KEY})
        cls.update_settings()

    @classmethod
    def update_settings(cls) -> None:
        """Updates the index settings."""
        cls.meilisearch_client().index(cls.index_name()).update_settings(cls.SETTINGS)  # type: ignore

    # --------------------------------------------------
    # Indexing
    # --------------------------------------------------
    @classmethod
    def index(cls, instance: M) -> None:
        """Builds and indexes a single model instance."""
        cls.index_multiple([instance])

    @classmethod
    def index_multiple(cls, instances: Union[List[M], QuerySet[M]]) -> None:
        """Builds and indexes multiple model instances."""
        objects = [cls.build_object(instance) for instance in instances]
        cls.meilisearch_client().index(cls.index_name()).add_documents(objects)

    @classmethod
    def index_from_query(cls, query: Q) -> None:
        """Builds and indexes all the instances of the model matching the query."""
        cls._index_from_query(query, cls.index_name())

    @classmethod
    def index_all(cls) -> None:
        """Builds and indexes all the instances of the model."""
        cls._index_from_query(Q(), cls.index_name())

    @classmethod
    def index_all_atomically(cls) -> None:
        """
        Builds and indexes all the instances of the model atomically.
        It will build another index and swap it with the current one once it's ready.
        """
        client = cls.meilisearch_client()
        # Create temporary index
        tmp_index_name = f"{cls.index_name()}_tmp"
        client.create_index(tmp_index_name, {"primaryKey": cls.PRIMARY_KEY})
        client.index(tmp_index_name).update_settings(cls.SETTINGS)  # type: ignore
        # Index all objects on it
        cls._index_from_query(Q(), tmp_index_name)
        # Swap indexes and cleanup
        client.swap_indexes([{"indexes": [cls.index_name(), tmp_index_name]}])
        client.delete_index(tmp_index_name)

    @classmethod
    def unindex(cls, id_: int) -> None:
        """Deletes from the index the object corresponding to the given id."""
        cls.unindex_multiple([id_])

    @classmethod
    def unindex_multiple(cls, ids: Union[List[int], List[str]]) -> None:
        """Deletes from the index the objects corresponding to the given ids."""
        cls.meilisearch_client().index(cls.index_name()).delete_documents(ids)

    # --------------------------------------------------
    # Searching
    # --------------------------------------------------
    @classmethod
    def search(
        cls,
        query: str = "",
        only_hits: bool = False,
        filters: MeilisearchFilters = None,
        **params: Unpack[MeilisearchSearchParameters],
    ) -> Union[MeilisearchSearchHits, MeilisearchSearchResults]:
        """
        Performs a search on the index with the given query and filters.

        Args:
            query (str): The text to search in the searchable fields. Defaults to "".
            only_hits (bool, optional): Whether to return only the hits. Defaults to False.
            filters (MeilisearchFilters, optional): The various extra filters to apply. Defaults to None.

        Returns:
            Union[MeilisearchSearchHits, MeilisearchSearchResults]: Either the complete results or only the hits.
        """
        filters = filters or {}
        params["filter"] = cls._build_search_filter(**filters) or None
        response: MeilisearchSearchResults = (
            cls.meilisearch_client().index(cls.index_name()).search(query, params)  # type: ignore
        )
        if only_hits:
            return {"hits": response["hits"]}
        return response

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    @classmethod
    def meilisearch_client(cls) -> Client:
        """Returns the Meilisearch client. Cached property."""
        if cls._meilisearch_client is None:
            cls._meilisearch_client = Client(
                settings.MEILISEARCH_HOST, settings.MEILISEARCH_API_KEY
            )
        return cls._meilisearch_client

    # --------------------------------------------------
    # Private utils
    # --------------------------------------------------
    @classmethod
    def _index_from_query(cls, query: Q, index_name: str) -> None:
        """
        Indexes all the objects matching the query on the given index.

        Args:
            query (Q): The django query object to apply
            index_name (str): The target index name
        """
        queryset = cls.MODEL_CLASS.objects.filter(query)
        paginator = Paginator(queryset, 500)
        for page in paginator.page_range:
            instances = paginator.page(page).object_list
            objects = [cls.build_object(instance) for instance in instances]
            if len(objects) > 0:
                cls.meilisearch_client().index(index_name).add_documents(objects)

    @staticmethod
    def _build_search_filter(
        is_empty: List[str] = None,
        is_not_empty: List[str] = None,
        is_null: List[str] = None,
        is_not_null: List[str] = None,
        one_of: List[Tuple[str, List[MeilisearchFilterValue]]] = None,
        none_of: List[Tuple[str, List[MeilisearchFilterValue]]] = None,
        all_of: List[Tuple[str, List[MeilisearchFilterValue]]] = None,
        eq: List[Tuple[str, MeilisearchFilterValue]] = None,
        neq: List[Tuple[str, MeilisearchFilterValue]] = None,
        gt: List[Tuple[str, MeilisearchFilterValue]] = None,
        gte: List[Tuple[str, MeilisearchFilterValue]] = None,
        lt: List[Tuple[str, MeilisearchFilterValue]] = None,
        lte: List[Tuple[str, MeilisearchFilterValue]] = None,
    ) -> str:
        """Builds a search filter string for Meilisearch using the provided supported filters."""
        filters = []
        if is_empty is not None:
            filters.extend([f"{field} IS EMPTY" for field in is_empty])
        if is_not_empty is not None:
            filters.extend([f"{field} IS NOT EMPTY" for field in is_not_empty])
        if is_null is not None:
            filters.extend([f"{field} IS NULL" for field in is_null])
        if is_not_null is not None:
            filters.extend([f"{field} IS NOT NULL" for field in is_not_null])
        if one_of is not None:
            for field, values in one_of:
                value_str = ", ".join([str(v) for v in values])
                filters.append(f"{field} IN [{value_str}]")
        if none_of is not None:
            for field, values in none_of:
                value_str = ", ".join([str(v) for v in values])
                filters.append(f"{field} NOT IN [{value_str}]")
        if all_of is not None:
            for field, values in all_of:
                filters.extend([f"{field} = {value}" for value in values])
        if eq is not None:
            filters.extend([f"{field} = {value}" for field, value in eq])
        if neq is not None:
            filters.extend([f"{field} != {value}" for field, value in neq])
        if gt is not None:
            filters.extend([f"{field} > {value}" for field, value in gt])
        if gte is not None:
            filters.extend([f"{field} >= {value}" for field, value in gte])
        if lt is not None:
            filters.extend([f"{field} < {value}" for field, value in lt])
        if lte is not None:
            filters.extend([f"{field} <= {value}" for field, value in lte])
        return " AND ".join(filters)
