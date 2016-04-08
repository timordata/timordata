import json
from django.core.urlresolvers import reverse
from django.db.models import F, Count, Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render
from django.template import RequestContext
from django.utils.safestring import mark_safe
from nhdb.models import PropertyTag, Organization
import os
from suggest.models import Suggest, AffectedInstance
from tables import PublicationTable, VersionTable
from models import Author, Publication, Pubtype, Tag, Version
from django_tables2 import SingleTableView, RequestConfig
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from forms import *
import warnings
from library import forms as library_forms, forms_delete as library_forms_delete
from django.apps import apps

def index(request):
    return render(request, 'library/index.html')



def thumbnail(request, app_name, model_name, pk, res=150):
    try:
        t = Thumbnail.make(instance = apps.get_model(app_name, model_name).objects.get(pk = pk), res=int(res))
    except:
        return HttpResponseNotFound()
    return HttpResponse(mark_safe(t.img))



class PublicationList(SingleTableView):

    model = Publication
    table_class = PublicationTable
    table_pagination={'per_page':50}

    def get_context_data(self, **kwargs):
        context = super(PublicationList, self).get_context_data(**kwargs)
        context['lang'] = self.request.LANGUAGE_CODE

        context['filters'] = {
            'language_id': [{'value':s[0], 'label':s[1]} for s in settings.LANGUAGES_FIX_ID],
            'tag__id': Tag.objects.all(),
            'sector__path': PropertyTag.objects.filter(path__startswith='INV.'),
            'pubtype': [{'value':p.pk, 'label':p.name} for p in Pubtype.objects.exclude(code='PRI')],
            'org': [{'value':o.pk, 'label':u'{}'.format(o.name)} for o in Organization.objects.annotate(
                num_publications = Count('publication')).filter(num_publications__gt=0)],
            }

        context['activefilters'] = {}

        for f in context['filters'].keys():

            if self.request.GET.getlist(f) != []:

                context['activefilters'][f] = self.request.GET.getlist(f)

        # ID numbers need to be numeric

        for f in 'tag__id', 'org':
            if self.request.GET.getlist(f) != []:
                try:
                    context['activefilters'][f] = [int(i) for i in context['activefilters'][f]]
                except ValueError, e:
                    pass

        if len(self.request.GET.getlist('org')) > 0:
            try:
                context['org'] = Organization.objects.filter(pk__in = self.request.GET.getlist('org'))
            except ValueError:
                context['org'] = Organization.objects.none()
        context['activefilters']['primarysource'] = self.request.GET.get('primarysource') or 'false'
        context['dashboard'] = self.get_dashboard(context['object_list'])
        context['object_class_count'] = PublicationList.model.objects.count()

        return context

    def get_dashboard(self, objects):
        dashboard = {}

        # Count response for each individual tag

        if len(self.request.GET.getlist('tag__id')) > 1:
            dashboard['tags'] = {}
            for tag_id in self.request.GET.getlist('tag__id'):
                tag = Tag.objects.get(pk = tag_id)
                dashboard['tags'][tag.name] = objects.filter(versions__tag = tag).distinct().count()

        if len(self.request.GET.getlist('sector__path')) > 1:
            dashboard[PropertyTag.objects.get(path='INV')] = {}
            for tag_id in self.request.GET.getlist('sector__path'):
                tag = PropertyTag.objects.get(path = tag_id)
                dashboard[PropertyTag.objects.get(path='INV')][tag] = objects.filter(versions__sector = tag).distinct().count()

        if len(self.request.GET.getlist('org')) > 1:
            orgs = Organization.objects.filter(pk__in = self.request.GET.getlist('org')).filter(publication__in = objects).annotate(
                num_publications = Count('publication'))
            dashboard['organizations'] = {}
            for o in orgs:
                dashboard['organizations'][o] = o.num_publications
        return dashboard

    def get_queryset(self):
        GET = self.request.GET
        filters = {}
        params = ('org', 'pubtype')
        version_params = ('tag__id',)
        version_filter_terms = ("sector__path", "activity__path", "beneficiary__path")

        for param in version_params:

            if GET.getlist(param):
                filters['versions__'+param+'__in'] = GET.getlist(param)

        for param in params:

            if GET.getlist(param):

                # Rewrite shorthand requests here
                if param == 'org':
                    _param = 'organization'
                else:
                    _param = param

                filters[_param+'__in'] = GET.getlist(param)

        years = GET.getlist('year')
        if years:
            param = 'year'
            if len(years) == 1:
                filters[param+'__in'] = GET.getlist(param)
            elif len(years) >= 2:
                filters[param+'__gte'] = min([int(i) for i in GET.getlist(param)])
                filters[param+'__lte'] = max([int(i) for i in GET.getlist(param)])

        for term in version_filter_terms:
            if GET.getlist(term):
                filters["versions__"+term+'__in'] = [PropertyTag.separatestring(i).upper() for i in self.request.GET.getlist(term)]

        languages = Q()
        language_ids = GET.getlist('language_id')
        for language_id in language_ids:
            kw = {'versions__title_'+language_id+'__isnull': False, 'versions__title_'+language_id+'__icontains': ' '}
            languages = languages | Q(**kw)
        try:

            objects = Publication.objects.filter(**filters).filter(languages).distinct()

        except ValueError, e:
            objects = Publication.objects.all()

        text = GET.get('q.text') or GET.get('text')
        if text:
            q = Q()
            for lang, lang_name in LANGUAGES_FIX_ID:
                for fieldname in ['name', 'description', 'versions__description', 'versions__title']:
                    k = {fieldname+'_'+lang+'__icontains': text}
                    q = q | Q(**k)
            # raise AssertionError, q
            objects = objects.filter(q)

        primarysource = self.request.GET.get('primarysource') or 'false'

        if primarysource == 'false': # Default
            objects = objects.exclude(pubtype = 'PRI')
        if primarysource == 'true':
            pass
        if primarysource == 'only':
            objects = objects.filter(pubtype = 'PRI')

        return objects.prefetch_related('author')\
            .prefetch_related('organization')\
            .prefetch_related('pubtype')


