# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from backend.utils import *

import uuid


class Host(models.Model):
    url = models.URLField(max_length=400)
    serviceAccountUsername = models.CharField(
        max_length=100, null=True, blank=True)
    serviceAccountPassword = models.CharField(
        max_length=100, null=True, blank=True)


class User(AbstractUser):
    githubUrl = models.URLField(max_length=400, blank=True)
    host = models.ForeignKey(
        Host, null=True, blank=True, on_delete=models.CASCADE)
    fullId = models.CharField(max_length=400, default='')

    def get_full_user_id(self):

        if self.host.url != settings.APP_HOST:
            return "https://{}".format(self.fullId)

        user_host = self.host.url
        if user_host[-1] == "/":
            user_host = user_host[:-1]

        return "{}/author/{}".format(user_host, self.id)

    def get_profile_url(self):
        profile_url = "{}author/{}".format(settings.APP_HOST, self.fullId)
        return profile_url

    def get_friends(self):
        friend_ids = Friend.objects.filter(
            fromUser__fullId=self.fullId).values_list('toUser__fullId', flat=True)
        friend_list = User.objects.filter(fullId__in=friend_ids)

        return friend_list

    def get_foaf(self):
        foaf = User.objects.none()
        friends = self.get_friends()

        for friend in friends:
            foaf |= friend.get_friends().exclude(fullId=self.fullId)

        return foaf.distinct()

    def save(self, *args, **kwargs):
        # save twice to get auto-increment id
        super().save(*args, **kwargs)

        if not self.host:
            current_host = settings.APP_HOST
            if Host.objects.filter(url=current_host).exists():
                host_obj = Host.objects.get(url=current_host)
            else:
                host_obj = Host.objects.create(url=current_host)
                host_obj.save()
            self.host = host_obj
        super().save(*args, **kwargs)
        if not self.fullId:
            fullId = self.get_full_user_id()
            fullId = protocol_removed(fullId)
            self.fullId = fullId
            super().save(*args, **kwargs)


class Post(models.Model):
    VISIBILITY_CHOICES = (
        ("PUBLIC", "PUBLIC"),
        ("FOAF", "FOAF"),
        ("FRIENDS", "FRIENDS"),
        ("PRIVATE", "PRIVATE"),
        ("SERVERONLY", "SERVERONLY"),
    )

    CONTENT_TYPES = (
        ("text/plain", "text/plain"),
        ("text/markdown", "text/markdown"),
        ("image/png;base64", "image/png;base64"),
        ("image/jpeg;base64", "image/jpeg;base64"),
        ("application/base64", "application/base64"),
    )

    postId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    content_type = models.CharField(
        max_length=20, choices=CONTENT_TYPES, default="text/markdown")
    # Visibility can be one of the followings : "PUBLIC","PRIVATE","Private","FRIENDS","FOF" or specific user ID
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default="PUBLIC")
    visibleTo = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    is_unlisted = models.BooleanField(default=False)

    def is_image(self):
        if self.content_type == "image/png;base64" or self.content_type == "image/jpeg;base64":
            return True
        return False

    def get_visible_users(self):
        if self.visibility == "PUBLIC":
            if self.is_unlisted:
                users = User.objects.none()
            else:
                users = User.objects.all()
        elif self.visibility == "FRIENDS":
            users = self.author.get_friends()
        elif self.visibility == "FOAF":
            users = self.author.get_friends()
            users = users.union(self.author.get_foaf())
        elif self.visibility == "PRIVATE":
            visible_to = map(protocol_removed, self.visibleTo)
            users = User.objects.filter(fullId__in=visible_to)
        elif self.visibility == "SERVERONLY":
            users = User.objects.filter(host__url=settings.APP_HOST)

        users |= User.objects.filter(id=self.author.id)

        # Superuser(server admin) will have access to all the posts
        superusers = User.objects.filter(is_superuser=True)
        users |= superusers

        return users.distinct()

    def get_source(self):
        host_name = settings.APP_HOST
        return "{}posts/{}".format(host_name, self.postId)


class Comments(models.Model):

    CONTENT_TYPES = (
        ("text/plain", "text/plain"),
        ("application/base64", "application/base64"),
        ("text/markdown", "text/markdown"),
        ("image/png;base64", "image/png;base64"),
        ("image/jpeg;base64", "image/jpeg;base64"),
    )

    commentId = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    postedBy = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_postedBy")
    published = models.DateTimeField(auto_now_add=True)
    contentType = models.CharField(
        max_length=30, choices=CONTENT_TYPES, default="text/plain")

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"


class FriendRequest(models.Model):
    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friendRequest_fromUser")
    toUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friendRequest_toUser")
    isAccepted = models.BooleanField(default=False)
    sentDate = models.DateTimeField(auto_now_add=True)


class Friend(models.Model):
    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friend_fromUser")
    toUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friend_toUser")
    friendDate = models.DateTimeField(auto_now_add=True)
    unfriendDate = models.DateTimeField(null=True, blank=True)
