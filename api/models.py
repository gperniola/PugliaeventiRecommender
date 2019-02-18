from django.db import models
from .common import constant
from .common.utils import ChoiceEnum
#from recommender_webapp.models import Comune, Distanza, Place, Mood, Companionship, Event

# Create your models here.

DEFAULT_RATING = 3
DEFAULT_EVENT_PLACE = 0

class Mood(ChoiceEnum):
    __order__ = 'angry joyful sad'
    angry = 1
    joyful = 2
    sad = 3


class Companionship(ChoiceEnum):
    __order__ = 'withFriends alone'
    withFriends = 1
    alone = 2

class WeatherConditions(ChoiceEnum):
    __order__ = 'sereno poco_nuvoloso coperto pioggia nebbia neve temporale'
    sereno = 1
    poco_nuvoloso = 2
    coperto = 3
    pioggia = 4
    nebbia = 5
    neve = 6
    temporale = 7

class Utente(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 20, blank=False, unique=True)
    location = models.CharField(max_length=40)
    first_configuration = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'utenti'

    @classmethod
    def create(cls, username, location):
        utente = cls(username=username, location=location)
        return utente

    def __str__(self):
        return "{}".format(self.username)


class Comune(models.Model):
    istat = models.TextField(primary_key=True)
    nome = models.TextField(blank=True, null=True, db_column='comune')
    provincia = models.TextField(blank=True, null=True)
    regione = models.TextField(blank=True, null=True)
    prefisso = models.TextField(blank=True, null=True)
    cap = models.TextField(blank=True, null=True)
    cod_fis = models.TextField(blank=True, null=True)
    abitanti = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    link = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comuni'

class Distanza(models.Model):
    cittaA = models.TextField(blank=True, null=True, db_column='a')
    cittaB = models.TextField(blank=True, null=True, db_column='b')
    distanza = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    autoid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'distanze'


class Place(models.Model):
    placeId = models.AutoField(primary_key=True, db_column='pid')
    ext_id = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    name = models.TextField(blank=True, null=True, db_column='nomeposto')
    tipo = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True, db_column='comune')
    indirizzo = models.TextField(blank=True, null=True)
    latitudine = models.TextField(blank=True, null=True)
    longitudine = models.TextField(blank=True, null=True)
    telefono = models.TextField(blank=True, null=True)
    sitoweb = models.TextField(blank=True, null=True)
    chiusura = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    informale = models.SmallIntegerField(blank=True, null=True)
    raffinato = models.SmallIntegerField(blank=True, null=True)
    freeEntry = models.SmallIntegerField(blank=True, null=True, db_column='free_entry')
    benessere = models.SmallIntegerField(blank=True, null=True)
    bere = models.SmallIntegerField(blank=True, null=True)
    mangiare = models.SmallIntegerField(blank=True, null=True)
    dormire = models.SmallIntegerField(blank=True, null=True)
    goloso = models.SmallIntegerField(blank=True, null=True)
    libri = models.SmallIntegerField(blank=True, null=True)
    romantico = models.SmallIntegerField(blank=True, null=True)
    museo = models.SmallIntegerField(blank=True, null=True)
    spiaggia = models.SmallIntegerField(blank=True, null=True)
    teatro = models.SmallIntegerField(blank=True, null=True)
    arte = models.SmallIntegerField(blank=True, null=True)
    avventura = models.SmallIntegerField(blank=True, null=True)
    cinema = models.SmallIntegerField(blank=True, null=True)
    cittadinanza = models.SmallIntegerField(blank=True, null=True)
    musica_classica = models.SmallIntegerField(blank=True, null=True)
    geek = models.SmallIntegerField(blank=True, null=True)
    bambini = models.SmallIntegerField(blank=True, null=True)
    folklore = models.SmallIntegerField(blank=True, null=True)
    cultura = models.SmallIntegerField(blank=True, null=True)
    jazz = models.SmallIntegerField(blank=True, null=True)
    concerti = models.SmallIntegerField(blank=True, null=True)
    vita_notturna = models.SmallIntegerField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'luoghi'

    def labels(self):
        labels = ""
        if self.freeEntry == 1:
            labels += constant.FREE_ENTRY + ', '
        if self.bere == 1:
            labels += constant.BERE + ', '
        if self.mangiare == 1:
            labels += constant.MANGIARE + ', '
        if self.benessere == 1:
            labels += constant.BENESSERE + ', '
        if self.dormire == 1:
            labels += constant.DORMIRE + ', '
        if self.goloso == 1:
            labels += constant.GOLOSO + ', '
        if self.libri == 1:
            labels += constant.LIBRI + ', '
        if self.romantico == 1:
            labels += constant.ROMANTICO + ', '
        if self.museo == 1:
            labels += constant.MUSEO + ', '
        if self.spiaggia == 1:
            labels += constant.SPIAGGIA + ', '
        if self.teatro == 1:
            labels += constant.TEATRO + ', '
        return labels

    def __str__(self):
        return str(self.placeId) + '|' + self.name + '|' + self.location

