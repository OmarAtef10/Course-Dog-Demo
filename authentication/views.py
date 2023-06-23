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
from user_profile.views import get_user_profile
import string
import secrets
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


def generate_new_password(length=28):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


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
    def post(self, request):
        user_email = request.POST.get('email')
        if user_email == None:
            return Response({'message': 'Email is required'}, 400)
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({'message': 'There is no user with this email'}, 404)
        new_password = generate_new_password()
        user.set_password(new_password)
        user.save()
        send_email("Change Password Request",
                   f"Your new password is {new_password}", user_email)
        return Response({'message': 'Email was sent successfully'}, 200)


class RetriveUserInfoAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_groups = user.groups.all()
        user_groups_names = [group.name for group in user_groups]
        user_profile = get_user_profile(user)
        user_organization = user_profile.organization
        if user_organization == None:
            user_organization = ''
        else:
            user_organization = user_organization.name
        user_info = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'groups': user_groups_names,
            'organization': user_organization,
        }
        return Response(user_info,200)
