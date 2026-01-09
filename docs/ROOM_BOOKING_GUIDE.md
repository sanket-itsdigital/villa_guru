# Room Booking Guide

## Overview

This guide explains how to book rooms in Resort and Couple Stay properties. The system supports booking multiple rooms of the same type using the `quantity` field.

---

## Understanding the Data Model

### Room Types vs Rooms

- **Room Type**: A category/classification of rooms (e.g., "Deluxe Room", "Suite", "Premium")
  - Each room type can have multiple physical rooms
  - Room types are shown in the villa detail API (`/customer/villas/{id}/`)
  
- **Room (villa_rooms)**: A specific room type within a property with:
  - `room_type`: The type of room (e.g., "Deluxe Room")
  - `room_count`: Number of physical rooms of this type available
  - `price_per_night`: Price for this room type
  - `available_count`: How many are currently available
  - `booked_count`: How many are currently booked

### Example

If a resort has:
- **Room Type**: "Deluxe Room" (ID: 2)
- **Room (villa_rooms)**: ID: 5
  - `room_type`: 2 (Deluxe Room)
  - `room_count`: 4 (4 physical Deluxe rooms)
  - `price_per_night`: ₹5000
  - `available_count`: 2 (2 available for your dates)
  - `booked_count`: 2 (2 already booked)

You can book up to 2 Deluxe rooms (the available count) using `room_id: 5` and `quantity: 2`.

---

## Booking Flow

### Step 1: Get Villa Details with Room Types

**Endpoint:** `GET /customer/villas/{villa_id}/`

This returns the villa details with `room_types` (not individual rooms).

**Example Response:**
```json
{
  "id": 3,
  "name": "Beach Resort",
  "property_type": {
    "id": 2,
    "name": "Resort"
  },
  "room_types": [
    {
      "id": 2,
      "name": "Deluxe Room",
      "amenities": [...],
      "images": [...]
    },
    {
      "id": 3,
      "name": "Suite",
      "amenities": [...],
      "images": [...]
    }
  ]
}
```

### Step 2: Get Available Rooms for Your Dates

**Endpoint:** `GET /customer/available-rooms/?villa_id={villa_id}&from_date={check_in}&to_date={check_out}&room_type={room_type_id}`

This returns available rooms with their availability counts.

**Query Parameters:**
- `villa_id` (required): Property ID
- `from_date` (required): Check-in date (YYYY-MM-DD)
- `to_date` (required): Check-out date (YYYY-MM-DD)
- `room_type` (optional): Filter by room type ID

**Example Request:**
```bash
GET /customer/available-rooms/?villa_id=3&from_date=2026-04-08&to_date=2026-04-09&room_type=2
```

**Example Response:**
```json
[
  {
    "id": 5,
    "room_type": 2,
    "room_type_name": "Deluxe Room",
    "price_per_night": "5000.00",
    "room_count": 4,
    "total_rooms": 4,
    "available_count": 2,
    "booked_count": 2,
    "max_guest_count": 2,
    "villa_details": {
      "id": 3,
      "name": "Beach Resort"
    }
  }
]
```

**Key Fields:**
- `id`: This is the `room_id` you'll use for booking
- `room_type`: The room type ID
- `available_count`: How many rooms of this type are available
- `room_count`: Total number of rooms of this type

### Step 3: Book the Rooms

**Endpoint:** `POST /customer/villa-resort-and-couple-stay/bookings/`

**Request Body:**
```json
{
  "villa": 3,
  "check_in": "2026-04-08",
  "check_out": "2026-04-09",
  "guest_count": 4,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "booking_type": "selected_rooms",
  "rooms": [
    {
      "room_id": 5,
      "quantity": 2
    }
  ]
}
```

**Key Points:**
- `room_id`: The ID from the available-rooms API response
- `quantity`: Number of rooms of this type to book (must be ≤ `available_count`)
- You can book multiple different room types in one booking

---

## Booking Multiple Rooms of the Same Type

### Single Room Type, Multiple Rooms

To book multiple rooms of the same type, use the `quantity` field:

**Example: Booking 2 Deluxe Rooms**
```json
{
  "villa": 3,
  "check_in": "2026-04-08",
  "check_out": "2026-04-09",
  "booking_type": "selected_rooms",
  "rooms": [
    {
      "room_id": 5,
      "quantity": 2
    }
  ]
}
```

**Validation:**
- The system checks that `quantity ≤ available_count` for each date
- If you try to book 3 rooms but only 2 are available, you'll get an error

### Multiple Different Room Types

You can book different room types in a single booking:

**Example: Booking 2 Deluxe Rooms + 1 Suite**
```json
{
  "villa": 3,
  "check_in": "2026-04-08",
  "check_out": "2026-04-09",
  "booking_type": "selected_rooms",
  "rooms": [
    {
      "room_id": 5,
      "quantity": 2
    },
    {
      "room_id": 7,
      "quantity": 1
    }
  ]
}
```

