# Generated by Django 2.1.7 on 2019-03-25 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_hobby'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='hobby',
            field=models.ManyToManyField(to='app01.Hobby', verbose_name='爱好'),
        ),
    ]