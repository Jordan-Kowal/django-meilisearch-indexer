from typing import List, Tuple

from django_meilisearch_indexer.types import MeilisearchFilterValue


def build_search_filter(
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
