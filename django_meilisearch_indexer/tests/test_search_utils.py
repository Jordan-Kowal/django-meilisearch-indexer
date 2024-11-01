from unittest import TestCase

from django_meilisearch_indexer.search_utils import build_search_filter


class BuildSearchFilterTestCase(TestCase):
    def test_empty(self) -> None:
        self.assertEqual(build_search_filter(), "")

    def test_is_empty(self) -> None:
        self.assertEqual(
            build_search_filter(is_empty=["field_1", "field_2"]),
            "field_1 IS EMPTY AND field_2 IS EMPTY",
        )

    def test_is_not_empty(self) -> None:
        self.assertEqual(
            build_search_filter(is_not_empty=["field_1", "field_2"]),
            "field_1 IS NOT EMPTY AND field_2 IS NOT EMPTY",
        )

    def test_is_null(self) -> None:
        self.assertEqual(
            build_search_filter(is_null=["field_1", "field_2"]),
            "field_1 IS NULL AND field_2 IS NULL",
        )

    def test_is_not_null(self) -> None:
        self.assertEqual(
            build_search_filter(is_not_null=["field_1", "field_2"]),
            "field_1 IS NOT NULL AND field_2 IS NOT NULL",
        )

    def test_one_of(self) -> None:
        self.assertEqual(
            build_search_filter(
                one_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 IN [1, 2, 3] AND field_2 IN [a, b, c]",
        )

    def test_none_of(self) -> None:
        self.assertEqual(
            build_search_filter(
                none_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 NOT IN [1, 2, 3] AND field_2 NOT IN [a, b, c]",
        )

    def test_all_of(self) -> None:
        self.assertEqual(
            build_search_filter(
                all_of=[("field_1", [1, 2, 3]), ("field_2", ["a", "b", "c"])]
            ),
            "field_1 = 1 AND field_1 = 2 AND field_1 = 3 AND field_2 = a AND field_2 = b AND field_2 = c",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            build_search_filter(eq=[("field_1", 1), ("field_2", "a")]),
            "field_1 = 1 AND field_2 = a",
        )

    def test_neq(self) -> None:
        self.assertEqual(
            build_search_filter(neq=[("field_1", 1), ("field_2", "a")]),
            "field_1 != 1 AND field_2 != a",
        )

    def test_gt(self) -> None:
        self.assertEqual(
            build_search_filter(gt=[("field_1", 1), ("field_2", "a")]),
            "field_1 > 1 AND field_2 > a",
        )

    def test_gte(self) -> None:
        self.assertEqual(
            build_search_filter(gte=[("field_1", 1), ("field_2", "a")]),
            "field_1 >= 1 AND field_2 >= a",
        )

    def test_lt(self) -> None:
        self.assertEqual(
            build_search_filter(lt=[("field_1", 1), ("field_2", "a")]),
            "field_1 < 1 AND field_2 < a",
        )

    def test_lte(self) -> None:
        self.assertEqual(
            build_search_filter(lte=[("field_1", 1), ("field_2", "a")]),
            "field_1 <= 1 AND field_2 <= a",
        )

    def test_complex(self) -> None:
        result = build_search_filter(
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
