from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Category
from shop.serializers.category_serializer import CategoryListSerializer


class CategoryApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Database query (equivalent to Category::where('is_active', true)->get() in Laravel)
        categories = Category.objects.filter(is_active=True).order_by('name')

        # Passing data to the serializer (many=True indicates that it is a list, not a single record)
        serializer= CategoryListSerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)