---

## Complete Booking Example

### Scenario: Book 2 Deluxe Rooms for 2 nights

**Step 1: Get Villa Details**
```bash
GET /customer/villas/3/
```

**Step 2: Get Available Rooms**
```bash
GET /customer/available-rooms/?villa_id=3&from_date=2026-04-08&to_date=2026-04-10&room_type=2
```

**Response:**
```json
[
  {
    "id": 5,
    "room_type": 2,
    "room_type_name": "Deluxe Room",
    "price_per_night": "5000.00",
    "available_count": 2,
    "room_count": 4
  }
]
```

**Step 3: Create Booking**
```bash
POST /customer/villa-resort-and-couple-stay/bookings/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "villa": 3,
  "check_in": "2026-04-08",
  "check_out": "2026-04-10",
  "guest_count": 4,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "booking_type": "selected_rooms",
  "rooms": [
    {
      "room_id": 5,
      "quantity": 2
    }
  ]
}
```

**Success Response:**
```json
{
  "id": 123,
  "booking_id": "VG-2026-00123",
  "villa": 3,
  "villa_details": {
    "id": 3,
    "name": "Beach Resort"
  },
  "check_in": "2026-04-08",
  "check_out": "2026-04-10",
  "booking_type": "selected_rooms",
  "booked_rooms": [
    {
      "id": 1,
      "room": 5,
      "room_details": {
        "id": 5,
        "room_type_name": "Deluxe Room",
        "price_per_night": "5000.00"
      },
      "quantity": 2,
      "price_per_night": "5000.00"
    }
  ],
  "total_price": "20000.00",
  "status": "pending"
}
```

---

## Important Notes

### 1. Availability Check

The system validates availability for **each date** in your booking range:
- Checks existing bookings
- Checks room availability records
- Ensures `quantity ≤ available_count` for all dates

### 2. Room ID vs Room Type ID

- **Room Type ID** (`room_type`): Used to filter/search (e.g., "Deluxe Room")
- **Room ID** (`room_id`): Used for actual booking (the `villa_rooms` instance)

### 3. Quantity Limits

- `quantity` must be ≤ `available_count` for all dates
- You cannot book more rooms than are available
- The system checks availability across the entire date range

### 4. Price Calculation

- Price is calculated as: `price_per_night × nights × quantity`
- Each room type may have different prices
- Total booking price = sum of all room prices

### 5. Booking Multiple Room Types

You can include multiple room types in one booking:
```json
{
  "rooms": [
    {
      "room_id": 5,
      "quantity": 2
    },
    {
      "room_id": 7,
      "quantity": 1
    }
  ]
}
```

---

## Error Handling

### Common Errors

**1. Insufficient Availability**
```json
{
  "error": "Cannot book 3 room(s) of type Deluxe Room. Only 2 room(s) available on 2026-04-08 (Total: 4, Booked: 2)."
}
```
**Solution:** Reduce `quantity` to match `available_count`

**2. Room Not Found**
```json
{
  "error": "Room 999 does not belong to this villa."
}
```
**Solution:** Use the correct `room_id` from the available-rooms API

**3. Room Closed**
```json
{
  "error": "Room Deluxe Room is not available on 2026-04-08 (marked as closed)."
}
```
**Solution:** Choose different dates or a different room type

---

## Frontend Implementation Tips

### 1. Room Selection Flow

```javascript
// 1. Get villa details with room types
const villa = await fetch(`/customer/villas/${villaId}/`);

// 2. User selects a room type
const selectedRoomType = villa.room_types[0]; // e.g., "Deluxe Room"

// 3. Get available rooms for selected dates
const availableRooms = await fetch(
  `/customer/available-rooms/?villa_id=${villaId}&from_date=${checkIn}&to_date=${checkOut}&room_type=${selectedRoomType.id}`
);

// 4. Show available rooms with quantity selector
// availableRooms[0].available_count shows max quantity

// 5. User selects quantity and books
const booking = {
  villa: villaId,
  check_in: checkIn,
  check_out: checkOut,
  rooms: [{
    room_id: availableRooms[0].id,
    quantity: selectedQuantity // ≤ availableRooms[0].available_count
  }]
};
```

### 2. Quantity Selector

```javascript
// Max quantity based on available_count
const maxQuantity = availableRoom.available_count;
// Show quantity selector: 1 to maxQuantity
```

### 3. Real-time Availability

- Call `/customer/available-rooms/` whenever dates change
- Update `available_count` in real-time
- Disable booking if `available_count = 0`

---

## Summary

1. **Get room types** from `/customer/villas/{id}/`
2. **Get available rooms** from `/customer/available-rooms/` with date range and optional `room_type` filter
3. **Book using `room_id` and `quantity`** - the `quantity` field allows booking multiple rooms of the same type
4. **Multiple room types** can be booked in a single booking by including multiple entries in the `rooms` array

The system already supports booking multiple rooms of the same type - just use the `quantity` field in your booking request!
