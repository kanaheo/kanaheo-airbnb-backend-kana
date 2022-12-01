from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist
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
        )
        
        if serializer.is_valid():
            wishlist = serializer.save()
            serializer = WishlistSerializer(
                wishlist,
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)