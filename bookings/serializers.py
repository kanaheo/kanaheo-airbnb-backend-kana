from django.utils import timezone
from rest_framework import serializers
from .models import Booking

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
        room = self.context.get("room")
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError("Check in should be smaller than check out!")
        
        if Booking.objects.filter(  # 특정한 방에 예약이 있는지를 체크해야함 ! 
            room=room,
            check_in__lte=data["check_out"],
            check_out__gte=data["check_in"]
        ).exists():
            raise serializers.ValidationError("Those or some of those dates are already bookings!")
        
        return data

class CreateExperienceBookingSerializer(serializers.ModelSerializer):
    
    experience_time_start = serializers.DateTimeField()
    experience_time_end = serializers.DateTimeField()
    
    class Meta:
        model = Booking
        fields = (
            "experience_time_start",
            "experience_time_end",
            "guests",
        )

    def validate_experience_time_start(self, value):
        now = timezone.localtime(timezone.now())
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value
        
    def validate_experience_time_end(self, value):
        now = timezone.localtime(timezone.now())
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value

    def validate(self, data):
        if data["experience_time_start"] <= data["experience_time_end"]:
            raise serializers.ValidationError("Check in should be smaller than experience time end!")
    
        if Booking.objects.filter(
            experience_time_start__lte=data["experience_time_end"],
            experience_time_end__gte=data["experience_time_start"]
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
            "experience_time_start",
            "experience_time_end",
            "guests",
        )
        
# 이건 모두가 보는 것
class PublicBookingExperienceSerializer(serializers.ModelSerializer):
    
    experience_time_start = serializers.DateTimeField()
    experience_time_end = serializers.DateTimeField()
    
    class Meta:
        model = Booking
        fields = (
            "pk",
            "experience_time_start",
            "experience_time_end",
            "guests",
        )
    
    def validate_experience_time_start(self, value):
        now = timezone.localtime(timezone.now())
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value
        
    def validate_experience_time_end(self, value):
        now = timezone.localtime(timezone.now())
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        else:
            return value

    def validate(self, data):
        if data["experience_time_start"] <= data["experience_time_end"]:
            raise serializers.ValidationError("Check in should be smaller than experience time end!")
    
        if Booking.objects.filter(
            experience_time_start__lte=data["experience_time_end"],
            experience_time_end__gte=data["experience_time_start"]
        ).exists():
            raise serializers.ValidationError("Those or some of those dates are already bookings!")
        
        return data