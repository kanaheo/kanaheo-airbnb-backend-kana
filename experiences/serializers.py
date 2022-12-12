from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from medias.serializers import PhotoSerializer

from users import serializers as UserSerializers

from .models import Perk, Experience

class PerkSerializer(ModelSerializer):
    
    class Meta:
        model = Perk
        fields = "__all__"

class ExperienceListSerializer(ModelSerializer):
    
    is_owner = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    # perks = PerkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Experience
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "address",
            # "start",
            # "end",
            "description",
            "is_owner",
            "rating",
            "photos",
            # "perks"
        )
    
    def get_is_owner(self, experience):
        request = self.context["request"]
        return request.user == experience.host
    
    def get_rating(self, experience):
        return experience.rating()

class ExperienceDetailSerializer(serializers.ModelSerializer):
    
    host = UserSerializers.TinyUserSerializer(read_only=True)
    perks = PerkSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Experience
        fields = "__all__"
    
    def get_rating(self, experience):
        return experience.rating()