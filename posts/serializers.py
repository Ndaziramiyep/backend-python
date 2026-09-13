from rest_framework import serializers

from posts.models import Post


class PostRequestSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=1)
    content = serializers.CharField(min_length=1)
    categoryId = serializers.IntegerField(required=False, allow_null=True, default=None)


class PostSerializer(serializers.ModelSerializer):
    categoryName = serializers.SerializerMethodField()
    categoryId = serializers.IntegerField(source="category_id", read_only=True)
    authorName = serializers.CharField(source="author.name", read_only=True)
    authorEmail = serializers.CharField(source="author.email", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    commentCount = serializers.IntegerField(source="comment_count", read_only=True, default=0)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "categoryName",
            "categoryId",
            "authorName",
            "authorEmail",
            "createdAt",
            "updatedAt",
            "commentCount",
        ]

    def get_categoryName(self, post: Post):
        return post.category.name if post.category_id else None
