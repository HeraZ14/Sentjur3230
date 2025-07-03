from django.shortcuts import render, get_object_or_404, redirect
from .models import Poll, PollOption, Reaction
import random

def glasovanje(request):
    poll = Poll.objects.first()
    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(PollOption, id=option_id)
        option.votes += 1
        option.save()

        # Izberi random reakcijo iz baze
        reactions = Reaction.objects.filter(pollOption_id=option_id)
        reaction = random.choice(reactions)

        da_count = (PollOption.objects.get(id=1)).votes
        ne_count = (PollOption.objects.get(id=2)).votes
        total = da_count + ne_count
        da_procent = (da_count / total) * 100
        ne_procent = (ne_count / total) * 100

        return render(request, 'zajebancija/rezultati.html', {
            'poll': poll,
            'reaction': reaction.text,
            "da_procent": da_procent,
            "ne_procent": ne_procent,
        })
    return render(request, 'zajebancija/glasovanje.html', {'poll': poll})

