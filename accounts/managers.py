from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, name: str, password: str, role: str, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a name")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, name: str, password: str, **extra_fields):
        from accounts.models import Role

        extra_fields.setdefault("role", Role.USER)
        return self._create_user(email, name, password, extra_fields.pop("role"), **extra_fields)

    def create_superuser(self, email: str, name: str, password: str, **extra_fields):
        from accounts.models import Role

        extra_fields["role"] = Role.ADMIN
        return self._create_user(email, name, password, extra_fields.pop("role"), **extra_fields)
