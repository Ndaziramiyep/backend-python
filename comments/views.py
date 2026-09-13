from rest_framework import generics
from rest_framework.permissions import AllowAny

from comments.models import Comment
from comments.serializers import CommentSerializer


class CommentListView(generics.ListAPIView):
    """GET /api/posts/{post_id}/comments"""

    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.select_related("author").filter(post_id=post_id).order_by("created_at")

    # TODO: Add POST endpoint for creating comments
    # TODO: Add DELETE endpoint for deleting comments
