# Villa Guru API Documentation

**Base URL:** `http://127.0.0.1:8002` (Development)  
**API Version:** v1  
**Authentication:** JWT Bearer Token (for protected endpoints)

---

## Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [User Management APIs](#user-management-apis)
3. [Villa APIs](#villa-apis)
4. [Booking APIs](#booking-apis)
5. [Support Ticket APIs](#support-ticket-apis)
6. [Master Data APIs](#master-data-apis)

---

## Authentication APIs

### 1. User Registration (Signup)

**Endpoint:** `POST /users/signup/`

**Description:** Register a new user with Firebase authentication

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "idToken": "firebase_id_token_here",
  "user_type": "customer",
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Parameters:**
- `idToken` (required): Firebase ID token from phone authentication
- `user_type` (required): One of `"customer"`, `"doctor"`, `"daycare"`, `"service_provider"`
- `name` (optional): User's full name
- `email` (optional): User's email address

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "mobile": "+1234567890",
    "email": "john@example.com",
    "name": "John Doe",
    "user_type": "customer",
    "created": true
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "idToken and user_type are required"
}
```

---

### 2. User Login

**Endpoint:** `POST /users/login/`

**Description:** Login user with Firebase authentication

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "idToken": "firebase_id_token_here",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Parameters:**
- `idToken` (required): Firebase ID token
- `email` (optional): User's email
- `first_name` (optional): User's first name
- `last_name` (optional): User's last name

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "mobile": "+1234567890",
    "is_customer": true,
    "created": false
  },
  "user_details": {
    "id": 1,
    "mobile": "+1234567890",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile_photo": null,
    "is_customer": true,
    "is_service_provider": false
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Invalid or expired Firebase token."
}
```

---

### 3. Get User Profile

**Endpoint:** `GET /users/get-user/`

**Description:** Get current user's basic information

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

### 4. Update User Profile

**Endpoint:** `PUT /users/update-user/`

**Description:** Update user's name and email

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Profile updated successfully."
}
```

---

### 5. Reset Password

**Endpoint:** `POST /users/reset-password/`

**Description:** Reset user password using Firebase token

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "idToken": "firebase_id_token_here",
  "new_password": "newSecurePassword123"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password reset successfully."
}
```

---

## Villa APIs

### 6. List Villas

**Endpoint:** `GET /customer/villas/`

**Description:** Get list of all active villas with filtering options

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `name` (optional): Filter by villa name (partial match)
- `city` (optional): Filter by city ID
- `category` (optional): Filter by category (Budget, Mid_range, Premium, Boutique)
- `is_featured` (optional): Filter featured villas (true/false)
- `is_recommended` (optional): Filter recommended villas (true/false)
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter

**Example Request:**
```
GET /customer/villas/?city=1&is_featured=true&category=Premium
```

**Success Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Luxury Beach Villa",
      "villa_id": "VG001",
      "category": "Premium",
      "no_of_rooms": 5,
      "address": "123 Beach Road",
      "city": "Goa",
      "pincode": 403001,
      "star_rating": 5,
      "overall_rating": "4.5",
      "main_image": "/media/hotels/villa1.jpg",
      "price_per_night": "15000.00",
      "marked_up_price_per_night": "16500.00",
      "min_price": "12000.00",
      "max_price": "20000.00",
      "is_featured": true,
      "is_recommended": true,
      "description": "Beautiful beachfront villa with ocean views",
      "amenities": [
        {
          "id": 1,
          "name": "Swimming Pool",
          "image": "/media/amenities/pool.jpg"
        }
      ],
      "rooms": [
        {
          "id": 1,
          "title": "Master Bedroom",
          "price_per_night": "15000.00",
          "max_guest_count": 2,
          "room_type_name": "Deluxe"
        }
      ],
      "images": [
        {
          "id": 1,
          "image": "/media/hotels/villa1_1.jpg"
        }
      ]
    }
  ]
}
```

---

### 7. Get Villa Details

**Endpoint:** `GET /customer/villas/{villa_id}/`

**Description:** Get detailed information about a specific villa

**Request Headers:**
```
Content-Type: application/json
```

**Path Parameters:**
- `villa_id` (required): Villa ID

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Luxury Beach Villa",
  "villa_id": "VG001",
  "category": "Premium",
  "no_of_rooms": 5,
  "address": "123 Beach Road",
  "city": "Goa",
  "landmark": "Near Beach",
  "pincode": 403001,
  "star_rating": 5,
  "overall_rating": "4.5",
  "main_image": "/media/hotels/villa1.jpg",
  "price_per_night": "15000.00",
  "marked_up_price_per_night": "16500.00",
  "min_price": "12000.00",
  "max_price": "20000.00",
  "is_featured": true,
  "is_recommended": true,
  "description": "Beautiful beachfront villa with ocean views",
  "amenities": [...],
  "rooms": [...],
  "images": [...]
}
```

