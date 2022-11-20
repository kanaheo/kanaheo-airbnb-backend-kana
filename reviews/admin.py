from django.contrib import admin
from .models import Review

class WordFilter(admin.SimpleListFilter):
    
    title = "Filter by Words!"
    
    parameter_name = "word"
    
    def lookups(self, request, model_admin):
        return [
            ("good", "Good"),
            ("greate", "Greate"),
            ("awesome", "Awesome"),
        ]
    
    def queryset(self, request, reviews):
        word = self.value()
        if word:
            return reviews.filter(payload__contains=word)
        else:
            reviews

class IsGoodBadReviewFilter(admin.SimpleListFilter):
    
    title = "Filter By Good | Bad"
    
    parameter_name = "judge"
    
    def lookups(self, request, model_admin):
        return [
            ("good", "⭐️⭐️⭐️이상"),
            ("bad", "⭐️⭐️이하"),
        ]
    
    def queryset(self, request, reviews):
        score = self.value()
        if score == "good":
            return reviews.filter(rating__gte=3)
        elif score == "bad":
            return reviews.filter(rating__lt=3)
        else:
            reviews

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    
    list_display = (
        "__str__",
        "payload"
    )
    
    list_filter = (
        WordFilter,
        IsGoodBadReviewFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly"
    )
