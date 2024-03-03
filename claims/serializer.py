
from rest_framework import serializers
from claims.models import Claim


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        exclude = ['deleted']
   
    def validate(self, data):
        errors = {}

        # Iterate over each field in the serializer
        for field_name, value in data.items():
            print("iteration")
            # Get the corresponding model field
            model_field = self.fields[field_name]

            # Validate the data type
            try:
                data[field_name] = model_field.to_internal_value(value)
            except serializers.ValidationError as e:
                errors[field_name] = e.detail

        if errors:
            print('Error validation')
            raise serializers.ValidationError(errors)
        print("Done validation")
        return data


    def create(self, validated_data):
        # Create the Claim instance
        instance = Claim.objects.create(**validated_data)
        return instance
