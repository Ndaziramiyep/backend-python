from django.urls import path

from accounts.views import LoginView, RegisterView
from categories.views import CategoryListView
from comments.views import CommentListView
from posts.views import PostDetailView, PostListCreateView

urlpatterns = [
    path("api/auth/register", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login", LoginView.as_view(), name="auth-login"),
    path("api/categories", CategoryListView.as_view(), name="category-list"),
    path("api/posts", PostListCreateView.as_view(), name="post-list-create"),
    path("api/posts/<int:post_id>", PostDetailView.as_view(), name="post-detail"),
    path("api/posts/<int:post_id>/comments", CommentListView.as_view(), name="comment-list"),
]
