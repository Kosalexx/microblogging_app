from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.models import Tweet, User
from django.db.models import Count, Q

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def get_replies(tweet_id: int) -> QuerySet:
    """
    Retrieve tweets replies based on the tweet ID.
    Args:
        tweet_id (int): The ID of the tweet.
    Returns:
        QuerySet: A queryset containing the tweets replies.
    """

    replies = (
        Tweet.objects.annotate(
            num_reposts=Count("reposts", distinct=True),
            num_likes=Count("likes", distinct=True),
            num_replies=Count("tweets_replies", distinct=True),
        )
        .prefetch_related("like", "repost", "tags")
        .select_related("user", "reply_to", "reply_to__user")
        .filter(reply_to=tweet_id)
        .order_by("-created_at")
    )
    return replies


def get_tweets_reposts_from_following_users(user: User) -> tuple[QuerySet, QuerySet]:
    """
    Retrieve tweets from users followed by the given user.
    Args:
        user (User): The user whose followed users' tweets are to be retrieved.
    Returns:
        QuerySet of tweets from following users.
    """

    following_users = user.following.all()

    result = (
        Tweet.objects.annotate(
            num_reposts=Count("reposts", distinct=True),
            num_likes=Count("likes", distinct=True),
            num_replies=Count("tweets_replies", distinct=True),
        )
        .prefetch_related("like", "repost", "tags")
        .select_related("user", "reply_to", "reply_to__user")
        .filter(Q(user__in=following_users) | Q(reposts__user__in=following_users))
        .order_by("created_at")
    )

    return result, following_users


def ordering_tweets(tweets: QuerySet, condition: str) -> QuerySet:
    """
    Order tweets by received condition.
    Args:
       tweets (QuerySet): The user whose followed users' tweets are to be retrieved.
       condition: Condition for ordering
    Returns:
        Ordered QuerySet of tweets.
    """

    if condition == "most_likes":
        most_likes_tweets = tweets.order_by("-num_likes")
        return most_likes_tweets
    else:
        newest_tweets = tweets.order_by("-created_at")
        return newest_tweets
