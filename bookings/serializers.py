from django.utils import timezone
from rest_framework import serializers
from .models import Booking

# only create room booking create api serializer
class CreateRoomBookingSerializer(serializers.ModelSerializer):
    
    check_in = serializers.DateField()  # defulut required value
    check_out = serializers.DateField() # defulut required value
    
    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )
    
    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value
        
    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value
        
    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError("Check in should be smaller than check out!")
        
        if Booking.objects.filter(
            check_in__lte=data["check_out"],
            check_out__gte=data["check_in"]
        ).exists():
            raise serializers.ValidationError("Those or some of those dates are already bookings!")
        
        return data


# 이건 모두가 보는 것
class PublicBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )