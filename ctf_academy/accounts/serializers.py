# accounts/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # This method is called to generate the token
        token = super().get_token(user)

        # Add custom claims to the token's payload
        token['username'] = user.username
        token['role'] = 'admin' if user.is_superuser else 'user'
        
        return token