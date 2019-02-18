import csv
from datetime import datetime

from api.common import constant
from engine import lightfm_pugliaeventi
from recommender_webapp.initializer import data_loader
from api.models import Place, Distanza, Event


def add_user(user_id, user_location,  user_contexts, data):
    """
    Aggiunta di un nuovo utente al sistema di raccomandazione:
    Quando un nuovo utente si registra al sistema e completa la procedura di configurazione del profilo, oltre che
    memorizzare l'utente e i rating nel database Django, è necessario  memorizzare le informazioni anche nel dataset di
    LightFM (users.csv e ratings_train.csv). Successivamente è INDISPENSABILE apprendere nuovamente il modello. A tal
    scopo viene utilizzato il metodo learn_model del modulo lightfm_pugliaeventi.
    """

    lightfm_user_id = constant.DJANGO_USER_ID_BASE_START_LIGHTFM + user_id
    print("user_id: "  + str(user_id) + " --- django id: " + str(lightfm_user_id) + " --- user_loc: " + str(user_location) + " --- user_contexts: " + str(user_contexts) + " --- data: " + str(data))
    for user_context in user_contexts:
        contextual_lightfm_user_id = str(lightfm_user_id) + str(user_context.get('mood').value) + str(user_context.get('companionship').value)

        # Add user (SPLIT) to users.csv
        with open(r'engine/data/users.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([contextual_lightfm_user_id, user_location, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        contextual_ratings = data.filter(mood=user_context.get('mood').name, companionship=user_context.get('companionship').name)
        print ("contextual ratings: " + str(contextual_ratings))

        # Add ratings to ratings.csv
        with open(r'engine/data/ratings_train.csv', 'a') as f:
            writer = csv.writer(f)
            for rating in contextual_ratings:
                print ("writing rating: " +str(rating.rating) + " - place: " + str(rating.place.placeId) + " - id_user: " + str(contextual_lightfm_user_id))
                writer.writerow([contextual_lightfm_user_id, rating.place.placeId, rating.rating])

    # LightFM model recreation - NEW USER SIGN UP-> NEW MODEL
    lightfm_pugliaeventi.learn_model(force_model_creation=True)


def add_rating(contextual_lightfm_user_id, place_id, rating):
    """
    Aggiunta di un nuovo rating al sistema di raccomandazione:
    Quando un utente aggiunge un nuovo luogo al suo profilo (lo seleziona come valido in un determinato contesto),
    oltre che memorizzare il rating nel database Django, è necessario memorizzare le informazioni anche nel dataset di
    LightFM (ratings_train.csv).
    Diversamente dal caso precedente, in questo caso l'utente già esiste ed è presente nel modello LightFM. In tal caso,
    per aggiungere un rating per un utente specifico non è necessario apprendere nuovamente il modello. La funzione
    fit_partial del modello di LightFM consente di aggiungere al modello preesistente il rating per l'utente
    specificato. Tutto questo processo viene implementato all'interno del metodo add_rating_to_model del modulo
    lightfm_pugliaeventi. A tal metodo è necessario passare (oltre che ID utente, ID luogo e rating) l'attuale ID
    massimo utente e l'attuale ID massimo item (sono necessari in quanto LightFM costruisce una matrice di shape
    max_user_id x max_item_id).
    """

    # Add rating to ratings.csv
    with open(r'engine/data/ratings_train.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([contextual_lightfm_user_id, place_id, rating])

    max_user_id = 0
    max_item_id = 0
    # I need the max user ID and the max item ID
    with open(r'engine/data/users.csv') as csvfile:
        for row in reversed(list(csv.reader(csvfile, delimiter=','))):
            max_user_id = int(row[0])
            break
    with open(r'engine/data/items.csv') as csvfile:
        for row in reversed(list(csv.reader(csvfile, delimiter=','))):
            max_item_id = int(row[0])
            break

    # Add new rating to LightFM model
    lightfm_pugliaeventi.add_rating_to_model(max_user_id, max_item_id, contextual_lightfm_user_id, place_id, rating)


def find_recommendations(user, user_location, distance, any_events):
    """
    Ricerca di raccomandazioni utili per un utente specifico:
    Il seguente metodo consente di ricercare raccomandazioni per un utente specifico ed implementa anche operazioni di
    post-filtering sui risultati restituiti da LightFM. Mediante il metodo find_recommendations del modulo
    lightfm_pugliaeventi vengono recuperati gli id dei luoghi raccomandati. LightFM restituisce un lista in cui gli ID
    dei luoghi sono ordinati per rilevanza e di tale lista vengono prelevati solamente i primi 300 (costante
    NUM_RECOMMENDATIONS_FROM_LIGHTFM). A partire da ciascun ID, vengono prelevati gli oggetti Place dal DB Django.
    Successivamente, se l'utente ha selezionato la voce "any_events", significa che è interessato a luoghi in cui ci
    sono degli eventi in programma. Inoltre, se l'utente ha specificato un range di KM, è necessario procedere ad un
    ulteriore filtraggio dei luoghi in base alla distanza dalla location dell'utente.
    PS. I luoghi non sono caricati dal DB Django in questo istante, ma si sfrutta un dizionario di luoghi che viene
    caricato al momento dell'avvio di Django all'interno del modulo initializer.py. In questo modo è possibile
    restituire i risultati di raccomandazione in modo più efficiente.
    """
    print("PAGE IS: LIGHTFM_MANAGER.PY >> find_recommendations(" + str(user) + ", " + str(user_location) + ", " + str(distance) + ", " + str(any_events) + ")")
    recommended_places = []
    print("find_recommendations.calling data_loader.data_in_memory for places")
    places_dict = data_loader.data_in_memory['places_dict']
    user = int(user) - 1   # LightFM uses a zero-based indexing
    print("find_recommendations.calling lightfm_pugliaeventi.learn_model on model and data")
    model, data = lightfm_pugliaeventi.learn_model()
    #print("MODEL: " + str(model))
    #print("DATA: " + str(data))
    print("find_recommendations.calling lightfm_pugliaeventi.find_recommendations on user, model and data")
    recommendations = lightfm_pugliaeventi.find_recommendations(user, model, data)[:constant.NUM_RECOMMENDATIONS_FROM_LIGHTFM]
    recommendation_objects = []
    for index in recommendations:
        place_id = index + 1  # Because the LightFM zero-based indexing
        if place_id in places_dict:
            recommendation_objects.append(places_dict[place_id])

    ## DEBUG:
    print ("+ N. of places found: " + str(len(recommendation_objects)))
    if any_events:
        recommendations_with_events = []
        for place in recommendation_objects:
            if Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()).exists():
            #if Event.objects.filter(place=place.name).exists():
                recommendations_with_events.append(place)

        recommendation_objects = recommendations_with_events
    ## DEBUG:
    print ("+ N. of places found with current avaiable events: " + str(len(recommendation_objects)))

    if distance:
        locations_in_range = [distance[0] for distance in
                              Distanza.objects.filter(cittaA=user_location,
                                                      distanza__lte=distance).order_by('distanza').values_list('cittaB')]
        locations_in_range = [user_location] + locations_in_range
        for place in recommendation_objects:
            if place.location in locations_in_range:
                recommended_places.append(place)
            if len(recommended_places) == constant.NUM_RECOMMENDATIONS_TO_SHOW:
                break
    else:
        places_to_show = recommendation_objects[:constant.NUM_RECOMMENDATIONS_TO_SHOW]
        for place in places_to_show:
            recommended_places.append(place)

    ## DEBUG:
    print("+ N. of places found with events and in " + str(distance) +"km range: " + str(len(recommended_places)))
    print("+ Returning recommended_places")

    ####### DEBUG EVENTI ##########
    i = 1
    for place in recommended_places:
        if Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()).exists():
            print("+++++++++ " + place.name + " " +str(len(Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()))))
            for ev in Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()):
                print(str(i) + ") " + ev.title + "|" + ev.place + "|" + str(ev.comune) + "|" + str(ev.date_from) + " - " + str(ev.date_to))
                i = i + 1
    #print(len(Event.objects.filter(date_from__gte=datetime.today().date())))
    #print(len(Event.objects.filter(date_to__gte=datetime.today().date())))
    #print(len(Event.objects.filter(place__exact='', date_to__gte=datetime.today().date())))
    #print(len(Event.objects.filter(date_to__gte=datetime.today().date()).exclude(place__exact='')))
    #print(len(Event.objects.filter(place__exact='')))
    #print(len(Event.objects.exclude(place__exact='')))

    return recommended_places


