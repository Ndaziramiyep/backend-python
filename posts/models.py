from django.conf import settings
from django.db import models

from categories.models import Category


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.URLField(max_length=2048, null=True, blank=True)

    # db_index=False: the composite indexes below already lead with this
    # column, so a separate single-column index would be redundant.
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts", db_index=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", db_index=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]
        indexes = [
            # Backs "list posts, newest first" (the default feed query/pagination).
            models.Index(fields=["-created_at"], name="posts_created_at_idx"),
            # Backs "list posts in a category, newest first".
            models.Index(fields=["category", "-created_at"], name="posts_category_created_idx"),
            # Backs "list posts by a given author, newest first".
            models.Index(fields=["author", "-created_at"], name="posts_author_created_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    # TODO: Add search fields/indexes (title/content full-text search)
