from django.contrib.auth.models import AbstractUser
from django.db import models
from main import models as main_models


class CustomUser(AbstractUser):
	email = models.EmailField(unique=True, default="")
	phone_number = models.CharField(max_length=20, default="")
	computing_id = models.CharField(max_length=10, default="")
	first_name = models.CharField(max_length=20, default="")
	last_name = models.CharField(max_length=20, default="")
	username = models.CharField(max_length=15, unique=True)
	bio = models.TextField(max_length=280, default="")
	image = models.ImageField(default='default.png', upload_to='profile_pics')
	
	def __str__(self):
		return self.username


	def send_message(self, to_post, text):
		# Create the message object.
		msg = main_models.Message.objects.create(sender=self, to_post=to_post, text=text)
		msg.save()
		return msg

	def create_post(self, title: str, description: str, price: float):
		# Create the sales post object.
		post = main_models.Post.objects.create(title=title, owner=self, description=description, price=price)
		post.save()
		return post

	