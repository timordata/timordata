# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-31 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('displayname', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'verbose_name_plural': 'Authors',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(blank=True, null=True, verbose_name='Year')),
                ('name', models.TextField(blank=True, null=True, verbose_name='name')),
                ('name_tet', models.TextField(blank=True, null=True, verbose_name='name')),
                ('name_en', models.TextField(blank=True, null=True, verbose_name='name')),
                ('name_pt', models.TextField(blank=True, null=True, verbose_name='name')),
                ('name_ind', models.TextField(blank=True, null=True, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('description_tet', models.TextField(blank=True, null=True, verbose_name='description')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='description')),
                ('description_pt', models.TextField(blank=True, null=True, verbose_name='description')),
                ('description_ind', models.TextField(blank=True, null=True, verbose_name='description')),
            ],
            options={
                'verbose_name_plural': 'Publications',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Pubtype',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('name_tet', models.CharField(max_length=128, null=True)),
                ('name_en', models.CharField(max_length=128, null=True)),
                ('name_pt', models.CharField(max_length=128, null=True)),
                ('name_ind', models.CharField(max_length=128, null=True)),
            ],
            options={
                'verbose_name_plural': 'Publication Types',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('name_tet', models.CharField(max_length=64, null=True, unique=True)),
                ('name_en', models.CharField(max_length=64, null=True, unique=True)),
                ('name_pt', models.CharField(max_length=64, null=True, unique=True)),
                ('name_ind', models.CharField(max_length=64, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Tags',
                'ordering': ('name', 'name_en'),
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(blank=True, max_length=256, null=True)),
                ('model_name', models.CharField(blank=True, max_length=256, null=True)),
                ('model_field', models.CharField(blank=True, max_length=256, null=True)),
                ('model_pk', models.CharField(blank=True, max_length=256, null=True)),
                ('resolution', models.IntegerField()),
                ('file_name', models.CharField(blank=True, max_length=256, null=True)),
                ('file_page', models.IntegerField(blank=True, default=0, null=True)),
                ('thumbnailPath', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
                ('description_tet', models.CharField(blank=True, max_length=256, null=True)),
                ('description_en', models.CharField(blank=True, max_length=256, null=True)),
                ('description_pt', models.CharField(blank=True, max_length=256, null=True)),
                ('description_ind', models.CharField(blank=True, max_length=256, null=True)),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('title_tet', models.CharField(blank=True, max_length=256, null=True)),
                ('title_en', models.CharField(blank=True, max_length=256, null=True)),
                ('title_pt', models.CharField(blank=True, max_length=256, null=True)),
                ('title_ind', models.CharField(blank=True, max_length=256, null=True)),
                ('upload', models.FileField(blank=True, max_length=256, null=True, upload_to='publications')),
                ('upload_tet', models.FileField(blank=True, max_length=256, null=True, upload_to='publications')),
                ('upload_en', models.FileField(blank=True, max_length=256, null=True, upload_to='publications')),
                ('upload_pt', models.FileField(blank=True, max_length=256, null=True, upload_to='publications')),
                ('upload_ind', models.FileField(blank=True, max_length=256, null=True, upload_to='publications')),
                ('cover', models.FileField(blank=True, max_length=256, null=True, upload_to='publication_covers')),
                ('cover_tet', models.FileField(blank=True, max_length=256, null=True, upload_to='publication_covers')),
                ('cover_en', models.FileField(blank=True, max_length=256, null=True, upload_to='publication_covers')),
                ('cover_pt', models.FileField(blank=True, max_length=256, null=True, upload_to='publication_covers')),
                ('cover_ind', models.FileField(blank=True, max_length=256, null=True, upload_to='publication_covers')),
                ('url', models.CharField(blank=True, max_length=256, null=True)),
                ('url_tet', models.CharField(blank=True, max_length=256, null=True)),
                ('url_en', models.CharField(blank=True, max_length=256, null=True)),
                ('url_pt', models.CharField(blank=True, max_length=256, null=True)),
                ('url_ind', models.CharField(blank=True, max_length=256, null=True)),
                ('journal', models.CharField(blank=True, max_length=128, null=True)),
                ('volume', models.CharField(blank=True, max_length=5, null=True)),
                ('issue', models.IntegerField(blank=True, null=True)),
                ('page_start', models.IntegerField(blank=True, null=True)),
                ('page_end', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Versions',
                'ordering': ('title',),
            },
        ),
    ]
