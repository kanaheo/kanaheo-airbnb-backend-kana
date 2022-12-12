# kanaheo-airbnb-backend-kana

Airbnb PJ

### API

### Categories

GET POST /categories  
GET(Rooms) PUT DELETE /categories/1

### Rooms

GET POST /rooms  
GET PUT DELETE /rooms/1  
GET /rooms/1/amenities  
GET POST /rooms/1/reviews  
GET POST /amenities  
GET PUT DELETE /amenities/1  
POST /rooms/1/photos  
DELETE /rooms/1/photos/1  
GET POST /rooms/1/bookings

### Wishlists(Room, Experience)

GET POST /wishlists  
GET PUT DELETE /wishlists/1  
PUT /wishlists/1/rooms

### Users

GET PUT /me  
POST /users  
GET /users/@username  
GET /users/@username/reviews  
POST /users/change-password  
POST /users/github  
POST /users/log-in  
POST /users/log-out

### Experiences

GET POST /experiences  
GET PUT DELETE /experiences/1  
GET POST /experiences/1/reviews  
GET /experiences/1/perks  
GET POST /experiences/1/bookings  
GET PUT DELETE /experiences/1/bookings/2  
GET POST /perks  
GET PUT DELETE /perks/1

### Medias

POST /medias  
DELETE /medias/1
