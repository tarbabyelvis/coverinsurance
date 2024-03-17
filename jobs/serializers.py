from rest_framework import serializers


class JobsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data.get("end_date") < data.get("start_date"):
            raise serializers.ValidationError(
                "End Date cannot be less than Start Date."
            )
        return data
