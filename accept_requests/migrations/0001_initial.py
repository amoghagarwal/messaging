# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FailedMessages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=512)),
                ('status', models.CharField(max_length=512, choices=[(b'queued', b'queued'), (b'sent', b'sent'), (b'delivered', b'delivered')])),
                ('message', models.CharField(max_length=1024)),
                ('retries', models.IntegerField(max_length=11)),
                ('callback_url', models.CharField(max_length=512)),
                ('created_time', models.DateTimeField(db_index=True, auto_now_add=True, null=True)),
                ('modified_time', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                'db_table': 'failed_messages',
            },
        ),
    ]
