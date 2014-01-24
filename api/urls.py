from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from views import Logger, Collection

urlpatterns = patterns('api.views',
                       url(r'^log/?$', Logger.as_view(), name='logger-api'),
                       url(r'^collection/?$', Collection.as_view(), name='collection-api'),)

urlpatterns = format_suffix_patterns(urlpatterns)
