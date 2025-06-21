from django.contrib import admin
from .models import Poll, PollOption, Reaction

class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 0

class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]


admin.site.register(Poll, PollAdmin)
admin.site.register(Reaction)