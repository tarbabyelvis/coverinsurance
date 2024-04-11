from rest_framework import serializers


class JobsSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date is not None and end_date is not None:
            if end_date < start_date:
                raise serializers.ValidationError(
                    "End Date cannot be less than Start Date."
                )

        return data
