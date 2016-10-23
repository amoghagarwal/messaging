
from django.contrib import admin

#urlpatterns = [
    # Examples:
    # url(r'^$', 'appsphere.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

#    url(r'^admin/', include(admin.site.urls)),

#]
from django.conf.urls import *

urlpatterns = patterns('',
                        url(r'^$', 'accept_requests.views.landing_service' ,name="landing_page"),
                        url(r'^message_api/$', 'accept_requests.views.msg_service', name="msg_service")
)