# shop/api_views/product_view.py
import re

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ai_chat.access import CHAT_AUTHENTICATION, IsChatParticipant
from shop.models import Product, ProductStatus
from shop.serializers import ProductListSerializer
from shop.services.category_filters import category_tree_ids


class ProductListAPIView(APIView):
    authentication_classes = CHAT_AUTHENTICATION
    permission_classes = [IsChatParticipant]

    def get(self, request):
        queryset = (
            Product.objects
            .filter(status=ProductStatus.PUBLISHED)
            .prefetch_related('categories', 'attributes')
            .order_by('-created_at')
        )

        # Text search filter (title or description)
        q = request.query_params.get('q', '').strip()
        if q:
            stop_words = {
                'برای', 'در', 'برابر', 'با', 'و', 'یا', 'از', 'به', 'را',
                'میخواهم', 'می‌خواهم', 'میخوام', 'می‌خوام', 'لطفا', 'لطفاً',
                'یک', 'دو', 'مدل', 'چند', 'دومدل', 'که', 'است', 'باشد',
            }
            words = [word.strip('،,.؟!') for word in q.split() if word.strip('،,.؟!') not in stop_words]
            word_filters = []
            for index, word in enumerate(words):
                if index == 0:
                    pattern = r'(^|[[:space:][:punct:]‌])' + re.escape(word) + r'($|[[:space:][:punct:]‌])'
                    word_filters.append(
                        Q(title__iregex=pattern) | Q(short_description__iregex=pattern)
                        | Q(description__iregex=pattern) | Q(attributes__value__iregex=pattern)
                    )
                else:
                    word_filters.append(
                        Q(title__icontains=word) | Q(short_description__icontains=word)
                        | Q(description__icontains=word) | Q(attributes__value__icontains=word)
                    )
            if word_filters:
                for word_filter in word_filters:
                    queryset = queryset.filter(word_filter)
                queryset = queryset.distinct()

        # Category Slug Filter
        category_slug = request.query_params.get('category', '').strip()
        if category_slug:
            queryset = queryset.filter(categories__id__in=category_tree_ids([category_slug])).distinct()

        categories = [slug for slug in request.query_params.get('categories', '').split(',') if slug][:5]
        if categories:
            queryset = queryset.filter(categories__id__in=category_tree_ids(categories)).distinct()

        tags = [tag.strip() for tag in request.query_params.get('tags', '').split(',') if tag.strip()]
        if tags:
            queryset = queryset.filter(Q(tags__title__in=tags) | Q(tags__slug__in=tags)).distinct()

        # Limiting the quantity (Limit)
        limit = request.query_params.get('limit')
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]

        serializer = ProductListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