---

### 8. Get Villa Rooms

**Endpoint:** `GET /customer/villas/{villa_id}/rooms/`

**Description:** Get all rooms for a specific villa

**Request Headers:**
```
Content-Type: application/json
```

**Path Parameters:**
- `villa_id` (required): Villa ID

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "room_type": 1,
    "room_type_name": "Deluxe",
    "title": "Master Bedroom",
    "price_per_night": "15000.00",
    "max_guest_count": 2,
    "refundable": true,
    "meals_included": true,
    "capacity": "2 Adults",
    "view": "Ocean View",
    "bed_type": "King Size",
    "room_amenity_details": [
      {
        "id": 1,
        "name": "WiFi"
      }
    ],
    "images": [
      {
        "id": 1,
        "image": "/media/rooms/room1.jpg"
      }
    ],
    "villa_details": {
      "id": 1,
      "name": "Luxury Beach Villa",
      "villa_id": "VG001",
      "city": "Goa",
      "address": "123 Beach Road"
    }
  }
]
```

---

### 9. Get Room Details

**Endpoint:** `GET /customer/room/{room_id}/`

**Description:** Get detailed information about a specific room

**Request Headers:**
```
Content-Type: application/json
```

**Path Parameters:**
- `room_id` (required): Room ID

**Success Response (200 OK):**
```json
{
  "id": 1,
  "room_type": 1,
  "room_type_name": "Deluxe",
  "title": "Master Bedroom",
  "price_per_night": "15000.00",
  "max_guest_count": 2,
  "refundable": true,
  "meals_included": true,
  "capacity": "2 Adults",
  "view": "Ocean View",
  "bed_type": "King Size",
  "room_amenity_details": [...],
  "images": [...],
  "villa_details": {...}
}
```

---

### 10. Get Property Room Types

**Endpoint:** `GET /customer/property-room-types/`

**Description:** Get all room types available for a specific property (Resort or Couple Stay). For Villa properties, returns an empty list as villas are booked as whole units.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <token> (optional)
```

**Query Parameters:**
- `property_id` (required): ID of the property (villa/resort/couple stay)

**Example Request:**
```
GET /customer/property-room-types/?property_id=3
```

**Success Response (200 OK) - For Resort/Couple Stay:**
```json
{
  "property_id": 3,
  "property_name": "Beach Resort",
  "property_type": "Resort",
  "room_types_count": 2,
  "room_types": [
    {
      "id": 1,
      "name": "Deluxe Room",
      "user": null,
      "created_by": null,
      "amenities": [
        {
          "id": 1,
          "name": "WiFi"
        },
        {
          "id": 2,
          "name": "AC"
        }
      ],
      "amenities_list": ["WiFi", "AC"]
    },
    {
      "id": 2,
      "name": "Suite",
      "user": 2,
      "created_by": {
        "id": 2,
        "name": "John Doe",
        "email": "vendor@example.com"
      },
      "amenities": [
        {
          "id": 3,
          "name": "Mini Bar"
        }
      ],
      "amenities_list": ["Mini Bar"]
    }
  ]
}
```

**Success Response (200 OK) - For Villa:**
```json
{
  "property_id": 1,
  "property_name": "Luxury Villa",
  "property_type": "Villa",
  "message": "Villa properties are booked as whole units and do not have individual room types.",
  "room_types": []
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "property_id is required as query parameter."
}
```

