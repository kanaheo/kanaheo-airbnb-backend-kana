from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from .models import Amenity, Room
from categories.models import Category
from . import serializers
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer

class Amenities(APIView):
    
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = serializers.AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(serializers.AmenitySerializer(amenity).data)
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

class AmenityDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise  NotFound
    
    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = serializers.AmenitySerializer(amenity)
        return Response(serializer.data)
    
    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = serializers.AmenitySerializer(
            amenity,
            data=request.data,
            partial=True    # 부분적인 수정 오키 ! 즉 name, description을 둘중 한개도, 두개도 수정가능하게 ! 
        )
        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(
                serializers.AmenitySerializer(updated_amenity).data
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )
    
    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class Rooms(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = serializers.RoomListSerializer(
            all_rooms, 
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.RoomDetailSerializer(data=request.data)     # room을 생성 할 때는 serializers의 fields가 all인것을 원하니까 !
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:      # 이건 ! rooms을 만드는 api! 즉 experiences를 만들지 말자 ! 
                    raise ParseError("The category kind should be 'rooms'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            try:
                with transaction.atomic():
                    room = serializer.save(
                        owner=request.user,
                        category=category,
                    )
                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                        room.amenities.add(amenity)
                    serializer = serializers.RoomDetailSerializer(
                        room,
                        context={"request": request},
                    )
                    return Response(serializer.data)
            except Exception as e:
                raise ParseError("Amenity not found")
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )
    
class RoomDetail(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = serializers.RoomDetailSerializer(
            room,
            context={"request": request}
        )
        return Response(serializer.data)
    
    def put(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        
        serializer = serializers.RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        
        
        if serializer.is_valid():
            # TODO 만약 category가 필수가 아니라면 여기 수정해야함 
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
            
            try:
                with transaction.atomic():
                    amenities = request.data.get("amenities")
                    if amenities:       # 유저가 보낸 amenities가 있으면 밑에 처리
                        room.amenities.clear()
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)            
                    serializer = serializers.RoomDetailSerializer(
                        room,
                        context={"request": request}
                    )
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)
        
    
    def delete(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class RoomReviews(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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
    
    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                room=self.get_object(pk)
            )
            serializer = ReviewSerializer(review)
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
        serializer = serializers.AmenitySerializer(
            room.amenities.all()[start:end],
            many=True
        )
        
        return Response(serializer.data)

class RoomPhotos(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
    
    # 해당 room에 대한 사진을 만들기 ~ 
    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer=PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class RoomBookings(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        now = timezone.localtime(timezone.now()).date()
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,
        )
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        room = self.get_object(pk)
        serializer = CreateRoomBookingSerializer(
            data=request.data,
            context={"room": room}
        )
        if serializer.is_valid():
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
            
        else:
            return Response(serializer.errors)

class RoomBookingCheck(APIView):
    
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except:
            raise NotFound
    
    def get(self, request, pk):
        room = self.get_object(pk)
        check_in = request.query_params.get("check_in") # url?check_in 있으면 뒤에 check_id의 값만 잘 빼온다
        check_out = request.query_params.get("check_out")
        exists = Booking.objects.filter(  # 특정한 방에 예약이 있는지를 체크해야함 ! 
            room=room,
            check_in__lte=check_out,
            check_out__gte=check_in,
        ).exists()
        
        print(exists)

        if exists:
            return Response({"ok": False})
        return Response({"ok": True})

def make_error(request):
    division_by_zero = 1 / 0