from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Profile
from .utils import normalize_email


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ("user",)

    def create(self, validated_data):
        normalized_email = normalize_email(validated_data["email"])
        validated_data["email"] = normalized_email
        profile = Profile.objects.create(**validated_data)
        return profile

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.email = validated_data.get("email", instance.email)
        instance.town = validated_data.get("town", instance.town)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "name", "codename"


class PermissionRequest(object):
    def __init__(self, permissions, groups):
        self.permissions = permissions
        self.groups = groups

    def to_dict(self):
        return {
            "permissions": self.permissions,
            "groups": self.groups,
        }


class PermissionRequestSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.CharField())
    groups = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = PermissionRequest
        fields = ("permissions", "groups")


class UserSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SerializerMethodField()
    permissions = PermissionRequestSerializer(write_only=True)
    user_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "user_type",
            "last_name",
            "phone",
            "is_supervisor",
            "is_teamleader",
            "is_superuser",
            "is_staff",
            "is_active",
            "permissions",
            "user_permissions",
            "user_groups",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        email = normalize_email(validated_data["email"])
        password = validated_data["password"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        phone = validated_data["phone"]
        is_supervisor = validated_data["is_supervisor"]
        is_team_leader = validated_data["is_teamleader"]
        is_superuser = validated_data["is_superuser"]
        is_staff = validated_data["is_staff"]
        is_active = validated_data["is_active"]
        user_type = validated_data["user_type"]
        user = User(email=email, first_name=first_name, last_name=last_name, phone=phone, is_superuser=is_superuser,
                    is_supervisor=is_supervisor, is_teamleader=is_team_leader,
                    is_staff=is_staff, is_active=is_active, user_type=user_type)
        user.set_password(password)
        user.save()
        code_names = validated_data["permissions"]["permissions"]
        for permission in code_names:
            try:
                perm, _ = Permission.objects.get_or_create(
                    codename=permission,
                    defaults={
                        "content_type": ContentType.objects.get(model="custom"),
                        "name": convert_to_name(permission),
                    })
                user.user_permissions.add(perm)
            except Exception:
                pass
        group_names = validated_data["permissions"]["groups"]
        if group_names:
            groups = Group.objects.filter(name__in=group_names)
            user.groups.set(groups)
        Token.objects.create(user=user)
        # profile = validated_data["profile"]
        # Profile.objects.create(user=user, **profile)
        return user

    def get_user_permissions(self, obj):
        group_permissions = [
            str(perm.codename) for perm in Permission.objects.filter(group__user=obj)
        ]
        user_permissions = [str(perm.codename) for perm in obj.user_permissions.all()]

        return user_permissions + group_permissions

    def get_user_groups(self, obj):
        return [str(grp.name) for grp in obj.groups.all()]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "permissions",
        )


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = "__all__"


def convert_to_name(code_name):
    parts = code_name.split('_')
    capitalized_parts = [part.capitalize() for part in parts]
    return 'Can ' + ' '.join(capitalized_parts)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['user_id'] = user.pk
        token['email'] = user.email
        token['name'] = f'{user.first_name} {user.last_name}'
        token['user_type'] = user.user_type
        token['is_supervisor'] = user.is_supervisor
        token['is_teamleader'] = user.is_teamleader
        token['phone'] = user.phone
        token['permissions'] = [perm.codename for perm in user.user_permissions.all()]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add additional information to the response data
        data['user_id'] = self.user.pk
        data['name'] = f'{self.user.first_name} {self.user.last_name}'
        data['email'] = self.user.email
        data['user_type'] = self.user.user_type
        data['is_supervisor'] = self.user.is_supervisor
        data['is_teamleader'] = self.user.is_teamleader
        data['phone'] = self.user.phone
        data['permissions'] = [perm.codename for perm in self.user.user_permissions.all()]
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
