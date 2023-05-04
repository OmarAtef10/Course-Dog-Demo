from rest_framework import serializers
from django.contrib.auth.models import User, Group
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from user_profile.models import Profile
from organization.models import Organization, OrganizationSubdomain


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


def get_domain(email):
    return email.split('@')[-1]


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('username', 'email', 'password',)

    def create(self, validated_data):
        email = validated_data['email']
        username = validated_data['username']
        user_domain = get_domain(email)
        # check username
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': ['Username already exists']})
        # check email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': ['Email already exists']})

        user = User.objects.create_user(**validated_data, is_active=False)
        student_group = Group.objects.get(name='Student')
        user.groups.add(student_group)
        # user_profile = Profile(user=user) ##TODO FIX
        # try:
        #     organization = OrganizationSubdomain.objects.get(
        #         subdomain=user_domain).organization
        #     user_profile.organization = organization
        # except OrganizationSubdomain.DoesNotExist:
        #     pass
        # user_profile.save()

        return user
