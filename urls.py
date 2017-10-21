from django.conf.urls import url
from . import views

# for tests
urlpatterns = [
    url(r'^searchbox$', views.general_search, name='searchbox'),
    url(r'^search$', views.PaperSearchHitView.as_view(), name='search2'),
    url(r'^image$', views.PaperSearchHitImageView.as_view(), name='search3'),
    url(r'^list$', views.PaperList.as_view(), name='list'),
]
