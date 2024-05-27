from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email

        # Add more custom claims here if needed

        return data
