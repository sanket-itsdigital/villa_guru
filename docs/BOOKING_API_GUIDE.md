# Complete Booking API Guide

## Overview
This guide explains how to book **Villa**, **Resort**, and **Couple Stay** properties using the booking APIs.

---

## Table of Contents
1. [Booking Villa (Whole Villa Booking)](#1-booking-villa-whole-villa-booking)
2. [Booking Resort (Room-based Booking)](#2-booking-resort-room-based-booking)
3. [Booking Couple Stay (Room-based Booking)](#3-booking-couple-stay-room-based-booking)
4. [List Bookings](#4-list-bookings)
5. [Get Booking Details](#5-get-booking-details)
6. [Calculate Booking Price](#6-calculate-booking-price)
7. [Cancel Booking](#7-cancel-booking)

---

## 1. Booking Villa (Whole Villa Booking)

### Endpoint
```
POST /customer/villa-bookings/
```

### Description
Books an entire villa. All rooms in the villa are automatically booked. No need to specify individual rooms.

### Authentication
**Required** - Bearer token in Authorization header

### Request Body
```json
{
  "villa": 1,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 8,
  "child_count": 2,
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
- `villa`: Villa ID (must be a Villa property type)
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `guest_count`: Number of adult guests
- `phone_number`: Contact phone number
- `email`: Contact email address
- `first_name`: Guest first name
- `last_name`: Guest last name

### Optional Fields
- `child_count`: Number of children (default: 0)
- `is_for_self`: Is booking for self (default: true)
- `special_request`: Special requests or notes
- `payment_type`: "online" or "cash" (default: "online")

### Important Notes
- **Do NOT include `rooms` field** - Villa bookings automatically book all rooms
- The `booking_type` is automatically set to `"whole_villa"`
- Pricing is based on villa's `price_per_night` and date-specific pricing

### Example cURL Request
```bash
curl -X POST 'https://your-domain.com/customer/villa-bookings/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "villa": 1,
    "check_in": "2026-02-01",
    "check_out": "2026-02-05",
    "guest_count": 8,
    "child_count": 2,
    "is_for_self": true,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+919876543210",
    "email": "john.doe@example.com",
    "special_request": "Late check-in requested",
    "payment_type": "online"
  }'
```

### Response (201 Created)
```json
{
  "id": 1,
  "booking_id": "RS-BK0001",
  "villa": 1,
  "villa_details": {
    "id": 1,
    "name": "Luxury Villa",
    "villa_id": "VG-001",
    "city": "Goa",
    "address": "123 Beach Road"
  },
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 8,
  "child_count": 2,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "base_amount": "80000.00",
  "gst_amount": "9600.00",
  "total_amount": "89600.00",
  "payment_status": "pending",
  "order_id": "order_abc123",
  "status": "confirmed",
  "booking_type": "whole_villa",
  "booked_rooms": [
    {
      "id": 1,
      "room": 1,
      "room_details": {
        "id": 1,
        "title": "Master Bedroom",
        "price_per_night": "20000.00"
      },
      "quantity": 1,
      "price_per_night": "20000.00"
    },
    {
      "id": 2,
      "room": 2,
      "room_details": {
        "id": 2,
        "title": "Guest Bedroom 1",
        "price_per_night": "15000.00"
      },
      "quantity": 1,
      "price_per_night": "15000.00"
    }
  ],
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

## 2. Booking Resort (Room-based Booking)

### Endpoint
```
POST /customer/villa-bookings/
```

### Description
Books specific rooms in a Resort property. You must specify which rooms and quantities you want to book.

### Authentication
**Required** - Bearer token in Authorization header

### Request Body
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

### Required Fields
- `villa`: Resort ID (must be a Resort property type)
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `guest_count`: Number of adult guests
- `phone_number`: Contact phone number
- `email`: Contact email address
- `first_name`: Guest first name
- `last_name`: Guest last name
- `rooms`: **REQUIRED** - Array of rooms to book

### Rooms Array Format
```json
"rooms": [
  {
    "room_id": 1,      // Room ID (required)
    "quantity": 2      // Number of rooms of this type (required, default: 1)
  },
  {
    "room_id": 2,
    "quantity": 1
  }
]
```

### Important Notes
- **Must include `rooms` field** - Resort bookings require room selection
- The `booking_type` is automatically set to `"selected_rooms"`
- Pricing is calculated from selected room prices
- System validates room availability before booking

### Example cURL Request
```bash
curl -X POST 'https://your-domain.com/customer/villa-bookings/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
```

### Response (201 Created)
```json
{
  "id": 2,
  "booking_id": "RS-BK0002",
  "villa": 3,
  "villa_details": {
    "id": 3,
    "name": "Beach Resort",
    "villa_id": "VG-003",
    "city": "Goa",
    "address": "456 Resort Road"
  },
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 4,
  "child_count": 0,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "base_amount": "60000.00",
  "gst_amount": "7200.00",
  "total_amount": "67200.00",
  "payment_status": "pending",
  "order_id": "order_xyz789",
  "status": "confirmed",
  "booking_type": "selected_rooms",
  "booked_rooms": [
    {
      "id": 3,
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
      "id": 4,
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
  "created_at": "2026-01-15T11:00:00Z"
}
```

---

## 3. Booking Couple Stay (Room-based Booking)

### Endpoint
```
POST /customer/villa-bookings/
```

### Description
Books specific rooms in a Couple Stay property. Same as Resort booking - you must specify which rooms and quantities.

### Authentication
**Required** - Bearer token in Authorization header

### Request Body
```json
{
  "villa": 5,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 2,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+919876543211",
  "email": "jane.smith@example.com",
  "special_request": "Romantic setup requested",
  "payment_type": "online",
  "rooms": [
    {
      "room_id": 10,
      "quantity": 1
    }
  ]
}
```

### Required Fields
Same as Resort booking - see [Section 2](#2-booking-resort-room-based-booking)

### Important Notes
- **Must include `rooms` field** - Couple Stay bookings require room selection
- The `booking_type` is automatically set to `"selected_rooms"`
- Pricing is calculated from selected room prices
- System validates room availability before booking

---

## 4. List Bookings

### Endpoint
```
GET /customer/villa-bookings/
```

### Description
Returns all bookings for the authenticated user.

### Authentication
**Required** - Bearer token in Authorization header

### Query Parameters (Optional)
- None currently supported

### Example Request
```bash
curl -X GET 'https://your-domain.com/customer/villa-bookings/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Response (200 OK)
```json
[
  {
    "id": 1,
    "booking_id": "RS-BK0001",
    "villa": 1,
    "villa_details": {
      "id": 1,
      "name": "Luxury Villa"
    },
    "check_in": "2026-02-01",
    "check_out": "2026-02-05",
    "guest_count": 8,
    "status": "confirmed",
    "payment_status": "paid",
    "total_amount": "89600.00",
    "booking_type": "whole_villa"
  },
  {
    "id": 2,
    "booking_id": "RS-BK0002",
    "villa": 3,
    "villa_details": {
      "id": 3,
      "name": "Beach Resort"
    },
    "check_in": "2026-02-10",
    "check_out": "2026-02-15",
    "guest_count": 4,
    "status": "confirmed",
    "payment_status": "pending",
    "total_amount": "67200.00",
    "booking_type": "selected_rooms"
  }
]
```

---

## 5. Get Booking Details

### Endpoint
```
GET /customer/villa-bookings/{booking_id}/
```

### Description
Returns detailed information about a specific booking.

### Authentication
**Required** - Bearer token in Authorization header

### Path Parameters
- `booking_id`: The ID of the booking

### Example Request
```bash
curl -X GET 'https://your-domain.com/customer/villa-bookings/1/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Response (200 OK)
```json
{
  "id": 1,
  "booking_id": "RS-BK0001",
  "villa": 1,
  "villa_details": {
    "id": 1,
    "name": "Luxury Villa",
    "villa_id": "VG-001",
    "city": "Goa",
    "address": "123 Beach Road",
    "main_image": "https://your-domain.com/media/villas/villa1.jpg"
  },
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 8,
  "child_count": 2,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "special_request": "Late check-in requested",
  "base_amount": "80000.00",
  "gst_amount": "9600.00",
  "total_amount": "89600.00",
  "payment_status": "paid",
  "order_id": "order_abc123",
  "status": "confirmed",
  "booking_type": "whole_villa",
  "booked_rooms": [
    {
      "id": 1,
      "room": 1,
      "room_details": {
        "id": 1,
        "title": "Master Bedroom",
        "price_per_night": "20000.00"
      },
      "quantity": 1,
      "price_per_night": "20000.00"
    }
  ],
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

## 6. Calculate Booking Price

### Endpoint
```
POST /customer/villa-prebooking-bookings/
```

### Description
Calculate the total booking price before creating the actual booking. Supports both room-based and villa-based pricing.

### Authentication
**Required** - Bearer token in Authorization header

### Request Body (Room-based - Resort/Couple Stay)
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

### Example Request
```bash
curl -X POST 'https://your-domain.com/customer/villa-prebooking-bookings/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "room_id": 1,
    "check_in": "2026-02-01",
    "check_out": "2026-02-05",
    "no_of_rooms": 2
  }'
```

### Response (200 OK)
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

## 7. Cancel Booking

### Endpoint
```
POST /customer/cancel-booking/{booking_id}/
```

### Description
Cancels a booking. Only bookings with status "confirmed" or "checked_in" can be cancelled.

### Authentication
**Required** - Bearer token in Authorization header

### Path Parameters
- `booking_id`: The ID of the booking to cancel

### Example Request
```bash
curl -X POST 'https://your-domain.com/customer/cancel-booking/1/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Response (200 OK)
```json
{
  "message": "Booking cancelled successfully",
  "booking_id": "RS-BK0001",
  "refund_amount": "89600.00"
}
```

---

## Summary

### Booking Flow

1. **Get Available Properties**
   - Use `/customer/available-villa-resort-and-couple-stay/` to find available properties
   - Filter by `property_type` to get specific type (Villa=1, Resort=2, Couple Stay=3)

2. **Get Available Rooms** (For Resort/Couple Stay only)
   - Use `/customer/available-rooms/?villa_id={id}&from_date={date}&to_date={date}`

3. **Calculate Price** (Optional)
   - Use `/customer/villa-prebooking-bookings/` to calculate price before booking

4. **Create Booking**
   - Use `POST /customer/villa-bookings/`
   - **Villa**: Don't include `rooms` field
   - **Resort/Couple Stay**: Include `rooms` array with `room_id` and `quantity`

5. **View Bookings**
   - Use `GET /customer/villa-bookings/` to list all bookings
   - Use `GET /customer/villa-bookings/{id}/` to get booking details

6. **Cancel Booking** (If needed)
   - Use `POST /customer/cancel-booking/{id}/`

---

## Error Responses

### 400 Bad Request - Missing Rooms (Resort/Couple Stay)
```json
{
  "rooms": ["Rooms must be selected for Resort/Couple Stay bookings."]
}
```

### 400 Bad Request - Room Not Available
```json
{
  "non_field_errors": [
    "Room 1 is not available for the selected dates. Only 1 room(s) available on 2026-02-01."
  ]
}
```

### 400 Bad Request - Room Doesn't Belong to Villa
```json
{
  "non_field_errors": [
    "Room 5 does not belong to this villa."
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Important Notes

1. **Property Type Behavior:**
   - **Villa**: Booked as whole unit, all rooms automatically booked
   - **Resort/Couple Stay**: Individual rooms can be selected and booked

2. **Room Selection Format:**
   ```json
   "rooms": [
     {"room_id": 1, "quantity": 2},
     {"room_id": 2, "quantity": 1}
   ]
   ```

3. **Availability Check:**
   - The booking API automatically checks room/villa availability
   - Ensures availability for all dates in the booking period
   - Validates that rooms belong to the selected villa

4. **Pricing:**
   - Room-based bookings: Sum of selected room prices × nights
   - Villa bookings: Villa's price_per_night × nights (with date-specific pricing)
   - GST, TDS, TCS are automatically calculated

5. **Payment:**
   - Razorpay order is automatically created
   - `order_id` is returned in the response
   - Use this `order_id` for payment processing

