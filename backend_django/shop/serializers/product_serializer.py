from rest_framework import serializers
from shop.models import Product
from shop.serializers.category_serializer import CategorySimpleSerializer


class ProductListSerializer(serializers.ModelSerializer):

    # Relational Fields (Foreign / ManyToMany)
    categories = CategorySimpleSerializer(many=True, read_only=True)

    # Computed field (the `final_price` property you defined within the `Product` model)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=0, read_only=True)
    attributes = serializers.SerializerMethodField()

    def get_attributes(self, obj):
        return [{"key": item.key, "value": item.value} for item in obj.attributes.all()[:8]]

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'slug',
            'sku',
            'price',
            'sale_price',
            'final_price',
            'stock',
            'available_stock',
            'is_in_stock',
            'status',
            'is_featured',
            'categories',
            'attributes',
            'created_at',
        ]
