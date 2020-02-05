import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from users.models import CustomUser


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    joined_date = models.DateField(default=datetime.date.today)

    def __repr__(self):
        return str(self)

    def __str__(self):
        out = ""
        if self.user.first_name is not "":
            out += self.user.first_name
        if self.user.last_name is not "":
            out += " " + self.user.last_name
        if out is "":
            return self.user.username
        else:
            return out.strip()

    def send_message(self, to_post, text):
        # Create the message object.
        msg = Message.objects.create(from_who=self, to_post=to_post, text=text)
        msg.save()
        return msg

    def create_post(self, title: str, description: str, price: float):
        # Create the sales post object.
        post = Post.objects.create(title=title, owner=self, description=description, price=price, )
        post.save()
        return post


class Cart(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Post(models.Model):
    # The title or heading of a post.
    title = models.CharField(max_length=100, default="")
    # The owner of the post/object being sold.
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # A shopping cart can have multiple posts and a post can be in multiple shopping carts
    cart = models.ManyToManyField(Cart)
    # The description of the object being sold.
    description = models.TextField(max_length=3000, default="")
    # The date when the post is published
    pub_date = models.DateTimeField(default=timezone.now)
    # Price of the object in USD.
    price = models.DecimalField(max_digits=10, decimal_places=2)
    post_id = models.IntegerField(default=0)
    # Optional picture to go with the post.
    cover = models.ImageField(default='default-post.jpg', upload_to='post_pics')

    pickup_address = models.CharField(max_length=200, default="")

    category = models.CharField(max_length=30, default="")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.title} created by {str(self.owner)}"

    def was_published_in_30days(self):
        now = timezone.now()
        return now - datetime.timedelta(days=30) <= self.pub_date <= now

    def was_published_in_180days(self):
        now = timezone.now()
        return now - datetime.timedelta(days=180) <= self.pub_date <= now


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(default='default-post.jpg', upload_to='post_pics')


class Message(models.Model):
    # The message's sender.
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # # The message's target receiver
    receiver = models.CharField(max_length=15)
    # The post the message is in reply to.
    to_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # The time that the message was sent.
    time_sent = models.DateTimeField('date sent', default=timezone.now)
    # The message's actual body.
    text = models.TextField(max_length=350)
    # Has the message been read yet?
    read = models.BooleanField(default=False)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{str(self.sender)} to {str(self.to_post)}"
