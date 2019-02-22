from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import datetime, timedelta
import datedelta

from .common import lightfm_manager, constant
#from recommender_webapp.models import Comune, Distanza, Place, Mood, Companionship, Event
from .models import Place, Mood, Companionship, Valutazione, Utente, Comune, Event, Distanza, PrevisioniEventi, PrevisioniComuni, WeatherConditions
from .serializers import UtenteSerializer, PlaceSerializer, EventSerializer, ValutazioneSerializer


def addUserDb(username, location):
    utente = Utente.create(username,location)
    utente.save()
    return str(utente.id)



# Create your views here.
class getUserConfig(APIView):
    def post(self, request, *args, **kwargs):
        username = str(request.data.get('username'))
        users = Utente.objects.filter(username=username)
        active_user = users[0]
        return JsonResponse({"first_config_done": active_user.first_configuration },safe=False, status=200)


def checkNumValutazioni(valutazioni):
    n_angry_withFriends = 0
    n_angry_alone = 0
    n_joyful_withFriends = 0
    n_joyful_alone = 0
    n_sad_withFriends = 0
    n_sad_alone = 0

    for v in valutazioni:
        if v.mood == "angry":
            if v.companionship == "alone":
                n_angry_alone = n_angry_alone + 1
            else:
                n_angry_withFriends = n_angry_withFriends + 1
        elif v.mood == "joyful":
            if v.companionship == "alone":
                n_joyful_alone = n_joyful_alone + 1
            else:
                n_joyful_withFriends = n_joyful_withFriends + 1
        else:
            if v.companionship == "alone":
                n_sad_alone = n_sad_alone + 1
            else:
                n_sad_withFriends = n_sad_withFriends + 1

    return (n_angry_withFriends, n_angry_alone, n_joyful_withFriends, n_joyful_alone, n_sad_withFriends, n_sad_alone)


class getRatings (APIView):
    def post(self, request, *args, **kwargs):
        username = str(request.data.get('username'))

        users = Utente.objects.filter(username=username)
        active_user = users[0]
        user_id = active_user.id
        first_config_done = active_user.first_configuration

        valutazioni = Valutazione.objects.filter(user=active_user)
        (n_angry_withFriends, n_angry_alone, n_joyful_withFriends, n_joyful_alone, n_sad_withFriends, n_sad_alone) = checkNumValutazioni(valutazioni)

        serializer = ValutazioneSerializer(instance=valutazioni, many=True)
        output = {"first_config_done":first_config_done, "n_angry_withFriends":n_angry_withFriends,
        "n_angry_alone":n_angry_alone, "n_joyful_withFriends":n_joyful_withFriends, "n_joyful_alone":n_joyful_alone,
        "n_sad_withFriends":n_sad_withFriends, "n_sad_alone":n_sad_alone, "valutazioni":serializer.data}
        return JsonResponse(output,safe=False, status=200)




class addRating (APIView):
    def post(self, request, *args, **kwargs):
        username = str(request.data.get('username'))
        place_id = int(request.data.get('place-id'))
        mood = str(request.data.get('emotion'))
        companionship = str(request.data.get('companionship'))

        users = Utente.objects.filter(username=username)

        user_id = users[0].id
        user_context_id = str(user_id + 100) + str(Mood[mood].value) + str(Companionship[companionship].value)

        place = Place.objects.filter(placeId=place_id)
        valutazione = Valutazione.create(users[0],mood,companionship,place[0])
        valutazione.save()

        #aggiungi al modello solo se il modello per l'utente esiste già (ovvero se ha completato la prima configurazione in precedenza)
        #altrimenti analizza le valutazioni in db per verificare se l'utente ha terminato la configurazione
        #nel caso abbia valutazioni a sufficienza per completare la configurazione, allora crea li modello utente
        if  users[0].first_configuration:
            print("+++ adding rating to user model")
            lightfm_manager.add_rating(user_context_id, place_id, 3)
        else:
            valutazioni_utente = Valutazione.objects.filter(user=users[0])
            (n_angry_withFriends, n_angry_alone, n_joyful_withFriends, n_joyful_alone, n_sad_withFriends, n_sad_alone) = checkNumValutazioni(valutazioni_utente)

            if n_angry_withFriends >= constant.RATINGS_PER_CONTEXT_CONF and n_angry_alone >= constant.RATINGS_PER_CONTEXT_CONF and n_joyful_withFriends >= constant.RATINGS_PER_CONTEXT_CONF and \
                n_joyful_alone >= constant.RATINGS_PER_CONTEXT_CONF and n_sad_withFriends >= constant.RATINGS_PER_CONTEXT_CONF and  n_sad_alone >= constant.RATINGS_PER_CONTEXT_CONF:

                users[0].first_configuration = True
                user_zero = Utente.objects.get(username=username)
                user_zero.first_configuration = True
                user_zero.save()

                user_contexts = []
                user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.withFriends})
                user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.alone})
                user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.withFriends})
                user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.alone})
                user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.withFriends})
                user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.alone})

                print("+++ creating new user model")
                lightfm_manager.add_user(users[0].id, users[0].location, user_contexts, valutazioni_utente)


        return Response(status=201)

