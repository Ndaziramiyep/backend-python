from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from passlib.context import CryptContext

from accounts.managers import UserManager

# Same hashing scheme as the original Spring/FastAPI services, so existing
# BCrypt password hashes (see resources seed data) keep working unchanged.
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Role(models.TextChoices):
    USER = "USER", "User"
    ADMIN = "ADMIN", "Admin"


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email

    def set_password(self, raw_password: str) -> None:
        self.password = password_hasher.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        try:
            return password_hasher.verify(raw_password, self.password)
        except ValueError:
            return False
