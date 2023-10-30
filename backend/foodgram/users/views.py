from django.shortcuts import get_object_or_404
from rest_framework import permissions

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from djoser.views import UserViewSet

from api.serializers import FollowSerializer, UserSerializer
from .models import Follow, User


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        if request.method == 'POST':
            if Follow.objects.filter(user=user, following=id).exists():
                return Response({"error": "Вы уже подписаны"},
                                status=HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, following=id)
            follow_author = get_object_or_404(User, id=id)
            serializer = FollowSerializer(follow_author)
            return Response(serializer.data, status=HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if Follow.objects.filter(user=user, id=id).exists():
                Follow.objects.filter(user=user, id=id).delete()
                return Response(status=HTTP_200_OK)
            return Response({"error": "Вы не подписаны на автора"},
                            status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribtions(self, request):
        user = request.user
        # me = User.objects.filter(id=user)
        me = get_object_or_404(User, id=user)
        serializer = FollowSerializer(me)
        return Response(serializer.data, status=HTTP_201_CREATED)
