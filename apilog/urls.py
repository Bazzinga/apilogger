from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^partnerprovisioning/v1/', include('api.urls')),)