def project_table_excel(request):
    pass

def version_thumbnail_nginx(request):

    '''
    NGINX is set up to forward a request for "thumbnail does not exist"
    :param request:
    :return:
    '''
    # Example request:
    # https://localhost/nhdb/thumbnail/?request=/media/publication_pages/150/en/07-057r7_Web_Map_Tile_Service_Standard_PRBxiHh_Stpcw2r_1.jpg

    r = request.GET.get('request')

    x, root, d, res, lang, filename = r.split('/')

     #    ['',
     # 'media',
     # 'publication_pages',
     # '150',
     # 'en',
     # '07-057r7_Web_Map_Tile_Service_Standard_PRBxiHh_Stpcw2r_1.jpg']

    if d == "publication_pages":

        page = int(filename.split('_')[-1][:-4]) # Cut off the last underscore + digit (page number)
        filename = filename[0:-1*(len(filename.split('_')[-1]))-1]

        kw = {'upload_{}__icontains'.format(lang):filename}

        version = Version.objects.filter(**kw).first()
        # t = Version.objects.filter(**kw).first().thumbnail_to_res(language=lang)

        if not version:
            return HttpResponseNotFound(open('/webapps/project/media/404.jpg').read(), content_type='image/jpg')
        t = version.page_image(page=page, language=lang, res=res )
        return HttpResponse(open(t).read(), content_type='image/jpg')

    elif d == "publication_covers":

        filename = filename[0:-1*(len(filename.split('_')[-1]))-1]

        kw = {'cover_{}__icontains'.format(lang):filename}

        version = Version.objects.filter(**kw).first()
        # t = Version.objects.filter(**kw).first().thumbnail_to_res(language=lang)

        if not version:
            return HttpResponseNotFound(open('/webapps/project/media/404.jpg').read(), content_type='image/jpg')
        t = version.page_image(language=lang, res=res, root="/webapps/project/media/publication_covers/", page="cover")
        return HttpResponse(open(t).read(), content_type='image/jpg')


