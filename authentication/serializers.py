from rest_framework import serializers
from django.contrib.auth.models import User


class EmailSerializer(serializers.Serializer):
    user_email = serializers.EmailField()
    subject = serializers.CharField(max_length=128)
    mail_body = serializers.CharField(max_length=10000)


class MassEmailSerializer(serializers.Serializer):
    user_emails = serializers.ListField()
    subject = serializers.CharField(max_length=128)
    mail_body = serializers.CharField(max_length=10000)


class UidTokenSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=500)
    token = serializers.CharField(max_length=500)
    new_password = serializers.CharField(max_length=100)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
