# Generated by Django 2.1.7 on 2019-03-25 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20190325_2143'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hobby',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='爱好')),
            ],
        ),
    ]