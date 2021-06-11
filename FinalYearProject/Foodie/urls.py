from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url


urlpatterns = [
	path('content/',views.content_based,name="content"),
    path('content/<int:pageno>',views.content_based,name="content"),
	path('recommendations/', views.recommendation),
    #path('simrecommendations/', views.get_suggestions),
	path('related/',views.related,name="related"),
    path('related/<int:blog_id>',views.related,name="related"),
    path('', views.index),
	path('login_page/', views.login_page),
	path('signup_page/', views.signup_page),
	path('accounts/login/', views.login_page),
	path('accounts/signup/', views.signup_page),
	path('signup/', views.signup),
	path('login/', views.login),
	path('logout/', views.logout_view),
	path('profile/', views.profile),
	path('updateprofile/', views.updateprofile),
	path('search/', views.search),
	path('signup/', views.signup),
	path('create_post/', views.create_post),
	path('detail_post/<str:pk>/', views.detail_post , name="detail_post"),
	path('update_post/<str:pk>/', views.update_post),
	path('delete_post/<str:pk>/', views.delete_post),
	path('passwordchange/', views.passwordchange),
	path('addreview/<str:pk>/', views.addreview, name="addreview"),
	path('contact/', views.contactView, name='contact')
]


if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

