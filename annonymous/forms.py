from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StudentProfile


# ─────────────────────────────────────────────
#  Register Form
# ─────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    full_name        = forms.CharField(max_length=100)
    email            = forms.EmailField()
    skills           = forms.CharField(help_text="Comma separated")
    interests        = forms.CharField(help_text="Comma separated")
    learning_goals   = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    experience_level = forms.ChoiceField(choices=[
        ('beginner',     'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced',     'Advanced'),
    ])

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user       = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user             = user,
                full_name        = self.cleaned_data['full_name'],
                skills           = self.cleaned_data['skills'],
                interests        = self.cleaned_data['interests'],
                learning_goals   = self.cleaned_data['learning_goals'],
                experience_level = self.cleaned_data['experience_level'],
            )
        return user


# ─────────────────────────────────────────────
#  Profile Update Form
# ─────────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = StudentProfile
        fields = ['full_name', 'bio', 'profile_picture', 'skills',
                  'interests', 'learning_goals', 'experience_level']
        widgets = {
            'bio':            forms.Textarea(attrs={'rows': 3}),
            'learning_goals': forms.Textarea(attrs={'rows': 3}),
        }


# ─────────────────────────────────────────────
#  Generate Path Form
# ─────────────────────────────────────────────
class GeneratePathForm(forms.Form):
    goal = forms.CharField(
        label="What do you want to learn?",
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': "e.g. I want to become a data scientist in 3 months. I know basic Python...",
        })
    )
