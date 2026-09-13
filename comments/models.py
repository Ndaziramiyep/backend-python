from django.conf import settings
from django.db import models

from posts.models import Post


class Comment(models.Model):
    content = models.TextField()

    # db_index=False on post: the composite index below already leads with
    # this column, so a separate single-column index would be redundant.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", db_index=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]
        indexes = [
            # Backs "list comments for a post, oldest first" and the post comment count.
            models.Index(fields=["post", "created_at"], name="comments_post_created_idx"),
        ]

    def __str__(self) -> str:
        return f"Comment({self.id}) on Post({self.post_id})"
