from django import forms
from .models import Post
import logging

logger = logging.getLogger(__name__)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'caption', 'image', 'tag', 'privacy']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter caption'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'tag': forms.Select(attrs={'class': 'form-control'}),
            'privacy': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_image(self):
        """Validate image field with logging."""
        image = self.cleaned_data.get('image')
        logger.debug(f"Validating image field: {image}")
        
        if image:
            logger.debug(f"Image file name: {image.name}, size: {image.size} bytes")
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                logger.warning(f"Image too large: {image.size} bytes")
                raise forms.ValidationError("Image file is too large (max 5MB)")
        else:
            logger.warning("Image field is empty/None")
            
        return image

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': 50, 'class' : 'comment-input-text', 'placeholder' : 'Write a comment...'}))
