from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.Serializer):
    
    pk = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True,
        max_length=50
    )
    kind = serializers.ChoiceField(
        choices=Category.CategoryKindChoices.choices,
    )
    created_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        return Category.objects.create(
            **validated_data
        )
        
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.kind = validated_data.get("kind", instance.kind)
        instance.save()
        return instance

# **validated_data 요건 밑에처럼 해줌!
# {
# "name": "Category from DRF",
# "kind": "rooms"
# }
# ->
# name="Category from DRF", kind="rooms"