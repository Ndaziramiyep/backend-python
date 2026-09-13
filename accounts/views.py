from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.jwt_auth import generate_token
from accounts.models import Role, User
from accounts.serializers import AuthResponseSerializer, LoginSerializer, RegisterSerializer


def _auth_response(user: User) -> Response:
    token = generate_token(user.email, user.role)
    payload = {"token": token, "email": user.email, "name": user.name, "role": user.role}
    return Response(AuthResponseSerializer(payload).data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError({"email": "Email already registered"})

        user = User(email=data["email"], name=data["name"], role=Role.USER)
        user.set_password(data["password"])
        user.save()

        return _auth_response(user)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid credentials")

        if not user.check_password(data["password"]):
            raise AuthenticationFailed("Invalid credentials")

        return _auth_response(user)