class Valutazione(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Utente, on_delete=models.PROTECT, blank=False)
    mood = models.CharField(max_length=20, choices=Mood.choices(), blank=False)
    companionship = models.CharField(max_length=20, choices=Companionship.choices(), blank=False)
    place = models.ForeignKey(Place, on_delete=models.PROTECT, blank=False)
    rating = models.IntegerField(blank=False, default=3)

    @classmethod
    def create(cls, user, mood,companionship,place):
        valutazione = cls(user=user, mood=mood, companionship=companionship, place=place)
        return valutazione

    class Meta:
        managed = False
        db_table = 'valutazioni'


    def __str__(self):
        return str(self.user.username) + '|' + str(self.mood) + '|' + str(self.companionship) \
               + '|' + str(self.place.placeId) + '|' + str(self.rating)

class Event(models.Model):
    eventId = models.AutoField(primary_key=True, db_column='autoid')
    link = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True, db_column='titolo')
    posto_link = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True, db_column='posto_nome')
    date_from = models.DateTimeField(blank=True, null=True, db_column='data_da')
    date_to = models.DateTimeField(blank=True, null=True, db_column='data_a')
    comune = models.TextField(blank=True, null=True)
    free_entry = models.SmallIntegerField(blank=True, null=True)
    arte = models.SmallIntegerField(blank=True, null=True)
    avventura = models.SmallIntegerField(blank=True, null=True)
    cinema = models.SmallIntegerField(blank=True, null=True)
    cittadinanza = models.SmallIntegerField(blank=True, null=True)
    musica_classica = models.SmallIntegerField(blank=True, null=True)
    geek = models.SmallIntegerField(blank=True, null=True)
    bambini = models.SmallIntegerField(blank=True, null=True)
    folklore = models.SmallIntegerField(blank=True, null=True)
    cultura = models.SmallIntegerField(blank=True, null=True)
    jazz = models.SmallIntegerField(blank=True, null=True)
    concerti = models.SmallIntegerField(blank=True, null=True)
    teatro = models.SmallIntegerField(blank=True, null=True)
    vita_notturna = models.SmallIntegerField(blank=True, null=True)
    featured = models.SmallIntegerField(blank=True, null=True)
    descrizione = models.TextField(blank=True, null=True)
    popularity = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True, db_column='popolarita')
    description = models.TextField(blank=True, null=True, db_column='contenuto_html')
    meteo_bool = models.SmallIntegerField(blank=True, null=True)
    previsioni_bool = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eventi'

    def __str__(self):
        return str(self.eventId) + '|' + self.title + '|' + self.place + '|' \
            + self.date_from.strftime('%d/%m/%Y') + '|' + self.date_to.strftime('%d/%m/%Y')


class PrevisioniComuni(models.Model):
    autoid = models.AutoField(primary_key=True)
    idcomune = models.ForeignKey(Comune, models.DO_NOTHING, db_column='idcomune', blank=True, null=True)
    comune = models.TextField(blank=True, null=True)
    data = models.DateTimeField(blank=True, null=True)
    primavera = models.SmallIntegerField(blank=True, null=True)
    estate = models.SmallIntegerField(blank=True, null=True)
    autunno = models.SmallIntegerField(blank=True, null=True)
    inverno = models.SmallIntegerField(blank=True, null=True)
    sereno = models.SmallIntegerField(blank=True, null=True)
    coperto = models.SmallIntegerField(blank=True, null=True)
    poco_nuvoloso = models.SmallIntegerField(blank=True, null=True)
    pioggia = models.SmallIntegerField(blank=True, null=True)
    temporale = models.SmallIntegerField(blank=True, null=True)
    nebbia = models.SmallIntegerField(blank=True, null=True)
    neve = models.SmallIntegerField(blank=True, null=True)
    temperatura = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    velocita_vento = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    old = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'previsioni_comuni'

    def __str__(self):
        return str(self.comune) +"|"+str(self.data)+"|"+str(self.temperatura) + "°C"

    def get_condizioni(self):
        if self.sereno == 1: return WeatherConditions.sereno
        if self.coperto == 1: return WeatherConditions.coperto
        if self.poco_nuvoloso == 1: return WeatherConditions.poco_nuvoloso
        if self.pioggia == 1: return WeatherConditions.pioggia
        if self.temporale == 1: return WeatherConditions.temporale
        if self.nebbia == 1: return WeatherConditions.nebbia
        if self.neve == 1: return WeatherConditions.neve


class PrevisioniEventi(models.Model):
    autoid = models.AutoField(primary_key=True)
    link = models.TextField(blank=True, null=True)
    titolo = models.TextField(blank=True, null=True)
    dataevento = models.DateTimeField(blank=True, null=True)
    idevento = models.ForeignKey(Event, models.DO_NOTHING, related_name='previsioni_evento', db_column='idevento')
    idprevisione = models.OneToOneField(PrevisioniComuni, models.DO_NOTHING, related_name='previsione_comune', db_column='idprevisione')

    class Meta:
        managed = False
        db_table = 'previsioni_eventi'