class getAllPlaces(APIView):
    def post(self, request, *args, **kwargs):
        username = str(request.data.get('username'))
        location = str(request.data.get('location'))
        range = int(request.data.get('range'))
        only_with_events = int(request.data.get('only-with-events'))
        only_rated_places = int(request.data.get('only-rated-places'))

        users = Utente.objects.filter(username=username)
        user_id = users[0].id
        if location == '':
            location = users[0].location

        if only_rated_places == 1:
            eval_queryset = Valutazione.objects.filter(user=user_id)
            user_eval_places = []
            for e in eval_queryset:
                user_eval_places.append(e.place.placeId)
            filtered_places = Place.objects.filter(placeId__in=user_eval_places)

        else:
            locations_in_range = []
            if location != '':
                locations_in_range.append(location)
                if range > 0:
                    locations_queryset = Distanza.objects.filter(cittaA=location,distanza__lte=range).order_by('distanza')
                    for loc in locations_queryset:
                        locations_in_range.append(loc.cittaB)
                filtered_places = Place.objects.filter(location__in=locations_in_range).order_by('location', 'name')

            if only_with_events == 1:
                date_today = datetime.today().date()
                places_with_events = []
                for p in filtered_places:
                    if(Event.objects.filter(place=p.name, date_to__gte=date_today).exists()):
                        places_with_events.append(p.placeId)
                        #print(str(p.placeId) + " has events")
                filtered_places = filtered_places.filter(placeId__in=places_with_events)

        serializer = PlaceSerializer(instance=filtered_places, many=True, context={'user_location':location, 'user_id':user_id})
        return JsonResponse(serializer.data,safe=False, status=200)




