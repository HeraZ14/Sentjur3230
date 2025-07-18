from datetime import timezone

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


class Poll(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text}"

class Reaction(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    pollOption = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.text}"

class Comment(models.Model):
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    anonymous_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )

    def author_display(self):
        if self.created_by:
            return self.created_by.username
        return self.anonymous_name or "Anonymous"

    def is_reply(self):
        return self.parent is not None

    def vote_score(self):
        return self.votes.aggregate(score=Sum('vote'))['score'] or 0

    def __str__(self):
        return f"{self.author_display()} – {self.content[:30]}"

class CommentVote(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    ip_address = models.GenericIPAddressField()
    vote = models.SmallIntegerField()  # 1 = upvote, -1 = downvote

    class Meta:
        unique_together = ('comment', 'ip_address')