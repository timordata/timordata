# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhdb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempExcelDownloadFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email')),
                ('purpose', models.CharField(choices=[(b'PP', b'Freshman'), (b'RE', b'Sophomore'), (b'IN', b'Junior'), (b'OT', b'Senior')], max_length=2)),
                ('purposeother', models.CharField(max_length=150, verbose_name='Other purpose')),
                ('referralurl', models.CharField(max_length=256)),
            ],
        ),
    ]
