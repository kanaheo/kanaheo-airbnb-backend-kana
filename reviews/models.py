from django.db import models
from common.models import CommonModel

class Review(CommonModel):
    
    """Review from a User to a Room or Experience"""
    
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    room = models.ForeignKey(
        "rooms.Room",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    payload = models.TextField()    # 리뷰 내용
    rating = models.PositiveIntegerField()
    
    # room, experience를 2개 쓴건 !! 보통 1개에 대해서만 리뷰를 쓰기 때문
    
    def __str__(self) -> str:
        return f"{self.user} / {self.rating}⭐️"
