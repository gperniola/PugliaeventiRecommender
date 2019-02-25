from operator import itemgetter
from django.db.models import Q
from datetime import datetime
from django.db.models import Max


from api.common import constant
from api.models import Place, Distanza, Event




N_OF_RECOMMENDATIONS = 10


def formula(emotion, empathy):
    return emotion + (emotion * empathy / 78)


def max_big_5(ope,con,ext,agr,neu):
    list = [ope, con, ext, agr, neu]
    max_index = list.index(min(list))
    if max_index == 0:
        return "ope"
    if max_index == 1:
        return "con"
    if max_index == 2:
        return "ext"
    if max_index == 3:
        return "agr"
    if max_index == 4:
        return "neu"

def prefiltering (user_location, distance, weather_conditions, no_weather_data):

    filtered_events = Event.objects.filter(date_to__gte=datetime.today().date())
    print("+++++[RULEBASED]: n. of filtered events by date: " + str(len(filtered_events)))
    if int(distance):
        locations_in_range = [distance[0] for distance in
                              Distanza.objects.filter(cittaA=user_location,distanza__lte=distance).order_by('distanza').values_list('cittaB')]

        locations_in_range = [user_location] + locations_in_range
        filtered_events = filtered_events.filter(comune__in=locations_in_range)
        print("+++++[RULEBASED]: n. of filtered events by range: " + str(len(filtered_events)))

    weather_filtered_events = []
    if weather_conditions > 0:
        max_weather = -1
        if weather_conditions == 1: max_weather = 4 #max pioggia
        if weather_conditions == 2: max_weather = 3 #max coperto
        if weather_conditions == 3: max_weather = 2 #max poco nuvoloso
        if weather_conditions == 4: max_weather = 1 #max sereno

        for ev in filtered_events:
                #prev = ev.previsioni_evento.all()
                previsioni_unfiltered = ev.previsioni_evento.all()
                prev = []
                for p in previsioni_unfiltered:
                        prev.append(p.idprevisione) #added
                if not prev and no_weather_data == 1: weather_filtered_events.append(ev.eventId) #aggiungi eventi senza previsioni meteo
                else:
                    for p in prev:
                        #print(str(p.idprevisione.get_condizioni().value))
                        if p.get_condizioni().value <= max_weather: #rmved
                            weather_filtered_events.append(ev.eventId)
                            break
    else:
        weather_filtered_events = filtered_events.values_list('eventId', flat=True)
    ## DEBUG:
    print("+++++[RULEBASED]: N. of events after weather filtering: " + str(len(weather_filtered_events)))

    #reconversion to queryset
    events = Event.objects.filter(eventId__in=weather_filtered_events)

    return events