class getAllEvents(APIView):
    def post(self, request, *args, **kwargs):
        location = str(request.data.get('location'))
        range = int(request.data.get('range'))
        days = str(request.data.get('days'))
        weather_conditions = int(request.data.get('weather'))
        no_weather_data = int(request.data.get('no-weather-data'))
        start_date_raw = (request.data.get('start-date'))
        end_date_raw = (request.data.get('end-date'))

        start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date()

        #offset = int(request.data.get('offset'))
        #date filter
        date_today = datetime.today().date()
        '''
        max_date = ''
         if days == '1d':
            max_start_date = date_today
        elif days == '7d':
            max_start_date = date_today + datedelta.datedelta(days=7)
        elif days == '1m':
            max_start_date = date_today + datedelta.datedelta(days=30)
        else:
            max_start_date = date_today + datedelta.datedelta(months=6)

        filtered_events = Event.objects.filter(date_to__gte=date_today, date_from__lte=max_start_date).order_by('date_to')
        '''
        filtered_events = Event.objects.filter(date_to__gte=start_date, date_from__lte=end_date).order_by('date_to')
        print(len(filtered_events))
        #location and range filter
        locations_in_range = []
        if location != '':
            locations_in_range.append(location)
            if range > 0:
                locations_queryset = Distanza.objects.filter(cittaA=location,distanza__lte=range).order_by('distanza')
                for loc in locations_queryset:
                    locations_in_range.append(loc.cittaB)

            filtered_events = filtered_events.filter(comune__in=locations_in_range)

        weather_filtered_events = []
        if weather_conditions > 0:
            max_weather = -1
            if weather_conditions == 1: max_weather = 4 #max pioggia
            if weather_conditions == 2: max_weather = 3 #max coperto
            if weather_conditions == 3: max_weather = 2 #max poco nuvoloso
            if weather_conditions == 4: max_weather = 1 #max sereno
            print("no_we: " + str(no_weather_data))

            for ev in filtered_events:
                #prev = ev.previsioni_evento.all()
                previsioni_unfiltered = ev.previsioni_evento.all()
                prev = []
                for p in previsioni_unfiltered:
                    if p.idprevisione.data.date() >= start_date and p.idprevisione.data.date() <= end_date:
                        print ("adding " + str(p.idprevisione))
                        prev.append(p.idprevisione) #added
                if not prev and no_weather_data == 1: weather_filtered_events.append(ev) #aggiungi eventi senza previsioni meteo
                else:
                    for p in prev:
                        #print(str(p.idprevisione.get_condizioni().value))
                        if p.get_condizioni().value <= max_weather: #rmved
                            weather_filtered_events.append(ev)
                            print(p.data) #rmved
                            break
                        else:
                            print("discarded: " + str(ev.eventId) + " " + str(p.get_condizioni())) #rmvd
        else:
            weather_filtered_events = filtered_events



        serializer = EventSerializer(instance=weather_filtered_events, many=True, context={'user_location':location})
        return JsonResponse(serializer.data,safe=False, status=201)




class GetUserLocation(APIView):
    def post(self,request,*args,**kwargs):
        username = str(request.data.get('username'))
        users = Utente.objects.filter(username=username)

        if not users:
            user_id = addUserDb(username,"")
            users = Utente.objects.filter(username=username)

        return Response(data={"user_location":str(users[0].location)})


class AddUser(APIView):
    def post(self,request,*args,**kwargs):
        '''mood_configuration = {}
        companionship_configuration = {}
        rated_places = []
        user_contexts = []'''


        username = str(request.data.get('username'))
        location = str(request.data.get('location'))
        user_id = addUserDb(username,location)

        '''user_ratings = Valutazione.objects.filter(user=utente.id)
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.alone})

        lightfm_manager.add_user(int(utente.id),str(location), user_contexts, user_ratings)'''
        return Response(data={"user_id":user_id})

class FindPlaceRecommendations(APIView):
    def post(self,request,*args,**kwargs):
        username = str(request.data.get('username'))
        location = str(request.data.get('location'))
        range = str(request.data.get('range'))
        mood = str(request.data.get('emotion'))
        companionship = str(request.data.get('companionship'))

        users = Utente.objects.filter(username=username)
        user_id = users[0].id

        if location == '':
            location = users[0].location
            range = 250

        user_context_id = str(user_id + 100) + str(Mood[mood].value) + str(Companionship[companionship].value)
        recs = lightfm_manager.find_recommendations(user_context_id,location,range,1)
        serializer = PlaceSerializer(instance=recs, many=True)
        #json = JSONRenderer().render(serializer.data)
        #print(json)
        #if serializer.is_valid():
            #serializer.save()
        return JsonResponse(serializer.data,safe=False, status=201)
        #return JsonResponse(serializer.errors, safe=False, status=400)

        #return JsonResponse({'foo':'bar'})
        #return Response(data={"recs":recs})
        #return Response(data={"foo":str(recs)})

class FindEventRecommendations(APIView):
    def post(self,request,*args,**kwargs):
        username = str(request.data.get('username'))

        location_filter = str(request.data.get('location'))
        range = str(request.data.get('range'))
        mood = str(request.data.get('emotion'))
        companionship = str(request.data.get('companionship'))
        weather_conditions = int(request.data.get('weather'))
        no_weather_data = int(request.data.get('no-weather-data'))

        users = Utente.objects.filter(username=username)
        user_id = users[0].id


        if location_filter == '':
            location = users[0].location
            range = 250
        else:
            location = location_filter

        user_context_id = str(user_id + 100) + str(Mood[mood].value) + str(Companionship[companionship].value)
        #recs = lightfm_manager.find_recommendations(user_context_id,location,60,1)
        recommended_events = lightfm_manager.find_events_recommendations(user_context_id,location,range, weather_conditions, no_weather_data)
        #for r in recommended_events:
        #    prev = r.previsionieventi_set.all()
        #    for p in prev:
        #        print(str(p.idprevisione))


        serializer = EventSerializer(instance=recommended_events, many=True, context={'user_location':location_filter})
        return JsonResponse(serializer.data,safe=False, status=201)



