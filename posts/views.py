from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Role
from categories.models import Category
from posts.models import Post
from posts.pagination import page_response, paginate_queryset
from posts.serializers import PostRequestSerializer, PostSerializer


def _base_queryset():
    return Post.objects.select_related("author", "category").annotate(comment_count=Count("comments"))


def _apply_category(post: Post, category_id) -> None:
    if category_id is None:
        return
    category = Category.objects.filter(id=category_id).first()
    if category is not None:
        post.category = category


class PostListCreateView(APIView):
    """GET/POST /api/posts"""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        queryset = _base_queryset().order_by("-created_at")
        content, page, size, total_elements = paginate_queryset(queryset, request)
        serialized = PostSerializer(content, many=True).data
        return Response(page_response(serialized, page, size, total_elements))

    def post(self, request):
        serializer = PostRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        post = Post(title=data["title"], content=data["content"], author=request.user)
        _apply_category(post, data.get("categoryId"))
        post.save()
        post.comment_count = 0

        return Response(PostSerializer(post).data)

    # TODO: Add search endpoint
    # GET /api/posts/search?q=...


class PostDetailView(APIView):
    """GET/PUT/DELETE /api/posts/{id}"""

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self, post_id: int) -> Post:
        try:
            return _base_queryset().get(id=post_id)
        except Post.DoesNotExist:
            raise NotFound("Post not found")

    def get(self, request, post_id: int):
        return Response(PostSerializer(self.get_object(post_id)).data)

    def put(self, request, post_id: int):
        post = self.get_object(post_id)
        if post.author_id != request.user.id:
            raise PermissionDenied("Not authorized to update this post")

        serializer = PostRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        post.title = data["title"]
        post.content = data["content"]
        _apply_category(post, data.get("categoryId"))
        post.updated_at = timezone.now()
        post.save()

        return Response(PostSerializer(post).data)

    def delete(self, request, post_id: int):
        post = self.get_object(post_id)
        if post.author_id != request.user.id and request.user.role != Role.ADMIN:
            raise PermissionDenied("Not authorized to delete this post")

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
