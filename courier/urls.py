from django.conf.urls import url
from django.conf.urls import patterns

from courier.views import AddRecipient, OptOut


urlpatterns = patterns(
    '',
    url(r'^email-signup/', AddRecipient.as_view(), name='courier_add_recipient'),
    url(r'^opt-out/', OptOut.as_view(), name='courier_opt_out'),
)