class AddUserModel(APIView):
    def post(self,request,*args,**kwargs):
        mood_configuration = {}
        companionship_configuration = {}
        rated_places = []
        user_contexts = []
        username = str(request.data.get('username'))
        utente = Utente.objects.filter(username=username)
        place = "boh"

        '''place = Place.objects.filter(placeId=78)
        valutazione = Valutazione.create(utente[0],"joyful","alone",place[0])
        valutazione.save()'''

        '''place = Place.objects.filter(placeId=80)
        valutazione = Valutazione.create(utente[0],"joyful","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=81)
        valutazione = Valutazione.create(utente[0],"joyful","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=82)
        valutazione = Valutazione.create(utente[0],"joyful","alone",place[0])
        valutazione.save()

        place = Place.objects.filter(placeId=83)
        valutazione = Valutazione.create(utente[0],"joyful","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=84)
        valutazione = Valutazione.create(utente[0],"joyful","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=85)
        valutazione = Valutazione.create(utente[0],"joyful","withFriends",place[0])
        valutazione.save()

        place = Place.objects.filter(placeId=86)
        valutazione = Valutazione.create(utente[0],"angry","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=87)
        valutazione = Valutazione.create(utente[0],"angry","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=88)
        valutazione = Valutazione.create(utente[0],"angry","alone",place[0])
        valutazione.save()

        place = Place.objects.filter(placeId=89)
        valutazione = Valutazione.create(utente[0],"angry","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=90)
        valutazione = Valutazione.create(utente[0],"angry","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=91)
        valutazione = Valutazione.create(utente[0],"angry","withFriends",place[0])
        valutazione.save()

        place = Place.objects.filter(placeId=92)
        valutazione = Valutazione.create(utente[0],"sad","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=93)
        valutazione = Valutazione.create(utente[0],"sad","alone",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=94)
        valutazione = Valutazione.create(utente[0],"sad","alone",place[0])
        valutazione.save()

        place = Place.objects.filter(placeId=95)
        valutazione = Valutazione.create(utente[0],"sad","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=96)
        valutazione = Valutazione.create(utente[0],"sad","withFriends",place[0])
        valutazione.save()
        place = Place.objects.filter(placeId=97)
        valutazione = Valutazione.create(utente[0],"sad","withFriends",place[0])
        valutazione.save()'''


        user_ratings = Valutazione.objects.filter(user=utente[0].id)
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.alone})

        lightfm_manager.add_user(utente[0].id,utente[0].location, user_contexts, user_ratings)

        return Response(data={"id":str(utente[0].id), "place":str(place)})













    '''queryset = Utente.objects.all()
    serializer_class = UtenteSerializer

    def perform_create(self, serializer):
        serializer.save()'''

'''class AddUser(APIView):
    def post(self,request,*args,**kwargs):
        mood_configuration = {}
        companionship_configuration = {}
        rated_places = []
        user_contexts = []

        email = str(request.data.get('email'))
        password = str(request.data.get('password'))
        location = str(request.data.get('location'))

        User.email = email
        User.set_password(password)
        User.save()

        location_found = Comune.objects.filter(nome__iexact=location)
        User.profile.location = location_found.first().nome
        User.save()

        user_ratings = Rating.objects.filter(user=int(request.data.get('userId')))
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.joyful, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.angry, 'companionship': Companionship.alone})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.withFriends})
        user_contexts.append({'mood': Mood.sad, 'companionship': Companionship.alone})

        lightfm_manager.add_user(int(request.data.get('userId')),str(request.data.get('location')), user_contexts, user_ratings)
        return Response(data={"result":"user " +  str(request.data.get('userId')) + " added"})'''
