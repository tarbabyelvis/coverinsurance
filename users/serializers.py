from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission, Group
from .models import User, Profile, SatelliteBranch, Branch
from .utils import normalize_email


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ("user",)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = (
            "id",
            "name",
            "email",
            "town",
            "is_active",
        )


class SatelliteSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()

    class Meta:
        model = SatelliteBranch
        fields = (
            "id",
            "name",
            "branch",
            "email",
            "town",
            "is_active",
        )

    def create(self, validated_data):
        branch = Branch.objects.get(name=validated_data["branch"]["name"])
        email = normalize_email(validated_data["email"])
        satellite = SatelliteBranch(
            name=validated_data["name"],
            branch=branch,
            email=email,
            town=validated_data["town"],
            is_active=validated_data["is_active"]
        )
        satellite.save()
        return satellite

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
    # profile = ProfileCreateSerializer(required=True)
    branch = SatelliteSerializer()
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
            "is_collections_user",
            "is_superuser",
            "is_staff",
            "is_staff",
            "is_active",
            "branch",
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
        branch = SatelliteBranch.objects.get(name=validated_data["branch"]["name"])
        isSupervisor = validated_data["is_supervisor"]
        isTeamLeader = validated_data["is_teamleader"]
        isCollectionsUser = validated_data["is_collections_user"]
        isSuperuser = validated_data["is_superuser"]
        isStaff = validated_data["is_staff"]
        isActive = validated_data["is_active"]
        userType = validated_data["user_type"]
        user = User(email=email, first_name=first_name, last_name=last_name, phone=phone, is_superuser=isSuperuser,
                    is_supervisor=isSupervisor, is_teamleader=isTeamLeader, is_collections_user=isCollectionsUser,
                    is_staff=isStaff, is_active=isActive, user_type=userType, branch=branch)
        user.set_password(password)
        user.save()
        codeNameList = validated_data["permissions"]["permissions"]
        for permission in codeNameList:
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
        groupNameList = validated_data["permissions"]["groups"]
        if groupNameList:
            groups = Group.objects.filter(name__in=groupNameList)
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
