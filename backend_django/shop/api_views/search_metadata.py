from functools import reduce
from operator import or_

from django.db.models import Q
from ai_chat.access import CHAT_AUTHENTICATION, IsChatParticipant
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Category, ProductAttribute, ProductStatus, Tag


class SearchMetadataAPIView(APIView):
    authentication_classes = CHAT_AUTHENTICATION
    permission_classes = [IsChatParticipant]

    def get(self, request):
        terms = [term[:80] for term in request.query_params.get("terms", "").split(",") if term][:12]
        if not terms:
            return Response({"categories": [], "tags": [], "attributes": []})
        category_query = reduce(or_, [Q(name__icontains=term) | Q(slug__icontains=term) for term in terms])
        tag_query = reduce(or_, [Q(title__icontains=term) | Q(slug__icontains=term) for term in terms])
        attribute_query = reduce(or_, [Q(key__icontains=term) | Q(value__icontains=term) for term in terms])
        categories = list(Category.objects.filter(is_active=True).filter(category_query).values("slug", "name")[:20])
        tags = list(Tag.objects.filter(tag_query).values("slug", "title")[:20])
        attributes = list(ProductAttribute.objects.filter(
            product__status=ProductStatus.PUBLISHED,
        ).filter(attribute_query).values("key", "value").order_by("key", "value").distinct()[:20])
        return Response({"categories": categories, "tags": tags, "attributes": attributes})
