from django.db import models

class Idea(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    idea = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.idea[:30]}"