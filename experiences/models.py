from django.db import models
from common.models import CommonModel


class Experience(CommonModel):
    
    """Experience Model Definition"""
    
    country = models.CharField(max_length=50, default="korea")
    city = models.CharField(max_length=80, default="seoul")
    name = models.CharField(max_length=250)
    host = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="experiences"
    )
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=250)
    start = models.TimeField()
    end = models.TimeField()
    description = models.TextField()
    perks = models.ManyToManyField(
        "experiences.Perk",
        related_name="experiences"
    )
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="experiences"
    )
    
    def rating(experience):
        count = experience.reviews.count()    # reviews모델에서 related_name을 reviews로 했기 때문에 이렇게 불러 올 수 있다.
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in experience.reviews.all().values("rating"):    # 우리는 reviews에서 점수만 가지고 오면 되니까 이렇게 가지고 오는게 효과적임 ! 
                total_rating += review['rating']
            return round(total_rating / count, 2)
    
    def __str__(self) -> str:
        return self.name
    
    
class Perk(CommonModel):
    
    """What is included on an Experience"""
    
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=250, blank=True, default="")
    explanation = models.TextField(blank=True, default="")
    
    def __str__(self) -> str:
        return self.name
