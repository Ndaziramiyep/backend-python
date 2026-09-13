from rest_framework import generics
from rest_framework.permissions import AllowAny

from categories.models import Category
from categories.serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    """GET /api/categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    # TODO: Add CRUD endpoints for admin category management
