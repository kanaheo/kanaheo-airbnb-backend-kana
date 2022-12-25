from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
from rooms.models import Room
from .serializers import WishlistSerializer

class Wishlists(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        all_wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(
            all_wishlists,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            # 위에서 생성한 것에 대해서 user도 저장하고 싶어서 밑에처럼 한다.
            wishlist = serializer.save(
                user=request.user,
            )
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)
        else:
            Response(serializer.errors)

class WishlistDetail(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(
            wishlist,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def delete(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        wishlist.delete()
        return Response(status=HTTP_200_OK)
    
    def put(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(
            wishlist,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        
        if serializer.is_valid():
            wishlist = serializer.save()
            serializer = WishlistSerializer(
                wishlist,
                context={"request": request}
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
class WishlistRoomToogle(APIView):
    
    def get_wishlist(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound
    
    def get_room(self, pk): # pk는 put이나 delete에서 room_pk를 뜻함
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    def put(self, request, pk, room_pk):
        wishlist = self.get_wishlist(pk, request.user)
        room = self.get_room(room_pk)
        
        if wishlist.rooms.filter(pk=room.pk).exists():  # wishlist에서 기존에 있는 room 지우기
            wishlist.rooms.remove(room)
        else: # wishlist에 room추가하기
            wishlist.rooms.add(room)
        return Response(status=HTTP_200_OK)