**404 Not Found:**
```json
{
  "error": "Property with id 999 not found."
}
```

---

### 11. Get Available Rooms

**Endpoint:** `GET /customer/available-rooms/`

**Description:** Get available rooms based on check-in and check-out dates

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `villa_id` (required): ID of the property (villa/resort/couple stay)
- `from_date` (required): Check-in date (YYYY-MM-DD)
- `to_date` (required): Check-out date (YYYY-MM-DD)
- `room_type` (optional): Filter by room type ID
- `price_min` (optional): Minimum price per night
- `price_max` (optional): Maximum price per night
- `title` (optional): Filter by package type (e.g., "room_only", "breakfast")
- `bed_type` (optional): Filter by bed type (partial match)
- `capacity` (optional): Filter by capacity (partial match)
- `view` (optional): Filter by view (partial match)
- `villa_amenities` (optional): Filter by amenity IDs (comma-separated)

**Example Request:**
```
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09
```

**Example Request with Room Type Filter:**
```
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09&room_type=2
```

**Example Request with Multiple Filters:**
```
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09&room_type=2&price_min=1000&price_max=5000
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "room_type": 1,
    "title": "Master Bedroom",
    "price_per_night": "15000.00",
    "available": true,
    "villa_details": {...}
  }
]
```

---

### 12. Get Available Villas

**Endpoint:** `POST /customer/available-villas/`

**Description:** Get available villas for whole villa booking

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "city": 1
}
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Luxury Beach Villa",
    "villa_id": "VG001",
    "price_per_night": "15000.00",
    "marked_up_price_per_night": "16500.00",
    "available": true
  }
]
```

---

## Booking APIs

### 12. Calculate Booking Price

**Endpoint:** `POST /customer/villa-prebooking-bookings/`

**Description:** Calculate total booking price before creating booking

**Request Headers:**
```
Content-Type: application/json
```

**Request Body (Room-based booking):**
```json
{
  "room_id": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "no_of_rooms": 2
}
```

**Request Body (Villa-based booking):**
```json
{
  "hotel_id": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20"
}
```

**Success Response (200 OK):**
```json
{
  "nights": 5,
  "price_per_night": "15000.00",
  "base_amount": "75000.00",
  "gst_amount": "9000.00",
  "total_amount": "84000.00",
  "tds_amount": "75.00",
  "tcs_amount": "375.00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Either room_id or hotel_id is required"
}
```

---

### 13. Create Booking

**Endpoint:** `POST /customer/villa-bookings/`

**Description:** Create a new villa booking

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body (Room-based booking):**
```json
{
  "room": 1,
  "villa": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "no_of_rooms": 2,
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_mobile": "+1234567890",
  "guest_count": 4,
  "special_requests": "Late check-in requested"
}
```

**Request Body (Villa-based booking - whole villa):**
```json
{
  "villa": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_mobile": "+1234567890",
  "guest_count": 8,
  "special_requests": "Late check-in requested"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "booking_id": "VG-BK-20240115-001",
  "villa": 1,
  "room": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "no_of_rooms": 2,
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "guest_mobile": "+1234567890",
  "guest_count": 4,
  "total_amount": "84000.00",
  "payment_status": "pending",
  "order_id": "order_abc123xyz",
  "status": "pending",
  "special_requests": "Late check-in requested",
  "room_details": {...},
  "villa_details": {...}
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": ["Check-in cannot be in the past."]
}
```

---

### 14. List Bookings

**Endpoint:** `GET /customer/villa-bookings/`

**Description:** Get list of user's bookings

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Query Parameters:**
- `villa` (optional): Filter by villa ID
- `check_in` (optional): Filter by check-in date (gte)
- `check_out` (optional): Filter by check-out date (lte)
- `booking_id` (optional): Filter by booking ID (partial match)

**Success Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "booking_id": "VG-BK-20240115-001",
      "villa": 1,
      "room": 1,
      "check_in": "2024-01-15",
      "check_out": "2024-01-20",
      "total_amount": "84000.00",
      "payment_status": "paid",
      "status": "confirmed",
      "room_details": {...},
      "villa_details": {...}
    }
  ]
}
```

