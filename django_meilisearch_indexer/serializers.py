from rest_framework import serializers


class MeilisearchSimpleSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255, required=True, allow_blank=False)


class MeilisearchOnlyHitsResponseSerializer(serializers.Serializer):
    hits = serializers.ListField(child=serializers.DictField())


class MeilisearchSearchResultsSerializer(serializers.Serializer):
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
