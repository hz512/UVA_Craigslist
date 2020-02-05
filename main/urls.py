from django.urls import path
from main import views as main_view
from django.conf import settings
from django.conf.urls.static import static

app_name = "main"

urlpatterns = [
    path('', main_view.index, name='index'),
    path("profile/", main_view.profile, name="profile"),
    path("cart/", main_view.CartView.as_view(), name="cart"),
    path("cart/clearcart", main_view.clearCart, name="clearCart"),
    path("profile/edit/", main_view.profile_edit, name="profile_edit"),
    path("makepost/", main_view.make_post, name="make_post"),
    path("allposts/", main_view.PostListView.as_view(), name="all_posts"),
    path("allposts/30days/", main_view.PostListView30.as_view(), name="posts_30days"),
    path("allposts/180days/", main_view.PostListView180.as_view(), name="posts_180days"),
    path("allposts/<str:category>/", main_view.PostListViewCategory.as_view(), name="by_category"),
    path("result=<str:search_result>/", main_view.SearchResultView.as_view(), name="result"),
    path("<str:username>/", main_view.nonlogin_profile, name="nonlogin_profile"),
    path("<str:username>/post_<int:post_id>/", main_view.detail_post, name="detail_post"),
    path("<str:username>/post_<int:post_id>/addtocart", main_view.addToCart, name="addToCart"),
    path("<str:username>/post_<int:post_id>/removefromcart", main_view.removeFromCart, name="removeFromCart"),
    path("<str:username>/post_<int:post_id>/update/", main_view.update_post, name="update_post"),
    path("<str:username>/post_<int:post_id>/delete/", main_view.delete_post, name="delete_post"),
    path("<str:username>/post_<int:post_id>/delete/done/", main_view.delete_done, name="delete_done"),
    path("<str:ownername>/post_<int:post_id>/all_messages/", main_view.AllMessagesView.as_view(), name="all_messages"),
    path("<str:ownername>/post_<int:post_id>/dialogue_with_<str:clientname>/", main_view.leave_message, name="leave_message"),
] 
