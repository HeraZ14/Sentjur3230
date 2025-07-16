import json

from django.shortcuts import render, get_object_or_404, redirect
from .models import Poll, PollOption, Reaction, Comment
import random
from .forms import CommentForm

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


def forum(request):
    if request.method == 'POST':
        form = CommentForm(request.POST or None, request=request)

        if form.is_valid():
            comment = form.save(commit=False)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            comment.ip_address = ip

            if request.user.is_authenticated:
                comment.created_by = request.user
            comment.save()
            return redirect('forum')  # ali karkoli je tvoj forum URL
    else:
        form = CommentForm(request=request)  # <<< tudi tu!

    valid_answers = request.session.get('captcha_result', [])
    question = form.fields['captcha_answer'].label
    top_level_comments = Comment.objects.filter(parent__isnull=True).order_by('-created_at')
    return render(request, 'zajebancija/forum.html', {
        'form': form,
        'top_level_comments': top_level_comments,
        'valid_answers_json': json.dumps([a.lower() for a in valid_answers]),
        'captcha_question': question,

    })

