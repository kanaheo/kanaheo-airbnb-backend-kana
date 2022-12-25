from django.db import models
from common.models import CommonModel

class Room(CommonModel):
    
    ### Room Model Definition ###
    
    class RoomKindChoices(models.TextChoices):
        ENTIRE_PLACE = ("entire_place", "Entire Place")
        PRIVATE_ROOM = ("private_room", "Private Room")
        SHARED_ROOM = ("shared_room", "Shared Room")
    
    name = models.CharField(max_length=180, default="")
    country = models.CharField(max_length=50, default="korea")
    city = models.CharField(max_length=80, default="seoul")
    price = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    toilets = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(max_length=250)
    pet_friendly = models.BooleanField(default=True)
    kind = models.CharField(max_length=20, choices=RoomKindChoices.choices)
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    amenities = models.ManyToManyField(
        "rooms.Amenity",
        related_name="rooms"
        
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rooms"
    )
    
    def __str__(self) -> str:
        return self.name
    
    def total_amenities(self):
        return self. amenities.count()
    
    def rating(room):
        count = room.reviews.count()    # reviews모델에서 related_name을 reviews로 했기 때문에 이렇게 불러 올 수 있다 .
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in room.reviews.all().values("rating"):    # 우리는 reviews에서 점수만 가지고 오면 되니까 이렇게 가지고 오는게 효과적임 ! 
                total_rating += review['rating']
            return round(total_rating / count, 2)


class Amenity(CommonModel):
    
    """ Amenity Definition """
    
    name = models.CharField(max_length=150)
    description = models.CharField(
        max_length=150, 
        null=True, # 이건 DB가 null가능한거
        blank=True # 이건 장고 어드민 패널에서 빈값이 가능하게
    )
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name_plural = "Amenities"