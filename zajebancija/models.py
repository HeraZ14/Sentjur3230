from django.db import models

class Poll(models.Model):
    question = models.CharField(max_length=255, default="Ali si Šmarčani zaslužijo merch?")
    created_at = models.DateTimeField(auto_now_add=True)

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='responses')