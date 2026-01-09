# Room Booking API Guide

## Overview
This guide explains how to show all rooms to customers and how to book resort/couple stay rooms.

---

## 1. List All Rooms for a Villa

### Endpoint
```
GET /customer/villas/{villa_id}/rooms/
```

### Description
Returns all rooms for a specific villa. **Note:** This API only returns rooms for **Resort** and **Couple Stay** properties. For **Villa** properties, this will return an empty list since villas are booked as a whole unit.

### Parameters
- `villa_id` (path parameter, required): The ID of the villa

### Query Parameters (Optional)
- `room_type`: Filter by room type ID
- `price_min`: Minimum price filter
- `price_max`: Maximum price filter
- Other filters from `VillaRoomFilter`

### Example Request
```bash
GET /customer/villas/3/rooms/
```

### Example Response
```json
[
  {
    "id": 1,
    "room_type": 1,
    "room_type_name": "Deluxe",
    "title": "Ocean View Room",
    "price_per_night": "5000.00",
    "max_guest_count": 2,
    "refundable": true,
    "meals_included": false,
    "capacity": "2 Adults",
    "view": "Ocean View",
    "bed_type": "King Size",
    "villa_amenity_details": [
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
      "id": 3,
      "name": "Beach Resort",
      "villa_id": "VG003",
      "city": "Goa",
      "address": "123 Beach Road"
    }
  }
]
```

---

## 2. Get Available Rooms (with Date Filter)

### Endpoint
```
GET /customer/available-rooms/
```

### Description
Returns rooms that are available for specific check-in and check-out dates. Only shows rooms for **Resort** and **Couple Stay** properties.

### Query Parameters (Required)
- `villa_id` (required): Villa/Resort/Couple Stay ID
- `from_date` (required): Check-in date (YYYY-MM-DD)
- `to_date` (required): Check-out date (YYYY-MM-DD)

### Query Parameters (Optional)
- `room_type` (optional): Filter by room type ID - Returns only rooms of the specified room type
- `price_min` (optional): Minimum price per night filter
- `price_max` (optional): Maximum price per night filter
- `title` (optional): Filter by package type (e.g., "room_only", "breakfast", "all_meals")
- `bed_type` (optional): Filter by bed type (partial match, case-insensitive)
- `capacity` (optional): Filter by capacity description (partial match, case-insensitive)
- `view` (optional): Filter by view description (partial match, case-insensitive)
- `villa_amenities` (optional): Filter by amenity IDs (comma-separated, e.g., "1,2,3")

### Example Request (Basic)
```bash
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09
```

### Example Request (With Room Type Filter)
```bash
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09&room_type=2
```

### Example Request (With Multiple Filters)
```bash
GET /customer/available-rooms/?villa_id=5&from_date=2026-04-08&to_date=2026-04-09&room_type=2&price_min=1000&price_max=5000
```

### Example Response
```json
[
  {
    "id": 1,
    "room_type": 2,
    "room_type_name": "Deluxe Room",
    "title": "room_only",
    "price_per_night": "5000.00",
    "max_guest_count": 2,
    "room_count": 4,
    "total_rooms": 4,
    "available_count": 2,
    "booked_count": 2,
    "capacity": "2 Adults",
    "view": "Ocean View",
    "bed_type": "King Size",
    "villa_amenity_details": [
      {
        "id": 1,
        "name": "WiFi"
      },
      {
        "id": 2,
        "name": "AC"
      }
    ],
    "images": [
      {
        "id": 1,
        "image": "/media/hotels/room1.jpg"
      }
    ],
    "villa_details": {
      "id": 5,
      "name": "Beach Resort",
      "villa_id": "RS-005",
      "city": "Goa",
      "address": "123 Beach Road"
    }
  }
]
```

### Notes
- The `room_type` filter accepts the room type ID (integer)
- When `room_type` is provided, only rooms of that specific type are returned
- The response includes `room_count`, `available_count`, and `booked_count` to show availability
- `available_count` shows how many rooms of this type are available for the specified date range

---

## 3. Book Resort/Couple Stay Rooms

### Endpoint
```
POST /customer/villa-bookings/
```

### Description
Creates a booking for resort or couple stay rooms. For **Villa** properties, use this API without the `rooms` parameter (whole villa booking).

### Authentication
Required - Bearer token in Authorization header

### Request Body (Resort/Couple Stay - Room-based Booking)
```json
{
  "villa": 3,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 4,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "special_request": "Late check-in requested",
  "payment_type": "online",
  "rooms": [
    {
      "room_id": 1,
      "quantity": 2
    },
    {
      "room_id": 2,
      "quantity": 1
    }
  ]
}
```

