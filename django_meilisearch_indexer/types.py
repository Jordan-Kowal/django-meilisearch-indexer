from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, Union


class Faceting(TypedDict):
    maxValuesPerFacet: int
    sortFacetValuesBy: Dict[str, str]


class Pagination(TypedDict):
    maxTotalHits: int


class MinWordSizeForTypos(TypedDict):
    oneTypo: int
    twoTypos: int


class TypoTolerance(TypedDict):
    enabled: bool
    MinWordSizeForTypos: MinWordSizeForTypos
    disableOnWords: List[str]
    disableOnAttributes: List[str]


Precision = Literal["byWord", "byAttribute"]
RankingRule = Literal["words", "typo", "proximity", "attribute", "sort", "exactness"]


class MeilisearchSettings(TypedDict, total=False):
    displayedAttributes: Optional[List[str]]
    distinctAttribute: Optional[str]
    faceting: Optional[Faceting]
    filterableAttributes: Optional[List[str]]
    pagination: Optional[Pagination]
    proximityPrecision: Optional[Precision]
    rankingRules: Optional[List[RankingRule]]
    searchableAttributes: Optional[List[str]]
    separatorTokens: Optional[List[str]]
    nonSeparatorTokens: Optional[List[str]]
    sortableAttributes: Optional[List[str]]
    stopWords: Optional[List[str]]
    synonyms: Optional[Dict[str, List[str]]]
    typoTolerance: Optional[TypoTolerance]


MeilisearchFilterValue = Union[str, int, float]


class MeilisearchFilters(TypedDict, total=False):
    is_empty: List[str]
    is_not_empty: List[str]
    is_null: List[str]
    is_not_null: List[str]
    one_of: List[Tuple[str, List[MeilisearchFilterValue]]]
    none_of: List[Tuple[str, List[MeilisearchFilterValue]]]
    all_of: List[Tuple[str, List[MeilisearchFilterValue]]]
    eq: List[Tuple[str, MeilisearchFilterValue]]
    neq: List[Tuple[str, MeilisearchFilterValue]]
    gt: List[Tuple[str, MeilisearchFilterValue]]
    gte: List[Tuple[str, MeilisearchFilterValue]]
    lt: List[Tuple[str, MeilisearchFilterValue]]
    lte: List[Tuple[str, MeilisearchFilterValue]]


class MeilisearchSearchParameters(TypedDict, total=False):
    offset: Optional[int]
    limit: Optional[int]
    hitsPerPage: Optional[int]
    page: Optional[int]
    filter: Optional[str]
    facets: Optional[List[str]]
    attributesToRetrieve: Optional[List[str]]
    attributesToCrop: Optional[List[str]]
    cropLength: Optional[int]
    cropMarker: Optional[str]
    attributesToHighlight: Optional[List[str]]
    highlightPreTag: Optional[str]
    highlightPostTag: Optional[str]
    showMatchesPosition: Optional[bool]
    sort: Optional[List[str]]
    matchingStrategy: Optional[str]
    showRankingScore: Optional[bool]
    attributesToSearchOn: Optional[List[str]]


class MeilisearchSearchResults(TypedDict, total=False):
    hits: List[Dict[str, Any]]
    offset: int
    limit: int
    estimatedTotalHits: int
    totalHits: int
    totalPages: int
    hitsPerPage: int
    page: int
    facetDistribution: Dict[str, Dict[str, int]]
    facetStats: Dict[str, Dict[str, int]]
    processingTimeMs: int
    query: str


class MeilisearchSearchHits(TypedDict, total=False):
    hits: List[Dict[str, Any]]
