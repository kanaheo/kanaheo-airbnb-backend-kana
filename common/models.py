from django.db import models

class CommonModel(models.Model):
    
    """Common Model Definition"""
    # 여기는 공통으로 쓰이는것들을 모아둔곳이다 ! 그래서 이 앱 자체는 DB에 저장되면 안됨 ! 
    
    created_at = models.DateTimeField(auto_now_add=True)   # 이건 처음에 저장 할 때 자동 저장됨 
    updated_at = models.DateTimeField(auto_now=True)   # 이건 오브젝트가 변경 될 때마다 자동저장
    
    class Meta:
        abstract = True
