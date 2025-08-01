from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email e senha são obrigatórios.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(email=email, password=password)

    if user is None:
        return Response(
            {'error': 'Credenciais inválidas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Usuário inativo.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'profile': user.profile,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def refresh_token_view(request):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token é obrigatório.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access_token': str(refresh.access_token),
        })
    except Exception:
        return Response(
            {'error': 'Token inválido.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
