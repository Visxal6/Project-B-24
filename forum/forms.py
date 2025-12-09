from django import forms
from .models import Post
import logging

logger = logging.getLogger(__name__)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class PostForm(forms.ModelForm):    
    class Meta:
        model = Post
        fields = ['title', 'caption', 'tag', 'privacy']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter caption'}),
            'tag': forms.Select(attrs={'class': 'form-control'}),
            'privacy': forms.Select(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 50, 'class' : 'comment-input-text', 'placeholder' : 'Write a comment...'}))
