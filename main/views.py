from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from main.models import *
from .forms import *
from PIL import Image
from itertools import chain
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)


def home(request):
    return render(request, "main/home.html")


def index(request):
    most_recent_posts = Post.objects.order_by("-pub_date")[:3]
    context = {
        "most_recent_posts": most_recent_posts
    }
    if (request.method == "POST"):
        form = SearchForm(request.POST)
        if form.is_valid():
            search_result = form.cleaned_data["data"]
            return HttpResponseRedirect(reverse('main:result', kwargs={'search_result':search_result} ))
    return render(request, "main/index.html", context)


# def result(request, search_result):
#     result = search_result.strip()
#     word_list = result.split(" ")
#     post_set = set()
#     for word in word_list:
#         posts = Post.objects.all()
#         post_subset = set(post for post in posts if word.lower() in post.title.lower() or word.lower() in post.description.lower())
#         post_set = post_set.union(post_subset)
#     context = {
#         'search_result' : search_result,
#         'posts' : post_set
#     }
#     return render(request, "main/result.html", context)


class SearchResultView(ListView):
    model = Post 
    template_name = 'main/result.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        result = self.kwargs.get('search_result').strip()
        word_list = result.split(" ")
        post_set = Post.objects.filter(Q(title__icontains=word_list[0]) | Q(description__icontains=word_list[0]))
        for i in range(1, len(word_list)):
            post_subset = Post.objects.filter(Q(title__icontains=word_list[i]) | Q(description__icontains=word_list[i]))
            post_set = post_set.union(post_subset)
        return post_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['search_result'] = self.kwargs.get('search_result').strip()
        return context


class CartView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'main/cart.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        return user.cart.post_set.all().order_by("-pub_date")


@login_required
def clearCart(request):
    for post in request.user.cart.post_set.all():
        post.cart.remove(request.user.cart)
    request.user.cart.post_set.clear()
    messages.success(request, f'You have cleared your shopping cart.')
    return redirect('main:cart')


