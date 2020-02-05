from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from main import views as main_views
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url('^api/v1/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
    path("main/", include("main.urls")),
    path("", main_views.home, name="home"),
    path("users/", include("users.urls")),
    path("", include("django.contrib.auth.urls")),
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html'
        ),
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)