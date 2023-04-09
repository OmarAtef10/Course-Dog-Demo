from rest_framework.response import Response
import requests

from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes

from rest_framework.generics import GenericAPIView

from django.conf import settings
from smtplib import SMTPException
from django.core.mail import send_mail, send_mass_mail

from .serializers import EmailSerializer, MassEmailSerializer, UidTokenSerializer
from .permissions import IsSupportAdmin
# Create your views here.


def get_base_url():
    domain = settings.DOMAIN
    return f"http://{domain}/"


def get_domain(email):
    return email.split('@')[-1]


def send_email(subject, body, to_email):
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False
        )
        return True
    except SMTPException:
        return False


def send_mass_email(subject, body, to_email_list):
    message_list = []
    for email in to_email_list:
        message_list.append((
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email]
        ))

    messages = tuple(message_list)
    try:
        count = send_mass_mail(messages, fail_silently=False)
        return count
    except SMTPException:
        return False


"""
API endpoint for sending email to a user
"""


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSupportAdmin])
def send_email_api(request):
    sent_mail_status = False
    email_deserializer = EmailSerializer(data=request.data)

    if email_deserializer.is_valid():
        subject = email_deserializer.validated_data['subject']
        to_email = email_deserializer.validated_data['user_email']
        mail_body = email_deserializer.validated_data['mail_body']
        sent_mail_status = send_email(
            subject, mail_body, to_email)

    if sent_mail_status:
        return Response({'code': '1'}, 200)
    return Response({'code': '0'}, 500)


"""
API endpoint for sending an email to multiple users
"""


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSupportAdmin])
def send_mass_email_api(request):
    sent_mail_status = False
    emails_deserializer = MassEmailSerializer(data=request.data)

    if emails_deserializer.is_valid():
        subject = emails_deserializer.validated_data['subject']
        to_email_list = emails_deserializer.validated_data['user_emails']
        mail_body = emails_deserializer.validated_data['mail_body']
        sent_mail_status = send_mass_email(
            subject, mail_body, to_email_list)

    if sent_mail_status:
        return Response({'code': '1'}, 200)
    return Response({'code': '0'}, 500)


class ActivateUser(GenericAPIView):
    """
    User Mail Activation Link
    """

    def get(self, request, uid, token, format=None):
        payload = {'uid': uid, 'token': token}

        url = get_base_url()+"auth/auth/users/activation/"
        response = requests.post(url, data=payload)

        if response.status_code == 204:
            return Response({}, response.status_code)
        else:
            return Response(response.json())


class ResetUserPassword(GenericAPIView):
    serializer_class = UidTokenSerializer

    def get(self, request, uid, token, format=None):
        return Response({'uid': uid, 'token': token}, 200)

    def post(self, request, uid, token, format=None):
        password = request.POST.get('new_password')
        payload = {'uid': uid, 'token': token, 'new_password': password}

        url = get_base_url()+"auth/auth/users/reset_password_confirm/"
        response = requests.post(url, data=payload)
        if response.status_code == 204:
            return Response({}, response.status_code)
        else:
            return Response(response.json())
