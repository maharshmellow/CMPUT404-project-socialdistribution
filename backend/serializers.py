from backend.models import *

from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email


class AuthRegisterSerializer(RegisterSerializer):

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'is_active': False  # Set to False because newly created user needs to get approval from system admin in order to sign in
        }

    def save(self, request):
        # Get the cleaned JSON data
        adapter = get_adapter()
        user = adapter.new_user(request)
        user.is_active = False
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])

        return user


class UserSerializer(serializers.ModelSerializer):

    displayName = serializers.CharField(source="username")
    github = serializers.URLField(source="githubUrl")
    id = serializers.CharField(source="get_full_user_id")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")

    class Meta:
        model = User
        # TODO ignored host stuff for now, need to add back later
        fields = ["firstName","lastName","id", "displayName", "github"]
        # fields = '__all__'
    

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Post
        fields = '__all__'

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ["id","friendDate","unfriendDate","toUser_id"]
        # fields = '__all__'

