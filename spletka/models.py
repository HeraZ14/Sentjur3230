from django.db import models

class Idea(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    idea = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.idea[:30]}"

class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    preview_token = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.title