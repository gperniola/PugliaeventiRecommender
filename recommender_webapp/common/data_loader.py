from recommender_webapp.common import constant
from api.models import Place
#from recommender_webapp.models import Place


class DataLoader:
    data_in_memory = {'places_dict': {}, 'places_list': [], 'place_feature': {}}

    def __init__(self):
        self.__load_data_from_db()

    def __load_data_from_db(self):
        print ("+++++ dataloader.load_data_from_db()")
        i = 0
        for place in Place.objects.all():
            self.data_in_memory['places_dict'][place.placeId] = place
            self.data_in_memory['places_list'].append(place)


            if place.freeEntry:
                self.data_in_memory['place_feature'][constant.FREE_ENTRY] = place
            if place.teatro:
                self.data_in_memory['place_feature'][constant.TEATRO] = place
            if place.spiaggia:
                self.data_in_memory['place_feature'][constant.SPIAGGIA] = place
            if place.museo:
                self.data_in_memory['place_feature'][constant.MUSEO] = place
            if place.romantico:
                self.data_in_memory['place_feature'][constant.ROMANTICO] = place
            if place.benessere:
                self.data_in_memory['place_feature'][constant.BENESSERE] = place
            if place.mangiare:
                self.data_in_memory['place_feature'][constant.MANGIARE] = place
            if place.bere:
                self.data_in_memory['place_feature'][constant.BERE] = place
            if place.dormire:
                self.data_in_memory['place_feature'][constant.DORMIRE] = place
            if place.goloso:
                self.data_in_memory['place_feature'][constant.GOLOSO] = place
            if place.libri:
                self.data_in_memory['place_feature'][constant.LIBRI] = place

        '''print ("LIBRI\n")
        print(str(self.data_in_memory['place_feature'][constant.LIBRI]) + "\n")
        print ("DORMIRE\n")
        print(str(self.data_in_memory['place_feature'][constant.DORMIRE]) + "\n")
        print ("MUSEO\n")
        print(str(self.data_in_memory['place_feature'][constant.MUSEO]) + "\n")
        print(str(i))
        print(str(self.data_in_memory['place_feature']))
        #print(str(len(self.data_in_memory)))
            #break
        #print(self.data_in_memory)

        data = {'a': {}, 'b': [], 'c': {}}
        data['a'][3] = "x1"
        data['b'].append("x1")
        data['c']['c3'] = "x1"
        data['a'][1] = "x2"
        data['b'].append("x2")
        data['c']['c1'].append("x2")
        data['c']['c1'].append("x3")



        print(data['a'])
        print(data['b'])
        print(data['c'])
        print(data['c']["c1"])
        print(data)'''
        #print(self.data_in_memory['place_feature'])
