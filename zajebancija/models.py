from datetime import timezone

from django.db import models

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