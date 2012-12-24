from django.conf.urls import url
from django.conf.urls import patterns

from courier.views import AddRecipient

urlpatterns = patterns(
    '',
    url(r'^', AddRecipient.as_view(), name='courier_add_recipient'),
    )
