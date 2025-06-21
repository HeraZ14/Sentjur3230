from django.contrib import admin
from .models import Poll, PollOption

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]