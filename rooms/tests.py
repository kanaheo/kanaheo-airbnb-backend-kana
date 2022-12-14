from rest_framework.test import APITestCase
from . import models
from users.models import User

class TestAmenities(APITestCase):
    
    NAME = "Amenity Test"
    DESC = "Amenity Des"
    
    URL = "/api/v1/rooms/amenities/"

    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )

    def test_all_amenities(self):
        
        response = self.client.get(self.URL)
        data = response.json()
        
        self.assertEqual(
            response.status_code,
            200,
            "Status code isn't 200."
        )
        self.assertIsInstance(
            data,
            list,
        )
        self.assertEqual(
            len(data),
            1,
        )
        self.assertEqual(
            data[0]["name"],
            self.NAME,
        )
        self.assertEqual(
            data[0]["description"],
            self.DESC,
        )
    
    def test_create_amenity(self):
        
        new_amenity_name = "New Amenity"
        new_amenity_description = "New Amenity Desc"
        
        response = self.client.post(
            self.URL,
            data={
                "name": new_amenity_name,
                "description": new_amenity_description,
            }
        )
        data = response.json()
        
        self.assertEqual(
            response.status_code,
            200,
            "Not 200 status code",
        )
        
        self.assertEqual(
            data["name"], new_amenity_name
        )
        
        self.assertEqual(
            data["description"], new_amenity_description
        )
        
        response = self.client.post(self.URL)
        data = response.json()
        
        self.assertEqual(
            response.status_code,
            400
        )
        self.assertIn("name", data)

class TestAmenity(APITestCase):
    
    NAME = "Test Amenity"
    DESC = "Test Dsc"
    
    def setUp(self):
        models.Amenity.objects.create(
            name=self.NAME,
            description=self.DESC,
        )
    
    def test_amenity_not_found(self):
        response = self.client.get("/api/v1/rooms/amenities/2") # 1개에 대해서 테스트 하니까 ! pk=1이 된다 ! 하지만 이건 404 테스트 ! 잘 404가 되는지
        
        self.assertEqual(response.status_code, 404, "Page is Exists!")
    
    def test_get_amenity(self):
        
        response = self.client.get("/api/v1/rooms/amenities/1") # 1개에 대해서 테스트 하니까 ! pk=1이 된다 ! 테스트 데이터는 매번 생성하면 삭제되니까
        
        self.assertEqual(response.status_code, 200, "Page is not exists")
        
        data = response.json()
        
        self.assertEqual(data["name"], self.NAME)
        self.assertEqual(data["description"], self.DESC)
    
    def test_put_amenity(self):
        #setUp을 1개 해주니까 바로 update를 들어가도 된다.
        
        # update sucess start #
        update_amenity_name = "update Amenity"
        update_amenity_description = "update Amenity Desc"
        
        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "name": update_amenity_name,
                "description": update_amenity_description,
            }
        )
        data = response.json()
        
        self.assertEqual(
            response.status_code,
            200,
            "Not 200 status code",
        )
        
        self.assertEqual(
            data["name"], update_amenity_name
        )
        
        self.assertEqual(
            data["description"], update_amenity_description
        )
        # update sucess end #
        
        # update wrong name start #
        update_amenity_name = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "name": update_amenity_name,
            }
        )
        
        self.assertEqual(response.status_code, 400)
        # update wrong name end #
        
        # update name empty start #
        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "name": ""
            }
        )
        data = response.json()
        
        self.assertEqual(response.status_code, 400)
        # update name empty end #
        
        # update wrong desc start #
        update_amenity_description = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
        response = self.client.put(
            "/api/v1/rooms/amenities/1",
            data={
                "description": update_amenity_description,
            }
        )
        
        self.assertEqual(response.status_code, 400)
        # update wrong desc end #
    
    def test_delete_amenity(self):
        
        response = self.client.delete("/api/v1/rooms/amenities/1")
        
        self.assertEqual(response.status_code, 204)

class TestRooms(APITestCase):
    
    def setUp(self):
        # login gogo
        user = User.objects.create(
            username="test"
        )
        user.set_password("123")
        user.save()
        self.user = user
    
    def test_create_room(self):
        # not login
        response = self.client.post("/api/v1/rooms/")
        self.assertEqual(response.status_code, 403)
        #login force process
        self.client.force_login(self.user)
        response = self.client.post("/api/v1/rooms/")
