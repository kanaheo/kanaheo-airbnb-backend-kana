import jwt
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated

from users.models import User
from . import serializers


class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(
            user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class Users(APIView):
    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError
        serializer = serializers.PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            pass
            # 아직 여기까진 패스워드를 가지고 있지 않다 !! 따로 설정해줘야함 ! 
            user = serializer.save()    # 일단 유저는 생성 하지만 아직 password는 생성 X
            # user.password = password <- X 왜냐하면 받은 글자 그대로 패스워드에 저장함 ;; 그래서 아래처럼 하자
            user.set_password(password)
            user.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class PublicUser(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = serializers.PrivateUserSerializer(user)    # TODO 이 유저에 대한 reviews, rooms, 어떤 도시를 여행했는지 만들어보자
        return Response(serializer.data)

class ChangePassword(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        # user가 보낸 old_password가 현재의 패스워드인지 알아봐야함 
        # 1234라면 이것을 해쉬해서 다시 맞춰봐야함 그것이 바로 check_password
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not old_password or not new_password:
            raise ParseError
        
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class LogIn(APIView):
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response({"ok": "Welcome!"})
        else:
            return Response(
                {"error": "ID 또는 비밀번호가 다릅니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class LogOut(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({"ok": "byebye!"})

class JWTLogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            # sercret_key는 잘 숨겨야함 !!! 우리 사이트에 잘 왔다고 사인을 해주는거거덩 ! 
            token = jwt.encode(
                {"pk": user.pk},
                settings.SECRET_KEY,
                algorithm="HS256",
            )
            return Response({"token": token})
        else:
            return Response({"error": "wrong password"})

class GithubLogIn(APIView):
    
    def post(self, request):
        try:
            code = request.data.get("code") # 프론트에서 보내준 code로 access_token을 구해와야한다 !! 
            access_token = requests.post(
                f"https://github.com/login/oauth/access_token?code={code}&client_id=af7a7fd83e41d7e7b1de&client_secret={settings.GH_SECRET}",
                headers={"Accept": "application/json"},
            )
            access_token = access_token.json().get("access_token")  # 구해왔스 ! 그 담에 우린 access_token 이걸 가지고 github api와 대화가 가능하게 됐다 ! 즉 밑에서 user획득 가능함
            # 밑에는 기본적인 user data ( not include email)
            user_data = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            user_data = user_data.json()
            # 위에서 email이 없었으니 밑에서 불러오자 ! 
            user_emails = requests.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            user_emails = user_emails.json()
            
            try:
                user = User.objects.get(email=user_emails[0]["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data.get("login"),
                    email=user_emails[0]["email"],
                    name=user_data.get("name"),
                    avatar=user_data.get("avatar_url"),
                )
                user.set_unusable_password()    # github로그인이니까 No password!
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class KakaoLogIn(APIView):
    
    def post(self, request):
        try:
            code = request.data.get("code") # 프론트에서 보내준 code로 access_token을 구해와야한다 !! 
            access_token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": "015abcad69e4ee8079188d6742057c3f",
                    "redirect_uri": "http://127.0.0.1:3000/social/kakao",
                    "code": code
                },
            )
            access_token = access_token.json().get("access_token")  # 구해왔스 ! 그 담에 우린 access_token 이걸 가지고 github api와 대화가 가능하게 됐다 ! 즉 밑에서 user획득 가능함
            # 밑에는 기본적인 user data ( not include email)
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            try:
                user = User.objects.get(email=kakao_account.get("email"))
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    email=kakao_account.get("email"),
                    username=profile.get("nickname"),
                    name=profile.get("nickname"),
                    avatar=profile.get("profile_image_url"),
                )
                user.set_unusable_password()    # kakao로그인이니까 No password!
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