def find_recommendations(data, location_filter, range, weather, no_weather_data):
    emp = float(data["behavior"]["empathy"])
    agr = float(data["behavior"]["agreeableness"])
    con = float(data["behavior"]["conscientiousness"])
    ext = float(data["behavior"]["extroversion"])
    neu = float(data["behavior"]["neuroticism"])
    ope = float(data["behavior"]["openness"])

    raw_topics = data["topics"]

    processed_words = 0
    topics=[]
    for t in raw_topics:
        t_name = t["key"].split("_")[0]

        #sport e travel appartengono alla stessa categoria
        if t_name == "sport" or t_name == "travel":
            t_name = "sport_or_travel"

        #controlla se il topic è già presente nella lista
        t_value = int(t["value"])
        processed_words = processed_words + t_value
        found = False
        for x in topics:
            if x["name"] == t_name:
                x["count"] = x["count"] + t_value
                found = True
        if found == False:
            topics.append({"name":t_name,"count":t_value})

    topics = sorted(topics, key=itemgetter('count'), reverse=True)



    filtered_events = prefiltering(location_filter, range, weather, no_weather_data)
    recommended_events = []
    resto_inserimenti = 0
    #### RULES

    for topic in topics:
        norm = int(round((topic["count"] * N_OF_RECOMMENDATIONS) / processed_words)) + resto_inserimenti
        resto_inserimenti = 0

        if topic["name"] == "tech":
            if formula(neu,emp) > 0.5547:
                evs = filtered_events.filter(geek=1, popularity__lt=180).distinct("title")
            elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                evs = filtered_events.filter(geek=1, popularity__gt=180).distinct("title")
            else:
                evs = filtered_events.filter(geek=1).distinct("title")


        elif topic["name"] == "sport_or_travel":
            if formula(neu,emp) > 0.5547:
                evs = filtered_events.filter(avventura=1, popularity__lt=180).distinct("title")
            elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                evs = filtered_events.filter(avventura=1, popularity__gt=180).distinct("title")
            else:
                evs = filtered_events.filter(avventura=1).distinct("title")


        elif topic["name"] == "politics":
            if formula(neu,emp) > 0.5547:
                evs = filtered_events.filter(cittadinanza=1, popularity__lt=180).distinct("title")
            elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                evs = filtered_events.filter(cittadinanza=1, popularity__gt=180).distinct("title")
            else:
                evs = filtered_events.filter(cittadinanza=1).distinct("title")


        elif topic["name"] == "music":
            max_name = max_big_5(ope,con,ext,agr,neu)
            if max_name == "ope":
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter( (Q(jazz=1) | Q(musica_classica=1)) & Q(popularity__lt=180) ).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter( (Q(jazz=1) | Q(musica_classica=1)) & Q(popularity__gt=180) ).distinct("title")
                else:
                    evs = filtered_events.filter( Q(jazz=1) | Q(musica_classica=1) ).distinct("title")

            elif max_name == "con":
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter( (Q(concerti=1) | Q(folklore=1)) & Q(popularity__lt=180) ).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter( (Q(concerti=1) | Q(folklore=1)) & Q(popularity__gt=180) ).distinct("title")
                else:
                    evs = filtered_events.filter( Q(concerti=1) | Q(folklore=1) ).distinct("title")

            elif max_name == "ext":
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter( (Q(concerti=1) | Q(folklore=1)) & Q(popularity__lt=180) ).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter( (Q(concerti=1) | Q(folklore=1)) & Q(popularity__gt=180) ).distinct("title")
                else:
                    evs = filtered_events.filter( Q(concerti=1) | Q(folklore=1) ).distinct("title")

            elif max_name == "agr":
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter( Q(concerti=1) & Q(popularity__lt=180) ).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter( Q(concerti=1) & Q(popularity__gt=180) ).distinct("title")
                else:
                    evs = filtered_events.filter(concerti=1).distinct("title")

            else:
                evs = filtered_events.filter(concerti=1, popularity__lt=180).distinct("title")


        elif topic["name"] == "style":
            if formula(ext,emp) > 0.715 or formula(ope,emp) > 0.7574:
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(vita_notturna=1, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(vita_notturna=1, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(vita_notturna=1).distinct("title")
            else:
                posti_raffinati = Place.objects.filter(raffinato=1)
                posti_nomi = []
                for p in posti_raffinati:
                    posti_nomi.append(p.name)

                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(place__in=posti_nomi, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(place__in=posti_nomi, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(place__in=posti_nomi).distinct("title")


        elif topic["name"] == "art":
            if formula(con,emp) > 0.6973 and formula(ext,emp) > 0.715:
                posti_libri = Place.objects.filter(libri=1)
                posti_nomi = []
                for p in posti_libri:
                    posti_nomi.append(p.name)

                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(place__in=posti_nomi, cultura=1, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(place__in=posti_nomi, cultura=1, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(place__in=posti_nomi, cultura=1).distinct("title")
            else:
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(arte=1, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(arte=1, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(arte=1).distinct("title")


        elif topic["name"] == "movie":
            if formula(con,emp) > 0.6973:
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(teatro=1, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(teatro=1, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(teatro=1, cultura=1).distinct("title")
            else:
                if formula(neu,emp) > 0.5547:
                    evs = filtered_events.filter(cinema=1, popularity__lt=180).distinct("title")
                elif formula(neu,emp) < 0.5547 or formula(ope,emp) < 0.7573:
                    evs = filtered_events.filter(cinema=1, popularity__gt=180).distinct("title")
                else:
                    evs = filtered_events.filter(cinema=1).distinct("title")


        else:
            print("topic not found")

        if len(evs) < norm:
            resto_inserimenti = norm - len(evs)

        evs = evs[:norm]
        print("+++++[RULEBASED]: N. of events found for topic "+topic["name"]+": " + str(len(evs)) + " (max " + str(norm) + ")")
        for e in evs:
            recommended_events.append(e)
        #recommended_events.sort(key=lambda x: x.date_to)

    return recommended_events
