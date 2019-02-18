from rest_framework import serializers
from .models import Utente, Place, Event, Distanza, PrevisioniEventi, PrevisioniComuni

class UtenteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Utente
		fields = ('id', 'username', 'location', 'first_configuration')

class PlaceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Place
		fields = ('placeId', 'name', 'location')

class PrevisioniComuniSerializer(serializers.ModelSerializer):
	stagione = serializers.SerializerMethodField('get_stagione_giorno')
	condizioni = serializers.SerializerMethodField('get_condizioni_giorno')
	temp = serializers.SerializerMethodField('get_temp_giorno')
	vento = serializers.SerializerMethodField('get_vento_giorno')

	class Meta:
		model = PrevisioniComuni
		fields=['data','stagione', 'condizioni', 'temp', 'vento']

	def get_condizioni_giorno(self,obj):
		if obj.sereno == 1: return 'sereno'
		if obj.coperto == 1: return 'coperto'
		if obj.poco_nuvoloso == 1: return 'poco nuvoloso'
		if obj.pioggia == 1: return 'pioggia'
		if obj.temporale == 1: return 'temporale'
		if obj.nebbia == 1: return 'nebbia'
		if obj.neve == 1: return 'neve'

	def get_stagione_giorno(self,obj):
		if obj.inverno == 1: return 'inverno'
		if obj.primavera == 1: return 'primavera'
		if obj.estate == 1: return 'estate'
		if obj.autunno == 1: return 'autunno'

	def get_temp_giorno(self,obj):
		return int(obj.temperatura)

	def get_vento_giorno(self,obj):
		return int(obj.velocita_vento)


class PrevisioniEventiSerializer(serializers.ModelSerializer):
	bollettino = PrevisioniComuniSerializer(source='idprevisione')

	class Meta:
		model = PrevisioniEventi
		fields = ['bollettino']
		depth=3


class EventSerializer(serializers.ModelSerializer):
	titolo = serializers.SerializerMethodField('get_title')
	data_da = serializers.SerializerMethodField('get_date_from')
	data_a =  serializers.SerializerMethodField('get_date_to')
	posto_nome = serializers.SerializerMethodField('get_place')
	popolarita = serializers.SerializerMethodField('get_popularity')
	tags = serializers.SerializerMethodField('get_taglist')
	distanza = serializers.SerializerMethodField('get_distanza_AB')
	centro_distanza = serializers.SerializerMethodField('get_centro')
	previsioni_evento = PrevisioniEventiSerializer(many=True, read_only=True)

	class Meta:
		model = Event
		fields = ('eventId', 'titolo', 'descrizione', 'link', 'posto_nome', 'posto_link', 'comune', 'data_da' ,'data_a', 'popolarita', 'tags', 'distanza', 'centro_distanza', 'previsioni_evento')
		depth=3

	def get_title(self,obj):
		return obj.title

	def get_date_from(self,obj):
		return obj.date_from

	def get_date_to(self,obj):
		return obj.date_to

	def get_place(self,obj):
		return obj.place

	def get_popularity(self,obj):
		return int(obj.popularity)

	def get_centro(self,obj):
		user_location = self.context.get("user_location")
		if user_location != '':
			return user_location
		else: return ''

	def get_distanza_AB(self,obj):
		user_location = self.context.get("user_location")
		event_location = obj.comune
		if user_location != '' and user_location != event_location:
			distanza_AB = Distanza.objects.filter(cittaA=user_location, cittaB=event_location)
			return distanza_AB[0].distanza
		else: return ''



	def get_taglist(self,obj):
		tags = []
		if obj.free_entry == 1: tags.append('free entry')
		if obj.arte == 1: tags.append('arte')
		if obj.avventura == 1: tags.append('avventura')
		if obj.cinema == 1: tags.append('cinema')
		if obj.cittadinanza == 1: tags.append('cittadinanza')
		if obj.musica_classica == 1: tags.append('musica classica')
		if obj.geek == 1: tags.append('geek')
		if obj.bambini == 1: tags.append('bambini')
		if obj.folklore == 1: tags.append('folklore')
		if obj.cultura == 1: tags.append('cultura')
		if obj.jazz == 1: tags.append('jazz')
		if obj.concerti == 1: tags.append('concerti')
		if obj.teatro == 1: tags.append('teatro')
		if obj.vita_notturna == 1: tags.append('vita notturna')
		if obj.featured == 1: tags.append('featured')
		return tags
