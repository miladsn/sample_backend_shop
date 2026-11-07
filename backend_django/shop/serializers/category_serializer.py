from rest_framework import serializers       # ✅
from shop.models import Category


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # Fields we want in the JSON output:
        fields = ['id', 'name', 'slug', 'is_active']