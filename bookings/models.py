from django.db import models
from common.models import CommonModel

class Booking(CommonModel):
    
    """ Booking Model Definition """
    
    class BookingKindChoices(models.TextChoices):   # rooms or experience인지 체크 하기 위해서
        ROOM = ("room", "ROOM")
        EXPERIENCE = ("experience", "Experience")
        
    kind = models.CharField(max_length=15, choices=BookingKindChoices.choices)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room",
        null=True,  # 이건 DB에서
        blank=True, # 이건 admin 패널에서 
        on_delete=models.SET_NULL
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    experience_time = models.DateTimeField(null=True, blank=True)
    guests = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.kind.title()} booking for :  {self.user}"
    
    

