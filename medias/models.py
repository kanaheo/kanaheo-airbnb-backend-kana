from django.db import models
from common.models import CommonModel

class Photo(CommonModel):
    
    """ Media Definition"""
    
    file = models.ImageField()
    description = models.CharField(max_length=140)
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    
    def __str__(self):
        return "Photo File"
    
class Viedo(CommonModel):
    
    file = models.FileField()
    # 밑에 ! viedo는 experience에 대해서만 사용함. 그리고 experience는 1개의 viedo만 가질 수 있기 때문에 이렇게 함
    experience = models.OneToOneField("experiences.Experience", on_delete=models.CASCADE)
    
    def __str__(self):
        return "Viedo File"
    
