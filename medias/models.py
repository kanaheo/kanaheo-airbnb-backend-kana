from django.db import models
from common.models import CommonModel

class Photo(CommonModel):
    
    """ Media Definition"""
    
    file = models.URLField()
    description = models.CharField(max_length=140)
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="photos"
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="photos"
    )
    
    def __str__(self):
        return "Photo File"
    
class Viedo(CommonModel):
    
    file = models.URLField()
    # 밑에 ! viedo는 experience에 대해서만 사용함. 그리고 experience는 1개의 viedo만 가질 수 있기 때문에 이렇게 함
    experience = models.OneToOneField(
        "experiences.Experience",
        on_delete=models.CASCADE,
        related_name="viedos"
    )
    
    def __str__(self):
        return "Viedo File"
    