def version_thumbnail(request, version_pk, language='en'):
    '''
    Returns URL for a version thumbnail, creates it if nonexistant;
    Intended to reduce waiting times for big Publications
    :param request:
    :param version_pk:
    :return:
    '''
    _g = request.GET.get
    kw = {
        'res':_g('res', 150),
        '_format':_g('format', 'jpg')
    }

    if kw['_format'] not in ('jpg','png','gif','jpeg','pdf'):
        kw['_format'] = 'jpg'

    try:
        kw['res'] = int(kw['res'])
        if kw['res'] < 150:
            kw['res'] = 150
        elif kw['res'] > 1000:
            kw['res'] = 1000
    except ValueError:
        kw['res'] = 150

    try:
        v = Version.objects.get(pk=version_pk)
        print kw
        t = v.thumbnail(language=language, **kw)
        if t.get('image-errors'):
            raise AssertionError('Could not generate thumbnail: %s'%t['image-errors'])
        thumbnail = t[language]['thumbnail']
        return HttpResponse(open(thumbnail.thumbnailPath).read(), content_type='image/'+kw['_format'])

    except:
        raise


def version_page(request, pk, page, language):
    version = Version.objects.get(pk = pk)
    res = request.GET.get('size', 150)
    p = version.page_image(page=page, language=language, res=res )
    return HttpResponse(open(p).read(), content_type='image/jpg')


def suggested_publication(request, suggestion_pk):

    context = {}
    context['suggestion'] = Suggest.objects.get(pk=suggestion_pk)

    return render(request, 'library/suggested_publication.html', context)


class PublicationDetail(DetailView):

    model = Publication

    # def get_context_data(self, **kwargs):
    #     context = super(PublicationDetail, self).get_context_data(**kwargs)
    #
    #     context['versions'] = {}
    #     languagecodes = ['en','tet','pt','id']
    #
    #     for v in self.object.versions.all():
    #         context['versions'][v.id] = {}
    #         count = 0
    #         any_upload_exists = False
    #         for lc in languagecodes:
    #             if not v.has_language(lc):
    #                 continue
    #             count = count+1
    #             upload =  getattr(v, 'upload_%s' % lc)
    #             cover =  getattr(v, 'cover_%s' % lc)
    #             if upload.name:
    #                 upload_exists = True
    #                 any_upload_exists = True
    #             else:
    #                 upload_exists = False
    #
    #             version_details = {
    #                 'pk':v.pk,
    #                 'upload':upload,
    #                 'url': getattr(v, 'url_%s' % lc),
    #                 'upload_exists': upload_exists,
    #                 'cover': getattr(v, 'cover_%s' % lc),
    #                 'title': getattr(v, 'title_%s' % lc),
    #                 # 'thumb': v.thumbnail_to_res(languages=[lc]),
    #                 'description': getattr(v, 'description_%s' % lc),
    #                 'staticthumbnailurl': u'/media/publication_pages/150/{}/{}_0.jpg'.format(lc, os.path.splitext(os.path.split(upload.name)[1])[0])
    #             }
    #             try:
    #                 if getattr(v, 'cover_%s' % lc) \
    #                 and getattr(v, 'cover_%s' % lc) != '' \
    #                 and os.path.exists(v.cover_en.path):
    #                     version_details['staticthumbnailurl'] = u'/media/publication_covers/150/{}/{}.jpg'.format(lc, os.path.splitext(os.path.split(cover.name)[1])[0])
    #             except ValueError: # Occurs when a file is not associated with the field
    #                 pass
    #
    #             context['versions'][v.id][lc] = version_details
    #         for lc in context['versions'][v.id].keys():
    #             if count == 1:
    #                 context['versions'][v.id][lc]['class'] = 'col-lg-12 col-sm-12 col-xs-12'
    #             if count == 2:
    #                 context['versions'][v.id][lc]['class'] = 'col-lg-6 col-sm-6 col-xs-12'
    #             if count == 3:
    #                 context['versions'][v.id][lc]['class'] = 'col-lg-4 col-sm-4 col-xs-12'
    #             if count == 4:
    #                 context['versions'][v.id][lc]['class'] = 'col-lg-3 col-sm-3 col-xs-12'
    #
    #             if any_upload_exists:
    #                 context['versions'][v.id][lc]['class'] += 'with-image'
    #     return context


