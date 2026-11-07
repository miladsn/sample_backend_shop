from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Tag
from shop.serializers.tag_serializer import TagListSerializer


class TagApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        tags = Tag.objects.all()
        if query:
            tags = tags.filter(title__icontains=query)
        serializer = TagListSerializer(tags[:100], many=True)
        return Response(serializer.data)
