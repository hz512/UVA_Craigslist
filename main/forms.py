from django import forms
from django.forms import Textarea

from users.models import CustomUser
from .models import *


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'computing_id', 'email', 'phone_number', 'username', 'bio']
        widgets = {
            'bio': Textarea(attrs={'cols': 10, 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['bio'].required = False

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False


CATEGORY_CHOICES = [
    ('study_supplies', 'Study Supplies'),
    ('daily_supplies', 'Daily Supplies'),
    ('textbook', 'Textbook'),
    ('furniture', 'Furniture'),
    ('tickets', 'Tickets'),
    ('electronics', 'Electronics'),
    ('event_posts', 'Event Posts'),
    ('music_instruments', 'Music Instruments'),
    ('sublets', 'Sublets'),
    ('rooms_shared', 'Rooms/Shared'),
    ('housing_wanted', 'Housing Wanted'),
    ('parking_storage', 'Parking/Storage'),
    ('miscellaneous', 'Miscellaneous'),
    ('lost_found', 'Lost & Found'),
    ]

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'price', 'description', 'cover', 'pickup_address', 'post_category']
        labels = {'price': 'Price in USD', 'cover': "Upload a cover for your post"}

    pickup_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "1826 University Ave, Charlottesville, VA"}))

    post_category = forms.CharField(label='Select a category for your post', widget=forms.Select(choices=CATEGORY_CHOICES))

    def __init__(self, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields['cover'].required = False



class PostImageForm(forms.Form):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        label="Upload pictures for your post (up to 12)",
        required=False,
    )


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'price', 'description', 'cover', 'pickup_address', 'post_category']
        labels = {'price': 'Price in USD', 'cover': "<span style=\"font-size:12.5pt\">Upload a cover for your post</span>"}


    pickup_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': "1826 University Ave, Charlottesville, VA"}))
    post_category = forms.CharField(label='Select a category for your post', widget=forms.Select(choices=CATEGORY_CHOICES))
   
    def __init__(self, *args, **kwargs):
        super(UpdatePostForm, self).__init__(*args, **kwargs)
        self.fields['cover'].required = False



class SearchForm(forms.Form):
    data = forms.CharField(max_length=100)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        labels = {'text': ''}
        widgets = {
            'text': Textarea(attrs={'cols': 9, 'rows': 4}),
        }
