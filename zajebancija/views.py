from django.shortcuts import render, get_object_or_404, redirect
from .models import Poll, PollOption, Reaction
import random

def glasovanje(request):
    poll = Poll.objects.first()
    print(request)
    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(PollOption, id=option_id)
        option.votes += 1
        option.save()

        # Izberi random reakcijo iz baze
        reactions = Reaction.objects.filter(pollOption_id=option_id)
        print(reactions)
        reaction = random.choice(reactions)

        return render(request, 'zajebancija/rezultati.html', {
            'poll': poll,
            'reaction': reaction.text
        })
    return render(request, 'zajebancija/glasovanje.html', {'poll': poll})

