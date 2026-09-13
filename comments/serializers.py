from rest_framework import serializers

from comments.models import Comment


class CommentRequestSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1)


class CommentSerializer(serializers.ModelSerializer):
    authorName = serializers.CharField(source="author.name", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "authorName", "createdAt"]
