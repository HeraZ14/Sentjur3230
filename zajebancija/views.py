from django.shortcuts import render, get_object_or_404, redirect
from .models import Poll, PollOption

def glasovanje(request):
    poll = Poll.objects.first()
    print("jebi se")
    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(PollOption, id=option_id)
        option.votes += 1
        option.save()
        return render(request, 'zajebancija/rezultati.html', {'poll': poll})
    return render(request, 'zajebancija/glasovanje.html', {'poll': poll})

