from django.http import HttpResponse
from django.views.generic.edit import View

from courier.models import EmailRecipient, EmailNotification


class AddRecipient(View):
    """
    Adds a new recipient to the database
    Requires the following GET parameters:
        email: the email to be added
        notification: the EmailNotification.title
    """
    
    model = EmailRecipient
    
    def add_recipient(self):
        if self.request.GET:
            return HttpResponse("test response")
            
    def dispatch(self, request, *args, **kwargs):
        if request.GET:
            recipient = EmailRecipient()
            recipient.email = request.GET.get('email', '')
            title = request.GET.get('notification', '')
            notification = EmailNotification.objects.get(title=title)
            recipient.notification = notification
            if not EmailRecipient.objects.filter(email=recipient.email, notification=recipient.notification):
                recipient.save()
                return HttpResponse(recipient.email)
