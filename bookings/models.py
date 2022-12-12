from django.utils import timezone
from django.db import models
from common.models import CommonModel
from django.core.exceptions import ValidationError

class Booking(CommonModel):
    
    """ Booking Model Definition """
    
    class BookingKindChoices(models.TextChoices):   # rooms or experience인지 체크 하기 위해서
        ROOM = ("room", "ROOM")
        EXPERIENCE = ("experience", "Experience")
        
    kind = models.CharField(max_length=15, choices=BookingKindChoices.choices)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    room = models.ForeignKey(
        "rooms.Room",
        null=True,  # 이건 DB에서
        blank=True, # 이건 admin 패널에서 
        on_delete=models.SET_NULL,
        related_name="bookings"
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bookings"
    )
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    experience_time_start = models.DateTimeField(null=True, blank=True)
    experience_time_end = models.DateTimeField(null=True, blank=True)
    guests = models.PositiveIntegerField()
    
    def clean(self):
        if self.kind == "room":
            if self.check_out < self.check_in:
                raise ValidationError("Check in should be smaller than check out!")
            
        elif self.kind == "experience":
            if not self.experience_time_end or not self.experience_time_start:
                raise ValidationError("Experience time start or Experience time end empty!")
            
            if timezone.localtime(self.experience_time_start) > timezone.localtime(self.experience_time_end):
                raise ValidationError("experience_time_start should be smaller than experience_time_end!")
    
    def __str__(self):
        return f"{self.kind.title()} booking for :  {self.user}"
    
    

