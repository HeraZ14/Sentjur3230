import random
import re

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    captcha_answer = forms.CharField(label="Potrdi, da si domačin", widget=forms.TextInput())

    class Meta:
        model = Comment
        fields = ['content', 'parent', 'captcha_answer']
        widgets = {
            'parent': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Generiraj random captcha vprašanje
        if self.request and self.request.method != 'POST':
            # Generiraj random captcha vprašanje samo, ko ni POST
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
            self.request.session['captcha_result'] = valid_answers[a]
        else:
            # Ko je POST, nastavi label iz session, da ne izgine
            if self.request:
                # Če captcha_result obstaja, nastavi label na pripadajoče vprašanje
                captcha_result = self.request.session.get('captcha_result')
                if captcha_result:
                    # Poišči index za label
                    questions = [
                        "Dve besedi in število:",
                        "Župan velemesta:",
                        "Reka, brezdomec:",
                        "Hrib z razglednim stolpom:"
                    ]
                    valid_answers = [
                        ["šentjur", "sentjur", "3230", "metropola"],
                        ["marko", "diaci"],
                        ["pešnica", "pešnca", "beco"],
                        ["resevna"]
                    ]
                    for i, answers in enumerate(valid_answers):
                        if answers == captcha_result:
                            self.fields['captcha_answer'].label = questions[i]
                            break

    def clean_captcha_answer(self):
        raw_answer = self.cleaned_data.get('captcha_answer', '')
        correct_answers = self.request.session.get('captcha_result', [])

        # Spucaj: vejice, pike, dvopičja, več presledkov
        cleaned_input = re.sub(r'[^a-zA-Z0-9čšžČŠŽ\s]', ' ', raw_answer.lower())
        user_inputs = [w.strip() for w in cleaned_input.split() if w.strip()]  # odstrani prazne vnose

        for word in user_inputs:
            if word not in correct_answers:
                raise forms.ValidationError("Nisi Šentjurčan.")
        return raw_answer