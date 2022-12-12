from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from django.utils import timezone

from config import settings
from reviews.serializers import ReviewSerializer
from categories.models import Category
from .models import Perk, Experience
from . import serializers

from bookings.models import Booking
from bookings.serializers import PublicBookingExperienceSerializer, CreateExperienceBookingSerializer

class Experiences(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        all_experiences = Experience.objects.all()
        serializer = serializers.ExperienceListSerializer(
            all_experiences,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.ExperienceDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is Requird")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("The category kind should be 'experience'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            
            try:
                with transaction.atomic():
                    experience = serializer.save(
                        host=request.user,
                        category=category
                    )
                    perks_ids = request.data.get("perks")
                    
                    for perk_id in perks_ids:
                        perk = Perk.objects.get(pk=perk_id)
                        experience.perks.add(perk)
                        
                    serializer = serializers.ExperienceDetailSerializer(
                        experience,
                        context={"request": request}
                    )
                    return Response(serializer.data)
            except:
                raise ParseError("Perks not found")
        else:
            return Response(serializer.errors)

class ExperienceDetail(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = serializers.ExperienceDetailSerializer(
            experience,
            context={"request": request}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk)
        
        if experience.host != request.user:
            raise PermissionDenied
        
        # 유저에게 받아온 데이터를 파이썬이 읽게 하기 위해서
        serializer = serializers.ExperienceDetailSerializer(
            experience,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk: # 유저가 보낸 카테고리가 있다면
                category = Category.objects.get(pk=category_pk)
                if category.kind == category.CategoryKindChoices.ROOMS:
                    raise ParseError("The category kind should be 'experience'")
            else:   #기존에 있는 category를 넣어줌
                category = experience.category
                # 기존에 있는 category도 없으면 
                if not category:
                    raise ParseError("Experience not found")
            perks_ids = request.data.get("perks")
            if perks_ids:
                try:
                    with transaction.atomic():
                        experience = serializer.save(category=category)
                        if perks_ids:
                            experience.perks.clear()
                        for perk_id in perks_ids:
                            perk = Perk.objects.get(pk=perk_id)
                            experience.perks.add(perk)
                        serializer = serializers.ExperienceDetailSerializer(
                            experience,
                            context={"request": request}
                        )
                        return Response(serializer.data)
                except:
                    raise ParseError("Perks value Error")
            else:
                experience = serializer.save(category=category)
                serializer = serializers.ExperienceDetailSerializer(
                    experience,
                    context={"request": request}
                )
                return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        experience = self.get_object(pk)
        
        if experience.host != request.user:
            raise PermissionDenied
        experience.delete()
        return Response(status=status.HTTP_200_OK)

class ExperienceReviews(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1

        start = (page -1) * settings.PAGE_FIVE_SIZE
        end = start + settings.PAGE_FIVE_SIZE
        
        experience = self.get_object(pk)
        serializer = ReviewSerializer(
            experience.reviews.all()[start:end],
            many=True
        )
        return Response(serializer.data)

class Perks(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = serializers.PerkSerializer(all_perks, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(serializers.PerkSerializer(perk).data)
        else:
            return Response(serializer.errors)
    

class PerkDetail(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(perk)
        return Response(serializer.data)
        
    
    def put(self, request, pk):
        perk = self.get_object(pk)
        serializer = serializers.PerkSerializer(perk, data=request.data, partial=True)
        if serializer.is_valid():
            update_perk = serializer.save()
            return Response(serializers.PerkSerializer(update_perk).data)
        else:
            return Response(serializer.errors)
    
    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExperiencePerks(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1
        
        start = (page-1) * settings.PAGE_FIVE_SIZE
        end = start + settings.PAGE_FIVE_SIZE
        
        experience = self.get_object(pk)
        serializer = serializers.PerkSerializer(
            experience.perks.all()[start:end],
            many=True
        )
        
        return Response(serializer.data)

class ExperienceBookings(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
    
    def get(self, request, pk):
        experience = self.get_object(pk)
        now = timezone.localtime(timezone.now()).date()
        
        bookings = Booking.objects.filter(
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time_start__gt = now,
        )
        
        serializer = PublicBookingExperienceSerializer(bookings, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        experience = self.get_object(pk)
        
        serializer = CreateExperienceBookingSerializer(data=request.data)
        
        if serializer.is_valid():
            booking = serializer.save(
                experience=experience,
                user=request.user,
                kind=Booking.BookingKindChoices.EXPERIENCE
            )
            serializer = PublicBookingExperienceSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class ExperienceDetailBooking(APIView):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_experience(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get_booking(self, bookings_pk):
        try:
            return Booking.objects.get(
                pk=bookings_pk,
                kind=Booking.BookingKindChoices.EXPERIENCE
            )
        except Booking.DoesNotExist:
            raise ParseError("This is Experience only or Not page")
    
    def get(self, request, pk, bookings_pk):
        booking = self.get_booking(bookings_pk)
        serializer = PublicBookingExperienceSerializer(booking)
        return Response(serializer.data)
    
    def put(self, request, pk, bookings_pk):
        
        booking = self.get_booking(bookings_pk)
        
        serializer = PublicBookingExperienceSerializer(
            booking,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_booking = serializer.save()
            serializer = PublicBookingExperienceSerializer(updated_booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    
    def delete(self, request, pk, bookings_pk):
        booking = self.get_booking(bookings_pk)
        booking.delete()
        return Response(status.HTTP_202_ACCEPTED)