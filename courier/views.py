from django.http import HttpResponse, HttpResponseForbidden
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
            if recipient.email != '':
                title = request.GET.get('notification', '')
                notification = EmailNotification.objects.get(title=title)
                recipient.notification = notification
                if not EmailRecipient.objects.filter(email=recipient.email, notification=recipient.notification):
                    recipient.save()
                    return HttpResponse(recipient.email)
                else:
                    return HttpResponseForbidden('Notification recipient already exists.')
            else:
                return HttpResponseForbidden('Email not set.')

class OptOut(View):
    """
    Removes an email from the database.
    Accepts the following GET parameters:
        email: the email to be removed
        notification: the EmailNotification.title, or all if not provided
    """
    
    model = EmailRecipient

    def dispatch(self, request, *args, **kwargs):
        if request.GET:
           delemail = request.GET.get('email')
           title = request.GET.get('notification', '')
           if title != '':
              notification = EmailNotification.objects.get(title=title)
              EmailRecipient.objects.filter(email=delemail, notification=notification).delete()
              return HttpResponse(delemail + ' has been removed from the list of ' + title + ' notifications.')
           else:
              EmailRecipient.objects.filter(email=delemail).delete()
              return HttpResponse(delemail + ' will no longer receive emails from Still a Dancing Queen.')
           return HttpResponse('That email wasn\'t found in our list of recipients.')
