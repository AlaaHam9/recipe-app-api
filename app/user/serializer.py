from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}


    # override the default method (we need to save the password after hashed it), it called after the above validation
    # create and return user with hashed pass stored
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    # also override update to the same reason to store passord hashed
    def update(self, instance, validate_data):
        password = validate_data.pop('password', None)
        user = super().update(instance, validate_data)

        if password:
            user.set_password(password)
            user.save()

        return user


# To customize the default (username and password to email and password), this serialiazer is the default that used by ObtainAuthToken view
class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user auth token """
    email    = serializers.EmailField()
    password = serializers.CharField(style={'input_type':'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = {'Unable to authenticate with provided credentials.'}
            return serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs