# Property Room Types API Documentation

## Overview

This API endpoint returns all room types available for a specific property (Resort or Couple Stay). For Villa properties, it returns an empty list as villas are booked as whole units.

---

## Endpoint

**URL:** `GET /customer/property-room-types/`

**Base URL:** `http://127.0.0.1:8002` (Development)  
**Production URL:** `https://your-domain.com/customer/property-room-types/`

---

## Authentication

**Optional:** JWT Bearer Token (for protected endpoints)

**Header:**
```
Authorization: Bearer <your_jwt_token>
```

---

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `property_id` | Integer | Yes | ID of the property (villa/resort/couple stay) |

---

## Request Examples

### cURL
```bash
curl --location 'http://127.0.0.1:8002/customer/property-room-types/?property_id=3' \
--header 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### JavaScript (Fetch)
```javascript
fetch('http://127.0.0.1:8002/customer/property-room-types/?property_id=3', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

### Python (Requests)
```python
import requests

url = "http://127.0.0.1:8002/customer/property-room-types/"
params = {"property_id": 3}
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
print(data)
```

---

## Response Format

### Success Response (200 OK) - For Resort/Couple Stay

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
        },
        {
          "id": 3,
          "name": "TV"
        }
      ],
      "amenities_list": ["WiFi", "AC", "TV"]
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
          "id": 4,
          "name": "Mini Bar"
        },
        {
          "id": 5,
          "name": "Jacuzzi"
        }
      ],
      "amenities_list": ["Mini Bar", "Jacuzzi"]
    }
  ]
}
```

### Success Response (200 OK) - For Villa

```json
{
  "property_id": 1,
  "property_name": "Luxury Villa",
  "property_type": "Villa",
  "message": "Villa properties are booked as whole units and do not have individual room types.",
  "room_types": []
}
```

### Error Responses

#### 400 Bad Request - Missing property_id

```json
{
  "error": "property_id is required as query parameter."
}
```

#### 400 Bad Request - Invalid property_id

```json
{
  "error": "property_id must be a valid integer."
}
```

#### 404 Not Found - Property Not Found

```json
{
  "error": "Property with id 999 not found."
}
```

---

## Response Fields

### Main Response Object

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Integer | ID of the property |
| `property_name` | String | Name of the property |
| `property_type` | String | Type of property: "Villa", "Resort", or "Couple Stay" |
| `room_types_count` | Integer | Number of room types (only for Resort/Couple Stay) |
| `room_types` | Array | List of room type objects |
| `message` | String | Informational message (only for Villa or unknown types) |

### Room Type Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Room type ID |
| `name` | String | Name of the room type (e.g., "Deluxe Room", "Suite") |
| `user` | Integer/null | ID of the vendor who created this room type (null for system-wide room types) |
| `created_by` | Object/null | Details of the vendor who created this room type |
| `amenities` | Array | List of amenity objects with full details |
| `amenities_list` | Array | Simple list of amenity names (for easy access) |

### Created By Object (when user is not null)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Vendor user ID |
| `name` | String | Vendor's full name or mobile number |
| `email` | String | Vendor's email address |

### Amenity Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Amenity ID |
| `name` | String | Name of the amenity |

---

## Use Cases

1. **Display Room Types for Booking**: When a customer selects a Resort or Couple Stay property, use this API to show all available room types.

2. **Room Type Selection**: After getting the room types list, customers can select a specific room type to see available rooms and book.

3. **Property Information**: Get information about what room types are available in a property before showing booking options.

---

## Notes

- **Villa Properties**: Villa properties return an empty `room_types` array because villas are booked as whole units, not individual rooms.

- **Resort/Couple Stay Properties**: These properties have individual rooms grouped by room type. Each room type can have multiple physical rooms (indicated by `room_count` in the room details).

- **Room Type Uniqueness**: Each room type appears only once per property, even if there are multiple rooms of that type.

- **Amenities**: Room types include their associated amenities, which are automatically assigned when rooms are created.

---

## Related APIs

- **Get Rooms for Property**: `GET /customer/resort-and-couple-stay/{villa_id}/rooms/`
- **Get Available Rooms**: `GET /customer/available-rooms/?villa_id={id}&from_date={date}&to_date={date}`
- **Get Property Details**: `GET /customer/villas/{villa_id}/`

---

## Example Flow

1. Customer selects a Resort property (ID: 3)
2. Call this API: `GET /customer/property-room-types/?property_id=3`
3. Display the list of room types to the customer
4. Customer selects a room type (e.g., "Deluxe Room")
5. Call available rooms API with the room type filter to show available rooms
6. Customer books the desired rooms

---

## Testing

### Test with Resort Property
```bash
curl 'http://127.0.0.1:8002/customer/property-room-types/?property_id=3'
```

### Test with Villa Property
```bash
curl 'http://127.0.0.1:8002/customer/property-room-types/?property_id=1'
```

### Test Error Handling
```bash
# Missing property_id
curl 'http://127.0.0.1:8002/customer/property-room-types/'

# Invalid property_id
curl 'http://127.0.0.1:8002/customer/property-room-types/?property_id=abc'

# Non-existent property
curl 'http://127.0.0.1:8002/customer/property-room-types/?property_id=999'
```
