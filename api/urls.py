from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import AddUser, GetUserLocation, AddUserModel, FindPlaceRecommendations, FindEventRecommendations, getAllEvents, getAllPlaces, addRating, getRatings, getUserConfig, getComuni, getEventi, getLuoghi

urlpatterns = {
		url(r'AddUser/$',AddUser.as_view()),
		url(r'GetUserLocation/$',GetUserLocation.as_view()),
		url(r'AddUserModel/$',AddUserModel.as_view()),
		url(r'FindPlaceRecommendations/$',FindPlaceRecommendations.as_view()),
		url(r'FindEventRecommendations/$',FindEventRecommendations.as_view()),
		url(r'getAllEvents/$',getAllEvents.as_view()),
		url(r'getAllPlaces/$',getAllPlaces.as_view()),
		url(r'addRating/$',addRating.as_view()),
		url(r'getRatings/$',getRatings.as_view()),
		url(r'getUserConfig/$',getUserConfig.as_view()),
		url(r'getComuni/(?P<letters>[\w\s]+)$',getComuni.as_view()),
		url(r'getEventi/(?P<letters>[\w\s]+)$',getEventi.as_view()),
		url(r'getLuoghi/(?P<letters>[\w\s]+)$',getLuoghi.as_view()),
}

urlpatterns = format_suffix_patterns(urlpatterns)
