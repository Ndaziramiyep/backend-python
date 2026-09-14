from typing import Optional, Tuple

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication

from accounts.jwt_auth import decode_token
from accounts.models import User


class JWTAuthentication(BaseAuthentication):
    """Reads ``Authorization: Bearer <token>`` and resolves the user by the
    token's ``sub`` (email) claim. Returns ``None`` (rather than raising) for
    a missing or invalid token so unauthenticated requests fall through to
    ``AnonymousUser`` and are rejected by ``IsAuthenticated`` where required.
    """

    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header[len("Bearer "):]
        payload = decode_token(token)
        if payload is None:
            return None

        try:
            user = User.objects.get(email=payload.get("sub"))
        except User.DoesNotExist:
            return None

        User.objects.filter(pk=user.pk).update(is_online=True, last_seen=timezone.now())

        return user, token
