from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#from webapp.views import case_list, case_detail, case_result, case_delete,\
#    case_scheme, questionary_start
from webtestingtool.settings import MEDIA_ROOT
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webtestingtool.views.home', name='home'),
    # url(r'^webtestingtool/', include('webtestingtool.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', direct_to_template, {'template':'index.html'}, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cases', 'webapp.views.case_list', name = 'case_list'),
    url(r'^case/(?P<case_id>\d+)', 'webapp.views.case_detail', name = 'case_detail'),
    url(r'^casepending/(?P<case_id>\d+)', 'webapp.views.case_scheme', name = 'case_scheme'),
    url(r'^case/delete/(?P<case_id>\d+)', 'webapp.views.case_delete', name = 'case_delete'),
    url(r'^result/(?P<case_id>\d+)', 'webapp.views.case_result', name = 'case_result'),
    
    url(r'^questionary_start', 'webapp.views.questionary_start', name = 'questionary_start'),
    url(r'^questionary', 'webapp.views.questionary', name = 'questionary'),
    
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': MEDIA_ROOT,
        }),

)
