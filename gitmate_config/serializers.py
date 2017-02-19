from rest_framework import serializers

from gitmate_config.models import Repository


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class RepositorySerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api:repository-detail')

    class Meta:
        model = Repository
        fields = '__all__'
        read_only_fields = ('user', 'provider', 'full_name')