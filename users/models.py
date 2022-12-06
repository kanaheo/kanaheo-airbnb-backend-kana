from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    class GenderChoices(models.TextChoices):
        MALE = ("male", "Male") # 첫번째 인자가 데이터베이스 들어갈 value 두번째 인자는 우리가 보는 곳!
        FEMAILE = ("female", "Female")
        
    class LanguageChoices(models.TextChoices):
        KR = ("kr", "Korean")
        EN = ("en", "English")
    
    class CurrencyChoices(models.TextChoices):
        WON = "won", "Korean Won"   # 이거나 튜플이나 같다네?
        USD = "usd", "Dollar"
    
    first_name = models.CharField(max_length=150, editable=False)
    last_name = models.CharField(max_length=150, editable=False)
    avatar = models.URLField(blank=True)
    name = models.CharField(max_length=150, default="")
    is_host = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    language = models.CharField(max_length=2, choices=LanguageChoices.choices)
    currency = models.CharField(max_length=5, choices=CurrencyChoices.choices)
    