def publicationdashboard(request):
    context = {}

    try:
        context['suggestion'] = Suggest.objects.get(pk = request.GET.get('suggestion'))
    except:
        context['suggestion'] = request.GET.get('suggestion')

    try:
        context['publication'] = Publication.objects.get(pk = request.GET.get('publication'))
    except:
        context['publication'] = request.GET.get('publication')

    return render(request, 'library/publication_dashboard.html', context)


def form(request, model, form='main'):

    args = {}
    f = None
    g = request.GET.get
    p = request.GET.get

    template = 'nhdb/crispy_form.html'

    for m in Publication, Version, Organization, Suggest, Pubtype:
        m_name = m._meta.model_name

        if g(m_name):
            args[m_name] = m.objects.get(pk = g(m_name))

        # Use an underscore to indicate a suggestion ID
        if g('_'+m_name):
            args[m_name] = Suggest.objects.get(pk = g('_'+m_name))
            # args['initial'] = Suggest.objects.get(pk = g('_'+m_name)).data_jsonify()

    # if model in args:
    #     args['instance'] = args[model]

    if model == 'publication':
        if form == 'main':
            f = PublicationForm
        if form == 'organization':
            f = PublicationOrganizationForm
        if form == 'author':
            f = PublicationAuthorForm
        if form == 'version':
            f = VersionForm
        # if form == 'delete':
        #     f = PublicationDeleteForm

    if model == "version":
        if form == "main":
            f = VersionForm
        # elif form == "delete":
        #     f = VersionDeleteForm

    if f:
        return render(request, template, {'form': f(**args)})

    else:
        if form == 'main':
            f_name = '%sForm' % model.title()
        elif form == 'delete':
            f_name = '%s%sForm' % (model.title(), 'Delete')
            if hasattr(library_forms_delete, f_name):
                f = getattr(library_forms_delete, f_name)
                return render(request, template, {'form': f(**args)})


        else:
            f_name = '%s%sForm' % (model.title(), form.upper())

        if hasattr(library_forms, f_name):
            f = getattr(library_forms, f_name)
            return render(request, template, {'form': f(**args)})

        # Else if there's a case error, try to match the name anyway
        for i in  dir(library_forms):
            if i.lower() == f_name.lower():
                f = getattr(library_forms, i)
                return render(request, template, {'form': f(**args)})

    return HttpResponseBadRequest(
        mark_safe("<form>Class library.forms.{} is not defined yet</form>".format(f_name)))


def suggested_publications(request):
    '''
    List of suggested additions: enrty point to create a new pub or modify an existing one (ie add / change version,
    organization, author etc)
    :param request:
    :return:
    '''
    context = {}
    context['suggestions'] = Suggest.objects.filter(affectedinstance__in = AffectedInstance.objects.filter(primary=True, model_name='library_publication'), action="CM")
    return render(request, 'library/suggested_publications.html', context)


class AuthorCreate (CreateView):
    model = Author


class PublicationDelete(DeleteView):

    model = Publication


class VersionDetail(DetailView):

    model = Version

    def get_context_data(self, **kwargs):
        context = super(VersionDetail, self).get_context_data(**kwargs)

        context['version_language'] = []
        languagecodes = [c[0] for c in LANGUAGES_FIX_ID]

        for lc in languagecodes:
            if not self.object.has_language(lc):
                continue

            upload = getattr(self.object, 'upload_%s' % lc)

            context['version_language'].append({
                'languagecode':lc,
                'upload': upload,
                'upload_exists': os.path.exists(upload.path),
                'url': getattr(self.object, 'url_%s' % lc),
                'cover': getattr(self.object, 'cover_%s' % lc),
                'title': getattr(self.object, 'title_%s' % lc),
                'description': getattr(self.object, 'description_%s' % lc)
            })
        return context


class VersionDelete(DeleteView):

    model = Version


class VersionUpdate(UpdateView):

    model = Version
    form_class = VersionUpdateForm


class VersionList(SingleTableView):

    model = Version
    table_class = VersionTable