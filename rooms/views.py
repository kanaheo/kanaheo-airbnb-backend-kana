from rest_framework.views import APIView
from django.db import transaction
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from .models import Amenity, Room
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from django.conf import settings
from medias.serializers import PhotoSerializer

class Amenities(APIView):
    
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)
        else:
            return Response(serializer.errors)

class AmenityDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise  NotFound
    
    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)
    
    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True    # 부분적인 수정 오키 ! 즉 name, description을 둘중 한개도, 두개도 수정가능하게 ! 
        )
        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(
                AmenitySerializer(updated_amenity).data
            )
        else:
            return Response(serializer.errors)
    
    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class Rooms(APIView):
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms, 
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        if request.user.is_authenticated:   # 현재 로그인을 했는지 체크(이걸 하는거 자체가 로그인 한 사람을 위해서 하는거니까)
            serializer = RoomDetailSerializer(data=request.data) # room을 생성 할 때는 serializers의 fields가 all인것을 원하니까 !
            if serializer.is_valid():
                category_pk = request.data.get("category")
                if not category_pk:
                    raise ParseError("Category is Requird")
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:   # 이건 ! rooms을 만드는 api! 즉 experiences를 만들지 말자 ! 
                        raise ParseError("The category kind should be 'rooms'")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
                try:
                    with transaction.atomic():
                        room = serializer.save(
                            owner=request.user, 
                            category=category
                        )
                        amenities = request.data.get("amenities")
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)                    
                        serializer = RoomDetailSerializer(room)
                        return Response(serializer.data)
                except Exception:
                    raise ParseError("Amenity not found")
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated

class RoomDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(
            room,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def put(self, request, pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if room.owner != request.user:
            raise PermissionDenied
        
        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    category_pk = request.data.get("category")
                    if not category_pk:
                        raise ParseError("Category is Requird")
                    try:
                        category = Category.objects.get(pk=category_pk)
                        if category.kind == Category.CategoryKindChoices.EXPERIENCES:   # 이건 ! rooms을 만드는 api! 즉 experiences를 만들지 말자 ! 
                            raise ParseError("The category kind should be 'rooms'")
                    except Category.DoesNotExist:
                        raise ParseError("Category not found")
                    room = serializer.save(category=category)
                    
                    amenities = request.data.get("amenities")
                    if amenities:       # 유저가 보낸 amenities가 있으면 밑에 처리
                        room.amenities.clear()
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)            
                        serializer = RoomDetailSerializer(room)
                        return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
            
            updated_room = serializer.save()
            return Response(
                RoomDetailSerializer(updated_room).data
            )
        else:
            return Response(serializer.errors)
        
    
    def delete(self, request, pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class RoomReviews(APIView):
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
        
    def get(self, request, pk):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1
        
        start = (page -1) * settings.PAGE_FIVE_SIZE
        end = start + settings.PAGE_FIVE_SIZE
        
        room = self.get_object(pk)
        serializer = ReviewSerializer(
            room.reviews.all()[start:end],
            many=True
        )
        return Response(serializer.data)
    
class RoomAmenities(APIView):
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1
        
        start = (page-1) * settings.PAGE_FIVE_SIZE
        end = start + settings.PAGE_FIVE_SIZE
        
        room = self.get_object(pk)
        serializer = AmenitySerializer(
            room.amenities.all()[start:end],
            many=True
        )
        
        return Response(serializer.data)

class RoomPhotos(APIView):
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    # 해당 room에 대한 사진을 만들기 ~ 
    def post(self, request, pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer=PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)