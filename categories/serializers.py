from rest_framework import serializers

class CategorySerializer(serializers.Serializer):
    
    name = serializers.CharField(required=True)
    kind = serializers.CharField()