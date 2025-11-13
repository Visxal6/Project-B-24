from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'caption', 'image', 'tag']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter caption'}),
            'tag': forms.Select(attrs={'class': 'form-control'}),
        }
