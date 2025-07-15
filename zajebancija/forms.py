import random

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    captcha_answer = forms.CharField(label="Potrdi, da si domačin", widget=forms.TextInput())

    class Meta:
        model = Comment
        fields = ['content', 'parent']
        widgets = {
            'parent': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Generiraj random captcha vprašanje
        a = random.randint(0, 2)
        questions = [
            "Dve besedi in število:",
            "Župan velemesta:",
            "Reka, brezdomec:"
        ]
        valid_answers = [
            ["šentjur", "sentjur", "3230", "metropola"],
            ["marko", "diaci"],
            ["pešnica", "pešnca", "beco"]
        ]

        self.fields['captcha_answer'].label = questions[a]
        if self.request:
            self.request.session['captcha_result'] = valid_answers[a]

    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer', '').strip().lower()
        correct_answers = self.request.session.get('captcha_result', [])
        user_inputs = [w.lower() for w in answer.strip().split()]
        print(user_inputs)

        for word in user_inputs:
            if word not in correct_answers:
                raise forms.ValidationError("Nisi Šentjurčan.")
        return answer