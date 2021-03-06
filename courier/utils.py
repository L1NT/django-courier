import logging, datetime

from django.db.models import signals
from django.db.models import get_model 
from django.core.mail import EmailMessage
from django.template import Context, Template
from courier.conf import settings
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from courier.models import EmailRecipient

log = logging.getLogger('courier')

def attach_signal(signal_name, content_type_pk):
    """
    Attach a given signal to a content type
    """
    ct    = ContentType.objects.get(pk=content_type_pk)
    model = ct.model_class()
    if model:
        app = ct.app_label
        uid = '%s.%s.%s' % (app, signal_name, content_type_pk)

        if signal_name == 'post_create':
            dispatcher = created_dispatcher
            signal = getattr(signals, 'post_save')
        else:
            signal = getattr(signals, signal_name)
            if signal_name == 'post_delete':
                dispatcher = deleted_dispatcher
            else:
                dispatcher = modified_dispatcher

        signal.connect(dispatcher, sender=model, dispatch_uid=uid)
        log.debug("Courier: Attached %s on %s.%s (uid %s)" % (signal_name, app, model.__name__, uid) )


def attach_signals(signal_list):
    """
    Attach a list of signals to content types
    """
    for s in signal_list:
        attach_signal(s['signal'], s['content_type'])


def detach_signal(signal_name, content_type_pk):
    """
    Attach a given signal to a content type
    """
    ct    = ContentType.objects.get(pk=content_type_pk)
    model = ct.model_class()
    if model:
        app = ct.app_label
        uid = '%s.%s.%s' % (app, signal_name, content_type_pk)

        if signal_name == 'post_create':
            dispatcher = created_dispatcher
            signal = getattr(signals, 'post_save')
        else:
            signal = getattr(signals, signal_name)
            if signal_name == 'post_delete':
                dispatcher = deleted_dispatcher
            else:
                dispatcher = modified_dispatcher

        signal.disconnect(dispatcher, sender=model, dispatch_uid=uid)
        log.debug("Courier: Detached %s.%s on %s (uid %s)" % (signal_name, app, model.__name__, uid) )


# Signal dispatchers

def get_dispatcher_context(kwargs, signal):
    ct = ContentType.objects.get_for_model(kwargs['instance'])
    return (kwargs['instance'], ct,
            # avoid circular reference
            get_model('courier', 'EmailNotification').objects.\
                    filter(content_type__pk=ct.pk, signal=signal, is_active=True))


def created_dispatcher(sender, **kwargs):
    if kwargs['created'] == True:
        instance, ct, notifications = get_dispatcher_context(kwargs, 'post_create')
        for notification in notifications:
            send_notification(notification, instance, 'created')


def modified_dispatcher(sender, **kwargs):
    instance, ct, notifications = get_dispatcher_context(kwargs, 'post_save')
    if kwargs['created'] == False:
        for notification in notifications:
            send_notification(notification, instance, 'modified')


def deleted_dispatcher(sender, **kwargs):
    instance, ct, notifications = get_dispatcher_context(kwargs, 'post_delete')
    for notification in notifications:
        send_notification(notification, instance, 'deleted')


def send_notification(notification, instance, created=False):
    """
    This is the actual method that sends the notifications
    """

    site       = Site.objects.get(id=settings.SITE_ID)
    template   = notification.template
    recipients = EmailRecipient.objects.filter(notification_id=notification)
    subject    = Template(template.subject).render(Context({
        '%s' % notification.object_name: instance,
        'site': site,
    }))
    
    start_time = datetime.datetime.today()
    log.debug(u"Courier: trying to send \"%s\" notification from %s" % (subject, notification.from_email))

    for recipient in recipients:
        body = Template(template.body).render(Context({
           '%s' % notification.object_name: instance,
           'site': site,
           'recipient': recipient,
        }))
        message = EmailMessage(subject, body, notification.from_email, [recipient.email])
        message.content_subtype = "html"
        message.send()

    end_time = datetime.datetime.today()
    log.debug(u"Courier: \"%s\" notification sent from %s (%ss)" % (subject, notification.from_email, end_time - start_time))
