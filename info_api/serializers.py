from rest_framework import serializers

class InfoSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=256)