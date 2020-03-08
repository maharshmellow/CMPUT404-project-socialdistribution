from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import views, status
from rest_framework import permissions
from rest_framework.decorators import permission_classes

from backend.serializers import UserSerializer, FriendSerializer, FriendRequestSerializer
from backend.models import User, Friend, FriendRequest
from backend.permissions import *
from rest_framework.decorators import action
from django.http import Http404
from django.db.models import Q
import json


class FriendRequestViewSet(views.APIView):
    """Make a friend request to a user"""
    serializer_class = FriendRequestSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request):
        '''
        /friendrequest/ : create a friendrequest between authenticated user and another user
        '''

        request_data = dict(request.data)
        if request_data:
            serializer = FriendRequestSerializer(
                data=request_data, context={"fromUser": request_data["fromUser"], "toUser": request_data["toUser"]})
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)