---

### 15. Get Booking Details

**Endpoint:** `GET /customer/villa-bookings/{booking_id}/`

**Description:** Get detailed information about a specific booking

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "booking_id": "VG-BK-20240115-001",
  "villa": 1,
  "room": 1,
  "check_in": "2024-01-15",
  "check_out": "2024-01-20",
  "total_amount": "84000.00",
  "payment_status": "paid",
  "status": "confirmed",
  "room_details": {...},
  "villa_details": {...}
}
```

---

### 16. Cancel Booking

**Endpoint:** `POST /customer/cancel-booking/{booking_id}/`

**Description:** Cancel a booking

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Path Parameters:**
- `booking_id` (required): Booking ID

**Success Response (200 OK):**
```json
{
  "message": "Booking cancelled successfully",
  "refund_amount": "84000.00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Booking cannot be cancelled. Check-in date is less than 24 hours away."
}
```

---

## Support Ticket APIs

### 17. Create Support Ticket

**Endpoint:** `POST /customer/tickets/`

**Description:** Create a new support ticket

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "subject": "Issue with booking",
  "booking": 1
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "subject": "Issue with booking",
  "booking": 1,
  "is_resolved": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 18. List Support Tickets

**Endpoint:** `GET /customer/tickets/`

**Description:** Get list of user's support tickets

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "subject": "Issue with booking",
    "booking": 1,
    "is_resolved": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

### 19. Add Ticket Message

**Endpoint:** `POST /customer/ticket-messages/`

**Description:** Add a message to a support ticket

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "ticket": 1,
  "message": "I need help with my booking cancellation"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "ticket": 1,
  "sender": 1,
  "sender_name": "John Doe",
  "message": "I need help with my booking cancellation",
  "created_at": "2024-01-15T10:35:00Z",
  "is_from_user": true
}
```

---

### 20. List Ticket Messages

**Endpoint:** `GET /customer/ticket-messages/?ticket={ticket_id}`

**Description:** Get all messages for a specific ticket

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Query Parameters:**
- `ticket` (required): Ticket ID

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "ticket": 1,
    "sender": 1,
    "sender_name": "John Doe",
    "message": "I need help with my booking cancellation",
    "created_at": "2024-01-15T10:35:00Z",
    "is_from_user": true
  }
]
```

---

## Master Data APIs

### 21. Get Cities

**Endpoint:** `GET /masters/get-city/`

**Description:** Get list of all cities

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Goa",
    "image": "/media/city_images/goa.jpg"
  }
]
```

---

### 22. Get Amenities

**Endpoint:** `GET /masters/get-amenity/`

**Description:** Get list of all amenities

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Swimming Pool",
    "image": "/media/amenities/pool.jpg"
  }
]
```

---

### 23. Get Property Types

**Endpoint:** `GET /masters/get-property-type/`

**Description:** Get list of all property types

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Villa"
  }
]
```

---

### 24. Get Room Types

**Endpoint:** `GET /masters/get-room-type/`

**Description:** Get list of all room types

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Deluxe"
  }
]
```

---

### 25. Get Room Amenities

**Endpoint:** `GET /masters/get-room-amenity/`

**Description:** Get list of all room amenities

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "WiFi"
  }
]
```

---

### 26. Get Coupons

**Endpoint:** `GET /masters/get-coupon/`

**Description:** Get list of all active coupons

**Request Headers:**
```
Content-Type: application/json
```

**Query Parameters:**
- `is_active` (optional): Filter by active status (true/false)
- `code` (optional): Filter by coupon code

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "SUMMER20",
    "title": "Summer Discount",
    "type": "percent",
    "discount_percentage": 20.00,
    "discount_amount": null,
    "min_purchase": 1000.00,
    "max_discount": 5000.00,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "is_active": true
  }
]
```

---

### 27. Get Events

**Endpoint:** `GET /masters/get-event/`

**Description:** Get list of upcoming events

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "New Year Celebration",
    "description": "Special New Year event",
    "image": "/media/events/newyear.jpg",
    "itinerary": "Day 1: Welcome, Day 2: Activities",
    "amount": "5000.00",
    "start_date": "2024-12-31T18:00:00Z"
  }
]
```

