from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что у вас нового?'
            }),
        }
        labels = {
            'text': 'Текст поста',
            'image': 'Изображение'
        }
