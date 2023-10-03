# Generated by Django 4.2.4 on 2023-10-03 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contacts',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contacts',
            name='is_muted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mediamessage',
            name='image_blurhash',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='mediamessage',
            name='media_type',
            field=models.CharField(choices=[('DOCUMENT', 'Document'), ('AUDIO', 'Audio'), ('VIDEO', 'Video'), ('IMAGE', 'Image'), ('DEFAULT', 'None')], default='DEFAULT'),
        ),
        migrations.AddField(
            model_name='message',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='is_deleted_for_me',
            field=models.BooleanField(default=False),
        ),
    ]