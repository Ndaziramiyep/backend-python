import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        db_index=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="posts",
                        to="categories.category",
                    ),
                ),
            ],
            options={
                "db_table": "posts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["-created_at"], name="posts_created_at_idx"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["category", "-created_at"], name="posts_category_created_idx"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["author", "-created_at"], name="posts_author_created_idx"),
        ),
    ]
