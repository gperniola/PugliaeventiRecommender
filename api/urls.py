from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AddUser, GetUserLocation, AddUserModel, FindPlaceRecommendations, FindEventRecommendations, getAllEvents

urlpatterns = {
		url(r'AddUser/$',AddUser.as_view()),
		url(r'GetUserLocation/$',GetUserLocation.as_view()),
		url(r'AddUserModel/$',AddUserModel.as_view()),
		url(r'FindPlaceRecommendations/$',FindPlaceRecommendations.as_view()),
		url(r'FindEventRecommendations/$',FindEventRecommendations.as_view()),
		url(r'getAllEvents/$',getAllEvents.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
