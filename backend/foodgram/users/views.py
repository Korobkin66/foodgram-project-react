from api.serializers import FollowSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from .models import Follow, User


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        follow_author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if Follow.objects.filter(user=user,
                                     following=follow_author).exists():
                return Response({"error": "Вы уже подписаны"},
                                status=HTTP_400_BAD_REQUEST)

            serializer = FollowSerializer(follow_author, data=request.data,
                                          context={"request": request})
            serializer.is_valid()

            Follow.objects.create(user=user, following=follow_author)
            return Response(serializer.data, status=HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if Follow.objects.filter(user=user,
                                     following=follow_author).exists():
                Follow.objects.filter(user=user,
                                      following=follow_author).delete()
                return Response({"log": "Вы отписались"}, status=HTTP_200_OK)
            return Response({"error": "Вы не подписаны на автора"},
                            status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        print('я туту')
        # me = User.objects.filter(id=user)
        me = get_object_or_404(User, id=user.id)
        serializer = FollowSerializer(me)
        return Response(serializer.data, status=HTTP_200_OK)

    # @action(detail=False, methods=['get'],
    #         permission_classes=[permissions.IsAuthenticated],
    #         url_path='subscriptions')
    # def subscriptions(self, request):
    #     user = request.user
    #     subscribed_users = Follow.objects.filter(user=user).values_list(
    #         'following', flat=True)

    #     serializer = FollowSerializer(
    #         User.objects.filter(id__in=subscribed_users), many=True)

    #     return Response(serializer.data, status=HTTP_200_OK)
