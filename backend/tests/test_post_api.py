from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from backend.models import Post, Host
from backend.permissions import *
from backend.settings import BASE_DIR

import pytest
import json
import base64
import os

User = get_user_model()


@pytest.mark.django_db
class TestPostAPI:

    def test_get_post_by_id(self, client, test_user, test_user_2):
        test_post = Post.objects.create(
            author=test_user, title="post title", content="post content", visibility=FRIENDS)
        test_post_id = test_post.postId

        # without logging in, user shouldn't be able to view the post
        response = client.get('/posts/{}'.format(test_post_id))
        assert response.status_code == 401

        # User who has no permission to view the post shouldn't see this post
        client.force_login(test_user_2)
        response = client.get('/posts/{}'.format(test_post_id))
        assert response.status_code == 401
        client.logout()

        client.force_login(test_user)
        response = client.get('/posts/{}'.format(test_post_id))
        assert response.status_code == 200
        assert response.data["query"] == "posts"
        assert response.data["count"] == 1
        assert response.data["size"] == 50

        assert response.data["posts"] is not None
        assert len(response.data["posts"]) == 1
        assert response.data["posts"][0]["title"] == "post title"
        assert response.data["posts"][0]["content"] == "post content"

        assert response.data["posts"][0]["author"] is not None
        assert response.data["posts"][0]["author"]["displayName"] == test_user.username
        assert response.data["posts"][0]["author"]["github"] == test_user.githubUrl

    def test_create_post(self, client, test_user):
        test_post_title = "testpost001"
        test_post_content = "testposttitle001"
        post_body_1 = json.dumps({
            "title": test_post_title,
            "content": test_post_content,
            "visibility": PUBLIC,
            "unlisted": False,
        })

        response = client.post('/author/posts', data=post_body_1,
                               content_type='application/json', charset='UTF-8')
        assert response.status_code == 401

        # Post should only be created after user is authenticated
        client.force_login(test_user)
        response = client.post('/author/posts', data=post_body_1,
                               content_type='application/json', charset='UTF-8')
        assert response.status_code == 201

        # Create image post
        image_path = os.path.join(
            BASE_DIR, 'backend/tests/assets/test-image.png')
        print(image_path)
        with open(image_path, "rb") as image_file:
            test_post_content = str(base64.b64encode(image_file.read()))

        image_body_1 = json.dumps({
            "title": test_post_title,
            "content": test_post_content,
            "visibility": PUBLIC,
            "content_type": "image/png;base64",
            "unlisted": True,
        })

        response = client.post('/author/posts', data=image_body_1,
                               content_type='application/json', charset='UTF-8')
        assert response.status_code == 201
        assert response.data["uuid"]

    def test_delete_post(self, client, test_user, test_host):
        # Create a post used to test the delete
        test_post = Post.objects.create(
            author=test_user, title="post title", content="post content")
        test_post_id = test_post.postId
        # Create another user
        test_user_non_author = User.objects.create_user(
            username='testuser002', password='ualberta!', host=test_host)

        response = client.delete('/posts/{}'.format(test_post_id))
        assert response.status_code == 401

        # user other than post owner shouldn't be able to delete the post
        client.force_login(test_user_non_author)
        response = client.delete('/posts/{}'.format(test_post_id))
        assert response.status_code == 403

        client.logout()
        client.force_login(test_user)
        response = client.delete('/posts/{}'.format(test_post_id))
        assert response.status_code == 204
        assert not Post.objects.filter(postId=test_post_id).exists()

    def test_get_visible_post(self, client, test_user, test_host):
        test_user_no_access = User.objects.create_user(
            username='testuser003', password='ualberta!', host=test_host)
        test_user_with_access = User.objects.create_user(
            username='testuser004', password='ualberta!', host=test_host)

        test_post = Post.objects.create(
            author=test_user, title="post title", content="post content", visibility=PRIVATE, visibleTo=[test_user_with_access.get_full_user_id()])

        client.force_login(test_user_no_access)
        response = client.get('/author/posts')
        assert response.status_code == 200
        assert response.data["query"] == "posts"
        assert response.data["count"] == 0
        assert response.data["posts"] is not None
        assert len(response.data["posts"]) == 0
        client.logout()

        client.force_login(test_user_with_access)
        response = client.get('/author/posts')
        assert response.status_code == 200
        assert response.data["query"] == "posts"
        assert response.data["count"] >= 0
        assert response.data["posts"] is not None
        assert len(response.data["posts"]) > 0
        assert response.data["posts"][0]["content"] == test_post.content
        client.logout()

    def test_get_visible_post_by_id(self, client, test_user, test_host):
        test_user_no_access = User.objects.create_user(
            username='testuser003', password='ualberta!', host=test_host)
        test_user_with_access = User.objects.create_user(
            username='testuser004', password='ualberta!', host=test_host)
        test_post = Post.objects.create(
            author=test_user, title="post title", content="post content", visibility=PRIVATE, visibleTo=[test_user_with_access.get_full_user_id()])

        random_user_id = "randomid"
        client.force_login(test_user_no_access)
        response = client.get('/author/{}/posts'.format(random_user_id))
        assert response.status_code == 400

        response = client.get('/author/{}/posts'.format(test_user.fullId))
        assert response.status_code == 200
        assert response.data["query"] == "posts"
        assert response.data["count"] == 0
        assert len(response.data["posts"]) == 0
        client.logout()

        client.force_login(test_user_with_access)
        response = client.get('/author/{}/posts'.format(test_user.fullId))
        assert response.status_code == 200
        assert response.data["query"] == "posts"
        assert response.data["count"] >= 0
        assert response.data["posts"] is not None
        assert len(response.data["posts"]) > 0
        assert response.data["posts"][0]["content"] == test_post.content
        client.logout()

    def test_update_post(self, client, test_user, test_host):
        test_user_no_access = User.objects.create_user(
            username='testuser003', password='ualberta!', host=test_host)
        test_user_with_access = User.objects.create_user(
            username='testuser004', password='ualberta!', host=test_host)

        test_post = Post.objects.create(
            author=test_user_with_access, title="post title", content="post content", visibility=PUBLIC
        )

        content = json.dumps({
            "username": test_user_with_access.username,
            "authorId": test_user_with_access.get_full_user_id(),
            "title": "Edited title",
            "content": "Edited Content",
            "source": test_post.get_source(),
            "comments": [],
            "isGithubPost": "false",
            "visibility": PUBLIC
        })
        client.force_login(test_user_no_access)
        response = client.put('/posts/{}'.format(test_post.postId),
                              data=content, content_type='application/json', charset='UTF-8')
        assert response.status_code == 400
        client.logout()

        client.force_login(test_user_with_access)
        response = client.put('/posts/{}'.format(test_post.postId),
                              data=content, content_type='application/json', charset='UTF-8')
        assert response.status_code == 200
        post = get_object_or_404(Post, pk=test_post.postId)
        assert post.title == "Edited title"
        assert post.content == "Edited Content"
        client.logout()
