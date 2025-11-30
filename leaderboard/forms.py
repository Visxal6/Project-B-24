from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "start_at", "end_at", "location", "image"]
        widgets = {
            'start_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_at')
        end = cleaned.get('end_at')
        if start and end and end < start:
            self.add_error('end_at', 'End must be after start')
        return cleaned
