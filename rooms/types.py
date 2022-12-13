from django.conf import settings
import strawberry
from strawberry.types import Info
import typing
from strawberry import auto
from . import models
from wishlists.models import Wishlist
from users.types import UserType
from reviews.types import ReviewType

@strawberry.django.type(models.Room)
class RoomType:
    id: auto
    name: auto
    kind: auto
    owner: "UserType"
    @strawberry.field
    def reviews(self, page:typing.Optional[int] = 1) -> typing.List["ReviewType"]:
        start = (page -1) * settings.PAGE_FIVE_SIZE
        end = start + settings.PAGE_FIVE_SIZE
        return self.reviews.all()[start:end]
    
    @strawberry.field
    def rating(self) -> str:
        return self.rating()
    
    @strawberry.field
    def is_owner(self, info: Info) -> bool:
        return self.owner == info.context.request.user
    
    @strawberry.field
    def is_liked(self, info: Info) -> bool:
        return Wishlist.objects.filter(
            user=info.context.request.user,
            rooms__id=self.pk
        ).exists()