### Request Body (Villa - Whole Villa Booking)
```json
{
  "villa": 1,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 8,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "special_request": "Late check-in requested",
  "payment_type": "online"
}
```

### Required Fields
- `villa`: Villa/Resort ID
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `guest_count`: Number of guests
- `phone_number`: Contact phone number
- `email`: Contact email address
- `first_name`: Guest first name
- `last_name`: Guest last name
- `rooms`: **Required for Resort/Couple Stay**, **Not needed for Villa** (whole villa booking)

### Response (201 Created)
```json
{
  "id": 1,
  "booking_id": "RS-BK0001",
  "villa": 3,
  "villa_details": {
    "id": 3,
    "name": "Beach Resort",
    "villa_id": "VG003"
  },
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 4,
  "child_count": 0,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "base_amount": "40000.00",
  "gst_amount": "4800.00",
  "total_amount": "44800.00",
  "payment_status": "pending",
  "order_id": "order_abc123",
  "status": "confirmed",
  "booking_type": "selected_rooms",
  "booked_rooms": [
    {
      "id": 1,
      "room": 1,
      "room_details": {
        "id": 1,
        "title": "Ocean View Room",
        "price_per_night": "5000.00"
      },
      "quantity": 2,
      "price_per_night": "5000.00"
    },
    {
      "id": 2,
      "room": 2,
      "room_details": {
        "id": 2,
        "title": "Garden View Room",
        "price_per_night": "4000.00"
      },
      "quantity": 1,
      "price_per_night": "4000.00"
    }
  ],
  "created_at": "2026-01-15T10:30:00Z"
}
```

### Error Responses

#### 400 Bad Request - Missing Rooms
```json
{
  "rooms": ["Rooms must be selected for Resort/Couple Stay bookings."]
}
```

#### 400 Bad Request - Room Not Available
```json
{
  "non_field_errors": [
    "Room 1 is not available for the selected dates. Only 1 room(s) available on 2026-02-01."
  ]
}
```

#### 400 Bad Request - Room Doesn't Belong to Villa
```json
{
  "non_field_errors": [
    "Room 5 does not belong to this villa."
  ]
}
```

---

## 4. Calculate Booking Price (Pre-booking)

### Endpoint
```
POST /customer/villa-prebooking-bookings/
```

### Description
Calculate the total booking price before creating the actual booking. Supports both room-based and villa-based pricing.

### Request Body (Room-based)
```json
{
  "room_id": 1,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "no_of_rooms": 2
}
```

### Request Body (Villa-based)
```json
{
  "hotel_id": 1,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05"
}
```

### Response
```json
{
  "nights": 4,
  "price_per_night": "5000.00",
  "base_amount": "40000.00",
  "gst_amount": "4800.00",
  "total_amount": "44800.00",
  "tds_amount": "75.00",
  "tcs_amount": "375.00"
}
```

---

## Summary

### To Show All Rooms:
1. **List all rooms for a villa**: `GET /customer/villas/{villa_id}/rooms/`
   - Shows all rooms for Resort/Couple Stay properties
   - Returns empty for Villa properties

2. **Get available rooms**: `GET /customer/available-rooms/?hotel_id={villa_id}&from_date={date}&to_date={date}`
   - Shows only available rooms for specific dates
   - Only for Resort/Couple Stay properties

### To Get All Resort and Couple Stay Properties:
Use the general villa list API with property type filter:
```
GET /customer/villas/?property_type={property_type_id}
```
You can filter by property type ID to get only Resort or Couple Stay properties.

### To Book Rooms:
1. **Create booking**: `POST /customer/villa-bookings/`
   - For Resort/Couple Stay: Include `rooms` array with `room_id` and `quantity`
   - For Villa: Don't include `rooms` (whole villa booking)
   - Automatically calculates pricing based on booking type

2. **Calculate price first**: `POST /customer/villa-prebooking-bookings/`
   - Use `room_id` for room-based pricing
   - Use `hotel_id` for villa-based pricing

---

## Important Notes

1. **Property Type Behavior:**
   - **Villa**: Booked as whole unit, no room selection needed
   - **Resort/Couple Stay**: Individual rooms can be selected and booked

2. **Room Selection Format:**
   ```json
   "rooms": [
     {"room_id": 1, "quantity": 2},
     {"room_id": 2, "quantity": 1}
   ]
   ```

3. **Availability Check:**
   - The booking API automatically checks room availability
   - Ensures rooms are available for all dates in the booking period
   - Validates that rooms belong to the selected villa

4. **Pricing:**
   - Room-based bookings: Sum of selected room prices
   - Villa bookings: Villa's price_per_night
   - GST, TDS, TCS are automatically calculated

