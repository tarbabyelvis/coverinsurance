from rest_framework import serializers

from audit.models import AuditTrail
from users.models import User


class AuditTrailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = AuditTrail
        fields = "__all__"
