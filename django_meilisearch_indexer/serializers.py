from rest_framework import serializers


class MeilisearchSimpleSearchSerializer(serializers.Serializer):
    """Serializer which represents a simple search query input for Meilisearch."""

    query = serializers.CharField(max_length=255, required=True, allow_blank=False)


class MeilisearchSearchResultsSerializer(serializers.Serializer):
    """Serializer which represents the complete result of a Meilisearch search query."""

    hits = serializers.ListField(child=serializers.DictField())
    offset = serializers.IntegerField()
    limit = serializers.IntegerField()
    estimatedTotalHits = serializers.IntegerField()
    totalHits = serializers.IntegerField()
    totalPages = serializers.IntegerField()
    hitsPerPage = serializers.IntegerField()
    page = serializers.IntegerField()
    facetDistribution = serializers.DictField(child=serializers.DictField())
    facetStats = serializers.DictField(child=serializers.DictField())
    processingTimeMs = serializers.IntegerField()
    query = serializers.CharField()


class MeilisearchOnlyHitsResponseSerializer(serializers.Serializer):
    """Serializer which only returns the 'hits' field from Meilisearch search results."""

    hits = serializers.ListField(child=serializers.DictField())