def find_events_recommendations(user, user_location, distance, weather_conditions, no_weather_data):
    """
    #####
    Come il metodo find_recommendations, ma restituisce la lista degli eventi anziche' dei luoghi
    #####
    """
    print("PAGE IS: LIGHTFM_MANAGER.PY >> find_events_recommendations(" + str(user) + ", " + str(user_location) + ", " + str(distance) + ")")
    recommended_places = []
    places_dict = data_loader.data_in_memory['places_dict']
    user = int(user) - 1   # LightFM uses a zero-based indexing
    model, data = lightfm_pugliaeventi.learn_model()
    recommendations = lightfm_pugliaeventi.find_recommendations(user, model, data)[:constant.NUM_RECOMMENDATIONS_FROM_LIGHTFM]
    recommendation_objects = []
    for index in recommendations:
        place_id = index + 1  # Because the LightFM zero-based indexing
        if place_id in places_dict:
            recommendation_objects.append(places_dict[place_id])



    ## DEBUG:
    print ("+ N. of places found: " + str(len(recommendation_objects)))
    recommendations_with_events = []
    for place in recommendation_objects:
        if Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()).exists():
            #if Event.objects.filter(place=place.name).exists():
            recommendations_with_events.append(place)
    recommendation_objects = recommendations_with_events
    ## DEBUG:
    print ("+ N. of places found with current available events: " + str(len(recommendation_objects)))





    if distance:
        locations_in_range = [distance[0] for distance in
                              Distanza.objects.filter(cittaA=user_location,
                                                      distanza__lte=distance).order_by('distanza').values_list('cittaB')]
        locations_in_range = [user_location] + locations_in_range
        for place in recommendation_objects:
            if place.location in locations_in_range:
                recommended_places.append(place)
    else:
        for place in recommendation_objects:
            recommended_places.append(place)

    ## DEBUG:
    print("+ N. of places found with events and in " + str(distance) +"km range: " + str(len(recommended_places)))






    events = []
    for place in recommended_places:
        #max 3 events per place?
            for ev in Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()):
                events.append(ev)


    #if (len(events) > constant.NUM_RECOMMENDATIONS_TO_SHOW):
    #    print("+ Found " + str(len(events)) + " events, more than " + str(constant.NUM_RECOMMENDATIONS_TO_SHOW) +"... Getting only 3 events per place... ")
    #    events = []
    #    for place in recommended_places:
    #        for ev in Event.objects.filter(place=place.name, date_to__gte=datetime.today().date())[:3]:
    #            events.append(ev)


    ## DEBUG:
    print("+ N. of found events without weather filtering: " + str(len(events)))
    weather_filtered_events = []
    if weather_conditions > 0:
        max_weather = -1
        if weather_conditions == 1: max_weather = 4 #max pioggia
        if weather_conditions == 2: max_weather = 3 #max coperto
        if weather_conditions == 3: max_weather = 2 #max poco nuvoloso
        if weather_conditions == 4: max_weather = 1 #max sereno

        for ev in events:
                #prev = ev.previsioni_evento.all()
                previsioni_unfiltered = ev.previsioni_evento.all()
                prev = []
                for p in previsioni_unfiltered:
                        prev.append(p.idprevisione) #added
                if not prev and no_weather_data == 1: weather_filtered_events.append(ev) #aggiungi eventi senza previsioni meteo
                else:
                    for p in prev:
                        #print(str(p.idprevisione.get_condizioni().value))
                        if p.get_condizioni().value <= max_weather: #rmved
                            weather_filtered_events.append(ev)
                            break
    else:
        weather_filtered_events = events
    ## DEBUG:
    print("+ N. of events after weather filtering: " + str(len(weather_filtered_events)))

    recommended_events = []
    #for place in recommended_places:
        # MAX 2 EVENTS FOR EACH PLACE
    #    events = weather_filtered_events.filter(place=place.name, date_to__gte=datetime.today().date())[:2]
    #for event in events:
    for event in weather_filtered_events:
        recommended_events.append(event)
        if len(recommended_events) == constant.NUM_RECOMMENDATIONS_TO_SHOW:
            break

    print("+ N. of recommended events found: " + str(len(recommended_events)))
    print("+ Returning recommended_events")

    ####### DEBUG EVENTI ##########
    i = 1
    for ev in recommended_events:
        print(str(i) + ") +++ " + ev.title + "|" + ev.place + "|" + str(ev.comune) + "|" + str(ev.date_from) + " - " + str(ev.date_to))
        i = i + 1

    #for place in recommended_places:
    #    if Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()).exists():
    #        print("+++++++++ " + place.name + " " +str(len(Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()))))
    #        # MAX 2 EVENTS FOR EACH PLACE
    #        for ev in Event.objects.filter(place=place.name, date_to__gte=datetime.today().date()):
    #            print(str(i) + ") " + ev.title + "|" + ev.place + "|" + str(ev.comune) + "|" + str(ev.date_from) + " - " + str(ev.date_to))
    #            i = i + 1
    #print(len(Event.objects.filter(date_from__gte=datetime.today().date())))
    #print(len(Event.objects.filter(date_to__gte=datetime.today().date())))
    #print(len(Event.objects.filter(place__exact='', date_to__gte=datetime.today().date())))
    #print(len(Event.objects.filter(date_to__gte=datetime.today().date()).exclude(place__exact='')))
    #print(len(Event.objects.filter(place__exact='')))
    #print(len(Event.objects.exclude(place__exact='')))

    return recommended_events