@login_required
def profile(request):
    def get_queryset(user):
        return Post.objects.filter(
            owner = user,
        ).order_by('-pub_date')
    most_recent_posts = request.user.post_set.all().order_by("-pub_date")[:1]
    unread_message_set = Message.objects.filter(read=False, receiver=request.user.username)
    if unread_message_set.count() != 0:
        messages.info(request, 'Your have ' + str(unread_message_set.count()) + ' unread messages.')

    unread_posts, post_to_unread_messages = [], {}
    for post in Post.objects.all():
        unread_count = post.message_set.filter(read=False, receiver=request.user.username).count()
        if unread_count != 0:
            unread_posts.append(post)
            post_to_unread_messages[post] = unread_count

    context = {
        'user' : request.user,
        'posts' : get_queryset(request.user),
        'most_recent_posts' : most_recent_posts,
        'unread_message_set' : unread_message_set,
        'unread_posts' : unread_posts,
        'dict' : post_to_unread_messages
    }
    return render(request, "main/profile.html", context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(data=request.POST, files=request.FILES, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('main:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'main/profile_edit.html', context)




def nonlogin_profile(request, username):
    try:
        user = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/nonlogin_profile.html', {"username_error" : "Username does not exist."})
    else:
        def get_queryset(in_user):
            return Post.objects.filter(
                owner = in_user,
            ).order_by('-pub_date')
        most_recent_posts = user.post_set.all().order_by("-pub_date")[:1]
        context = {
            'user' : user,
            'posts' : get_queryset(user),
            'most_recent_posts' : most_recent_posts,
        }
        return render(request, 'main/nonlogin_profile.html', context)


@login_required
def make_post(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        image_form = PostImageForm(request.POST, request.FILES)
        if form.is_valid():
            post_id_list = [0]
            for post in request.user.post_set.all():
                post_id_list.append(post.post_id)
            post = Post.objects.create(
                owner=request.user,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                price=form.cleaned_data["price"],
                post_id=max(post_id_list)+1,
                pickup_address=form.cleaned_data["pickup_address"],
                category=form.cleaned_data["post_category"],
            )
            coverImg = request.FILES.getlist('cover')
            if len(coverImg) > 0:
                post.cover = coverImg[0]
            post.save()
            images = request.FILES.getlist('images')
            for image in images:
                PostImage.objects.create(
                    post=post,
                    image=image,
                ).save()
            messages.success(request, f'You have created a new post! You can now view it in your profile.')
            return redirect('main:index')
    else:
        form = CreatePostForm()
        image_form = PostImageForm()
    return render(request, 'main/make_post.html', {'form': form, "image_form": image_form})


# def all_posts(request):
#     context = {
#         "posts": Post.objects.all().order_by('-pub_date')
#     }
#     return render(request, 'main/all_posts.html', context)

# def posts_30days(request):
#     posts = Post.objects.all().order_by('-pub_date')
#     post_list = [post for post in posts if post.was_published_in_30days()]
#     context = {
#         "posts": post_list
#     }
#     return render(request, 'main/posts_30days.html', context)

# def posts_180days(request):
#     posts = Post.objects.all().order_by('-pub_date')
#     post_list = [post for post in posts if post.was_published_in_180days()]
#     context = {
#         "posts": post_list
#     }
#     return render(request, 'main/posts_180days.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'main/all_posts.html'
    context_object_name = 'posts'
    ordering = ['-pub_date']
    paginate_by = 6


class PostListView30(ListView):
    model = Post
    template_name = 'main/posts_30days.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        selected_pub_date = [post.pub_date for post in Post.objects.all() if post.was_published_in_30days()]
        return Post.objects.filter(pub_date__in=selected_pub_date).order_by('-pub_date')


class PostListView180(ListView):
    model = Post
    template_name = 'main/posts_30days.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        selected_pub_date = [post.pub_date for post in Post.objects.all() if post.was_published_in_180days()]
        return Post.objects.filter(pub_date__in=selected_pub_date).order_by('-pub_date')


class PostListViewCategory(ListView):
    category_map = {
        'study_supplies' : 'Study Supplies',
        'daily_supplies' : 'Daily Supplies',
        'textbook' : 'Textbook',
        'furniture' : 'Furniture',
        'tickets' : 'Tickets',
        'electronics' : 'Electronics',
        'event_posts' : 'Event Posts',
        'music_instruments' : 'Music Instruments',
        'sublets' : 'Sublets',
        'rooms_shared' : 'Rooms/Shared',
        'housing_wanted' : 'Housing Wanted',
        'parking_storage' : 'Parking/Storage',
        'miscellaneous' : 'Miscellaneous',
        'lost_found' : 'Lost & Found',
        }
    model = Post
    template_name = 'main/by_category.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        inputCategory = self.kwargs.get('category')
        if inputCategory in self.category_map.keys():
            context['category'] = self.category_map[inputCategory]
        else:
            context['category_error'] = inputCategory + " is not a valid category."
        return context

    def get_queryset(self):
        inputCategory = self.kwargs.get('category')
        return Post.objects.filter(category=inputCategory.lower()).order_by('-pub_date')


# def by_category(request, category):
#     category_map = {
#         'study_supplies' : 'Study Supplies',
#         'daily_supplies' : 'Daily Supplies',
#         'textbook' : 'Textbook',
#         'furniture' : 'Furniture',
#         'tickets' : 'Tickets',
#         'electronics' : 'Electronics',
#         'event_posts' : 'Event Posts',
#         'music_instruments' : 'Music Instruments',
#         'sublets' : 'Sublets',
#         'rooms_shared' : 'Rooms/Shared',
#         'housing_wanted' : 'Housing Wanted',
#         'parking_storage' : 'Parking/Storage',
#         'miscellaneous' : 'Miscellaneous',
#         'lost_found' : 'Lost & Found',
#         }
#     posts = Post.objects.filter(category = category.lower())   
#     if category in category_map.keys():
#         return render(request, 'main/by_category.html', {"posts" : posts, "category" : category_map[category]}) 
#     else:
#         return render(request, 'main/by_category.html', {"category_error" : category + " is not a valid category."}) 


@login_required
def detail_post(request, username, post_id):
    try:
        owner = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Username does not exist."})
    else:
        try:
            post = owner.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            flag = (request.user == owner)
            context = {
                'owner': owner,
                'post': post,
                'flag': str(flag),
                'client': request.user
            }
            return render(request, 'main/detail_post.html', context)


@login_required
def addToCart(request, username, post_id):
    try:
        owner = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Post does not exist."})
    else:
        try:
            post = owner.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            if owner == request.user:
                messages.warning(request, f'You cannot add your own item to shopping cart.')
                return HttpResponseRedirect(
                        reverse('main:detail_post', kwargs={'username': username, 'post_id': post_id}))
            else:
                if post not in request.user.cart.post_set.all():
                    post.cart.add(request.user.cart)
                    request.user.cart.post_set.add(post)
                    messages.success(request, f'Your have added this item to your shopping cart!')
                    return HttpResponseRedirect(
                            reverse('main:detail_post', kwargs={'username': username, 'post_id': post_id}))
                else:
                    messages.success(request, f'This item is already in your shopping cart.')
                    return HttpResponseRedirect(
                        reverse('main:detail_post', kwargs={'username': username, 'post_id': post_id}))


@login_required
def removeFromCart(request, username, post_id):
    try:
        owner = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Post does not exist."})
    else:
        try:
            post = owner.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            if post not in request.user.cart.post_set.all():
                messages.warning(request, f'This item was not in your shopping cart.')
                return redirect('main:cart')
            else:
                request.user.cart.post_set.remove(post)
                post.cart.remove(request.user.cart)
                messages.success(request, f'You have removed this item from your shopping cart.')
                return redirect('main:cart')


@login_required
def update_post(request, username, post_id):
    try:
        user = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/update_post.html', {"username_error": "Username does not exist."})
    else:
        try:
            post = user.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/update_post.html', {"post_id_error": "Post does not exist."})
        else:
            context = {'username': username, 'post_id': post_id}
            if request.user == user:
                if request.method == 'POST':
                    form = UpdatePostForm(data=request.POST, instance=post)
                    image_form = PostImageForm(request.POST, request.FILES)
                    if form.is_valid():
                        form.save()
                        for postimage in post.postimage_set.all():
                            postimage.delete()
                        images = request.FILES.getlist('images')
                        for image in images:
                            PostImage.objects.create(
                                post=post,
                                image=image,
                            ).save()
                        coverImg = request.FILES.getlist('cover')
                        if len(coverImg) > 0:
                            post.cover = coverImg[0]
                            post.save()
                        messages.success(request, f'Your post has been updated!')
                        return HttpResponseRedirect(
                            reverse('main:detail_post', kwargs=context))
                else:
                    form = UpdatePostForm(instance=post)
                    image_form = PostImageForm()
                return render(request, 'main/update_post.html', {'form': form, "image_form": image_form})
            else:
                messages.warning(request,
                                 f'Username didn\'t match. Please log in the author\'s account to update this post')
                return HttpResponseRedirect(
                    reverse('main:detail_post', kwargs=context))


@login_required
def delete_post(request, username, post_id):
    try:
        user = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Username does not exist."})
    else:
        try:
            post = user.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            if request.user == user:
                context = {
                    'user': user,
                    'post': post,
                }
                return render(request, 'main/delete_post.html', context)
            else:
                messages.warning(request,
                                 f'Username didn\'t match. Please log in the author\'s account to delete this post')
                return HttpResponseRedirect(
                    reverse('main:detail_post', kwargs={'username': username, 'post_id': post_id}))


@login_required
def delete_done(request, username, post_id):
    try:
        user = CustomUser.objects.get(username=username)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Username does not exist."})
    else:
        try:
            post = user.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            if request.user == user:
                post.delete()
                messages.success(request, f'Your post has been deleted!')
                return redirect('main:profile')
            else:
                messages.warning(request,
                                 f'Username didn\'t match. Please log in the author\'s account to delete this post')
                return HttpResponseRedirect(
                    reverse('main:detail_post', kwargs={'username': username, 'post_id': post_id}))


@login_required
def leave_message(request, ownername, post_id, clientname):
    try:
        owner = CustomUser.objects.get(username=ownername)
    except (KeyError, CustomUser.DoesNotExist):
        return render(request, 'main/detail_post.html', {"username_error": "Username [" + str(ownername) + "] does not exist."})
    else:
        try:
            post = owner.post_set.get(post_id=post_id)
        except (KeyError, Post.DoesNotExist):
            return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
        else:
            try:
                client = CustomUser.objects.get(username=clientname)
            except (KeyError, CustomUser.DoesNotExist):
                return render(request, 'main/leave_message.html', {"clientname_error": "Username [" + str(clientname) + "] does not exist."})
            else:

                if client == owner:
                    err = "Owner cannot have a conversation with himself/herself/theirselves!"
                    return render(request, 'main/leave_message.html', {"self_conversation_error":err})

                elif  request.user == client or request.user == owner:
                    if request.method == 'POST':
                        form = MessageForm(request.POST)
                        if form.is_valid():
                            Message.objects.create(
                                sender = request.user,
                                receiver = ownername if request.user == client else clientname,
                                to_post = post,
                                time_sent = timezone.now(),
                                text = form.cleaned_data["text"],
                                read = False
                                ).save()
                            return HttpResponseRedirect(
                                reverse('main:leave_message', kwargs={'ownername': ownername,
                                    'post_id': post_id, 'clientname': clientname}))
                    else:
                        form = MessageForm()

                    unread_owner_messages = post.message_set.filter(sender=owner, receiver=clientname, read=False).order_by("time_sent")
                    unread_owner_messages_copy = post.message_set.filter(sender=owner, receiver=clientname, read=False)
                    read_owner_messages = post.message_set.filter(sender=owner, receiver=clientname, read=True)

                    unread_client_messages = post.message_set.filter(sender=client, receiver=ownername, read=False).order_by("time_sent")
                    unread_client_messages_copy = post.message_set.filter(sender=client, receiver=ownername, read=False)
                    read_client_messages = post.message_set.filter(sender=client, receiver=ownername, read=True)

                    other_messages_owner = read_owner_messages.union(unread_client_messages_copy, read_client_messages).order_by("time_sent")
                    other_messages_client = read_client_messages.union(unread_owner_messages_copy, read_owner_messages).order_by("time_sent")
                    if request.user == client:
                        for message in unread_owner_messages:
                            message.read = True
                            message.save()
                    else:
                        for message in unread_client_messages:
                            message.read = True
                            message.save()
                    message_set = unread_client_messages_copy.union(unread_owner_messages_copy, read_owner_messages, read_client_messages)
                    context = {"unread_owner_messages" : unread_owner_messages,
                                "unread_client_messages" : unread_client_messages,
                                "other_messages_owner" : other_messages_owner,
                                "other_messages_client" : other_messages_client,
                                "message_set" : message_set, "curr_user" : request.user,
                                "form" : form, "owner" : owner, "post" : post}
                    return render(request, 'main/leave_message.html', context)

                else:
                    err = 'Your username does not match with the username that sent messages!'
                    return render(request, 'main/leave_message.html', {"not_yours_error":err})


# @login_required
# def all_messages(request, ownername, post_id):
#     try:
#         owner = CustomUser.objects.get(username=ownername)
#     except (KeyError, CustomUser.DoesNotExist):
#         return render(request, 'main/detail_post.html', {"username_error": "Username [" + str(ownername) + "] does not exist."})
#     else:
#         try:
#             post = owner.post_set.get(post_id=post_id)
#         except (KeyError, Post.DoesNotExist):
#             return render(request, 'main/detail_post.html', {"post_id_error": "Post does not exist."})
#         else:
#             if request.user == owner:
#                 client_list = list(set(message.sender for message in post.message_set.all() if message.sender != owner))
#                 latest_message_text = []
#                 for client in client_list:
#                     latest_message = post.message_set.filter(Q(sender=client, receiver=owner.username) | 
#                     Q(sender=owner, receiver=client.username)).latest("time_sent")
#                     latest_message_text.append(latest_message.text)

#                 context = {
#                     "message_set" : post.message_set.filter(text__in=latest_message_text).order_by("-time_sent"),
#                     "owner" : owner,
#                     "post" : post,
#                     "true" : True,
#                 }
#                 return render(request, 'main/all_messages.html', context)
#             else:
#                 err = "You are not the owner of this post."
#                 return render(request, 'main/all_messages.html', {"not_owner_error":err})


class AllMessagesView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'main/all_messages.html'
    paginate_by = 5
    context_object_name = 'message_set'
    
    def get_queryset(self):
        owner = CustomUser.objects.get(username=self.kwargs.get('ownername'))
        post = owner.post_set.get(post_id=self.kwargs.get('post_id'))
        client_set = set(message.sender for message in post.message_set.all() if message.sender != owner)
        latest_message_text = []
        for client in client_set:
            latest_message = post.message_set.filter(Q(sender=client, receiver=owner.username) | 
            Q(sender=owner, receiver=client.username)).latest("time_sent")
            latest_message_text.append(latest_message.text)
        return post.message_set.filter(text__in=latest_message_text).order_by("-time_sent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        try:
            owner = CustomUser.objects.get(username=self.kwargs.get('ownername'))
        except (KeyError, CustomUser.DoesNotExist):
            context["username_error"] = "Username [" + self.kwargs.get('ownername') + "] does not exist."
            return context
        else:
            try:
                post = owner.post_set.get(post_id=self.kwargs.get('post_id'))
            except (KeyError, Post.DoesNotExist):
                context["post_id_error"] = "Post does not exist."
                return context
            else:
                context["owner"] = owner
                context["post"] = post
                context["true"] = True
                return context
