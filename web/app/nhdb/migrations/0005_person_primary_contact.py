# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-01 06:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("nhdb", "0004_auto_20160506_0610")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="primary_contact",
            field=models.BooleanField(default=False),
            preserve_default=False,
        )
    ]
