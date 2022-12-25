from django.db import models
from common.models import CommonModel

class Category(CommonModel):
    
    """Room or Experience Category"""
    
    class CategoryKindChoices(models.TextChoices):
        ROOMS = "rooms", "Rooms"
        EXPERIENCES = "experiences", "Experiences"

    name = models.CharField(max_length=50)
    kind = models.CharField(
        max_length=15,
        choices=CategoryKindChoices.choices,
    )

    def __str__(self) -> str:
        return f"{self.kind.title()}: {self.name}"  # title은 문자열의 메서드인데 맨앞에 글자를 대문자로 바꿔줌

    class Meta:
        verbose_name_plural = "Categories"
