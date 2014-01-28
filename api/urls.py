from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from views import Logger, LoggerDetail, Collection

urlpatterns = patterns('api.views',
                       url(r'^log/$', Logger.as_view(), name='logger-api'),
                       url(r'^log/(?P<log_id>[0-9]+)/$', LoggerDetail.as_view(), name='logger-api-detail'),
                       url(r'^collection/$', Collection.as_view(), name='collection-api'),)

urlpatterns = format_suffix_patterns(urlpatterns)
