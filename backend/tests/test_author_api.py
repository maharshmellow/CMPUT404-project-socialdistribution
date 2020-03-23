from django.contrib.auth import get_user_model
from django.conf import settings
from backend.utils import *
from backend.models import User, Friend, Host
import pytest


@pytest.mark.django_db
class TestAuthorAPI:
    user_notFound_id = "https://example/20"
    def test_get_profile_by_author_id(self, client, test_user, friend_user):
        
        # Checking scenario where the user does not exist, 404 Error
        
        nouserResponse = client.get('/author/{}/'.format(self.user_notFound_id))
        assert nouserResponse.status_code == 404

        # Checking user's profile
        
        test_author_id = test_user.get_full_user_id()
        Friend.objects.create(
            fromUser=test_user, toUser=friend_user[0])
        Friend.objects.create(
            fromUser=test_user, toUser=friend_user[1])

        response = client.get('/author/{}/'.format(test_author_id))
        assert response.status_code == 200

        assert response.data["id"] == test_user.get_full_user_id()

        assert response.data["displayName"] == test_user.username
        assert response.data["host"] is not None
        assert response.data["url"] == test_user.get_full_user_id()
        assert response.data["friends"] is not None

        assert response.data["friends"][0]["id"] == friend_user[0].get_full_user_id(
        )
        assert response.data["friends"][1]["id"] == friend_user[1].get_full_user_id(
        )

    def test_get_friends(self, client, test_user, friend_user):
        
        test_auth_id = test_user.get_full_user_id()

        # Checking scenario where the user doesnt have friends

        noFriendsresponse = client.get('/author/{}/friends/'.format(test_auth_id))
        assert noFriendsresponse.status_code == 200
        assert noFriendsresponse.data["query"] == "friends"
        assert noFriendsresponse.data["authors"] == []

        # checking scenario where the user has friends

        Friend.objects.create(
            fromUser=test_user, toUser=friend_user[0])
        Friend.objects.create(
            fromUser=test_user, toUser=friend_user[1])

        response = client.get('/author/{}/friends/'.format(test_auth_id))

        assert response.status_code == 200
        assert response.data["query"] == "friends"
        assert response.data["authors"] is not None
        assert response.data["authors"][0] == friend_user[0].get_full_user_id()
        assert response.data["authors"][1] == friend_user[1].get_full_user_id()

        # Checking scenario where the user does not exist, 404 Error
        
        nouserResponse = client.get('/author/{}/friends/'.format(self.user_notFound_id))
        assert nouserResponse.status_code == 404


    # def test_github(self, client, test_user,test_host):
    #     no_github_user = User.objects.create_user(
    #         username="user001", password="ualberta01!", host=test_host, githubUrl= "")
    #     nodata_github_user = User.objects.create_user(
    #         username="user0012", password="ualberta01!", host=test_host, githubUrl= "https://github.com/testuser001")
    #     github_user = User.objects.create_user(
    #         username="user0013", password="ualberta01!", host=test_host, githubUrl= "https://github.com/roychowd")


    #     client.force_login(no_github_user)
    #     response = client.get('/author/github')
    #     assert response.status_code == 400
    #     client.logout()

    #     client.force_login(nodata_github_user)
    #     response = client.get('/author/github')
    #     assert response.status_code == 200
    #     assert response.data["data"] == []
    #     client.logout()

    #     client.force_login(github_user)
    #     response = client.get('/author/github')
    #     assert response.status_code == 200
    #     assert response.data["data"] is not None
    #     client.logout()