---

### 28. Get Testimonials

**Endpoint:** `GET /masters/get-testimonials/`

**Description:** Get list of all testimonials

**Request Headers:**
```
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "description": "Great experience!",
    "rating": 5.0,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

---

### 29. Create Customer Address

**Endpoint:** `POST /masters/customer-address/`

**Description:** Create a new customer address

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "type": "Home",
  "address": "123 Main Street",
  "landmark": "Near Park",
  "pin_code": "123456",
  "city": "Mumbai",
  "state": "Maharashtra"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "name": "John Doe",
  "type": "Home",
  "address": "123 Main Street",
  "landmark": "Near Park",
  "pin_code": "123456",
  "city": "Mumbai",
  "state": "Maharashtra"
}
```

---

### 30. List Customer Addresses

**Endpoint:** `GET /masters/customer-address/`

**Description:** Get list of user's addresses

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "name": "John Doe",
    "type": "Home",
    "address": "123 Main Street",
    "landmark": "Near Park",
    "pin_code": "123456",
    "city": "Mumbai",
    "state": "Maharashtra"
  }
]
```

---

### 31. Get Customer Addresses (Alternative)

**Endpoint:** `GET /masters/get-customer-address/`

**Description:** Get list of user's addresses (alternative endpoint)

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "name": "John Doe",
    "type": "Home",
    "address": "123 Main Street",
    "landmark": "Near Park",
    "pin_code": "123456",
    "city": "Mumbai",
    "state": "Maharashtra"
  }
]
```

---

## User Profile APIs

### 32. Get User Profile

**Endpoint:** `GET /users/profile/`

**Description:** Get current user's profile

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "firebase_uid": "firebase_uid_here",
  "mobile": "+1234567890",
  "email": "john@example.com",
  "profile_photo": "/media/profile_photos/user1.jpg",
  "first_name": "John",
  "last_name": "Doe",
  "is_customer": true,
  "is_service_provider": false
}
```

---

### 33. Update User Profile

**Endpoint:** `PUT /users/profile/`

**Description:** Update user's profile

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "profile_photo": null
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "firebase_uid": "firebase_uid_here",
  "mobile": "+1234567890",
  "email": "newemail@example.com",
  "profile_photo": null,
  "first_name": "John",
  "last_name": "Smith",
  "is_customer": true,
  "is_service_provider": false
}
```

---

## Favourite Villas APIs

### 34. Add Favourite Villa

**Endpoint:** `POST /customer/favourite-villas/`

**Description:** Add a villa to user's favourites

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "villa": 1
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "user": 1,
  "villa": 1
}
```

---

### 35. List Favourite Villas

**Endpoint:** `GET /customer/favourite-villas/`

**Description:** Get list of user's favourite villas

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": 1,
    "villa": 1
  }
]
```

---

### 36. Remove Favourite Villa

**Endpoint:** `DELETE /customer/favourite-villas/{favourite_id}/`

**Description:** Remove a villa from user's favourites

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Success Response (204 No Content):**
```
(Empty response body)
```

---

## Payment Webhook

### 37. Razorpay Booking Webhook

**Endpoint:** `POST /customer/booking/webhook/`

**Description:** Webhook endpoint for Razorpay payment notifications

**Request Headers:**
```
Content-Type: application/json
X-Razorpay-Signature: {signature}
```

**Request Body:**
```json
{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_abc123",
        "order_id": "order_xyz789",
        "status": "captured",
        "amount": 8400000
      }
    }
  }
}
```

**Success Response (200 OK):**
```json
{
  "status": "success"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Error message here"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

To get an access token, use the login or signup endpoints.

---

## Rate Limiting

Currently, there are no rate limits implemented. However, please use the API responsibly.

---

## Support

For API support, please contact: villaguru@gmail.com

---

## Changelog

### Version 1.0 (Current)
- Initial API documentation
- All endpoints documented with sample payloads and responses

---

**Last Updated:** January 2024

