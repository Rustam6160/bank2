from rest_framework import serializers
from .models import *


class ShowAllUsersSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = ('wallet', 'username')
