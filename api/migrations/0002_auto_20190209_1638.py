# Generated by Django 2.1.5 on 2019-02-09 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='utente',
            table='utenti',
        ),
        migrations.AlterModelTable(
            name='valutazione',
            table='valutazioni',
        ),
    ]
