# Price Calculation API with Coupon and Weekend Pricing

## Endpoint
**POST** `/customer/calculate-price-with-coupon/`

## Description
This API calculates the booking price with automatic weekend pricing and optional coupon discount. The booking type is automatically determined based on the property type:
- **Villa Property**: Whole villa booking (rooms not required)
- **Resort/Couple Stay Property**: Room-based booking (rooms required)

The API automatically:
- Determines booking type based on property type
- Calculates daily prices considering weekend pricing (Friday, Saturday, Sunday)
- Applies date-specific pricing if configured
- Validates and applies coupon codes
- Returns detailed price breakdown

## Request Body

### For Villa Property (Whole Villa Booking)
```json
{
  "villa_id": 1,
  "check_in": "2024-12-20",
  "check_out": "2024-12-25",
  "coupon_code": "DISCOUNT10"  // Optional
}
```
**Note**: For Villa property type, `rooms` is not required and will be ignored if provided.

### For Resort/Couple Stay Property (Room-based Booking)
```json
{
  "villa_id": 3,
  "check_in": "2026-01-08",
  "check_out": "2026-01-25",
  "rooms": [
    {
      "room_id": 1
    },
    {
      "room_id": 2
    }
  ],
  "coupon_code": "DISCOUNT10"  // Optional
}
```

### With Quantity (Optional)
```json
{
  "villa_id": 3,
  "check_in": "2026-01-08",
  "check_out": "2026-01-25",
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

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `villa_id` | integer | **Yes** | Villa ID (always required) |
| `rooms` | array | **Conditional** | Required for Resort and Couple Stay properties. Not needed for Villa properties. |
| `check_in` | string (YYYY-MM-DD) | **Yes** | Check-in date |
| `check_out` | string (YYYY-MM-DD) | **Yes** | Check-out date |
| `coupon_code` | string | No | Coupon code to apply discount |

### Room Object Structure
```json
{
  "room_id": 1,      // Required: Room ID
  "quantity": 1      // Optional: Number of rooms (defaults to 1 if not specified)
}
```

### Important Notes
- **`villa_id` is always required**
- **For Villa property type**: `rooms` is not required (whole villa booking)
- **For Resort/Couple Stay property type**: `rooms` array is required (must have at least one room)
- If `quantity` is not specified in room object, it defaults to 1

## Response

### Success Response (200 OK)
```json
{
  "booking_type": "selected_rooms",
  "villa_id": 1,
  "villa_name": "Luxury Resort",
  "check_in": "2024-12-20",
  "check_out": "2024-12-25",
  "nights": 5,
  "price_summary": {
    "base_amount": 55000.00,
    "gst_percentage": 5.00,
    "gst_amount": 2750.00,
    "subtotal_before_coupon": 57750.00,
    "coupon_applied": true,
    "coupon_discount": 5775.00,
    "final_total": 51975.00,
    "average_price_per_night": 11000.00
  },
  "coupon_details": {
    "code": "DISCOUNT10",
    "title": "10% Off",
    "type": "percent",
    "discount_percentage": 10.00,
    "max_discount": null,
    "applied_discount": 5775.00
  },
  "breakdown": {
    "base_amount": 55000.00,
    "gst_amount": 2750.00,
    "subtotal": 57750.00,
    "discount": 5775.00,
    "total": 51975.00
  },
  "internal_calculation": {
    "commission": 5500.00,
    "commission_gst": 990.00,
    "tcs_amount": 275.00,
    "tds_amount": 55.00
  }
}
```

### Error Responses

#### 400 Bad Request - Missing Required Fields
```json
{
  "error": "check_in and check_out dates are required"
}
```

#### 400 Bad Request - Invalid Date Format
```json
{
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

#### 400 Bad Request - Invalid Coupon
```json
{
  "error": "Invalid or inactive coupon code"
}
```

#### 400 Bad Request - Coupon Minimum Purchase Not Met
```json
{
  "error": "Minimum purchase amount of ₹10000.00 required for this coupon",
  "minimum_purchase": 10000.00,
  "current_subtotal": 5775.00
}
```

#### 400 Bad Request - Coupon Expired
```json
{
  "error": "Coupon is not valid for current date",
  "coupon_valid_from": "2024-01-01T00:00:00Z",
  "coupon_valid_until": "2024-12-31T23:59:59Z"
}
```

#### 404 Not Found - Villa Not Found
```json
{
  "error": "Villa not found"
}
```

#### 400 Bad Request - Villa ID Required
```json
{
  "error": "villa_id is required"
}
```

#### 400 Bad Request - Rooms Required for Resort/Couple Stay
```json
{
  "error": "rooms array is required for Resort and Couple Stay properties"
}
```

#### 400 Bad Request - Invalid Property Type
```json
{
  "error": "Invalid property type. Must be Villa, Resort, or Couple Stay"
}
```

#### 404 Not Found - Room Not Found
```json
{
  "error": "Room with id 5 not found or does not belong to this villa"
}
```

## Features

### 1. Weekend Pricing
- Automatically applies weekend percentage increase on **Friday, Saturday, and Sunday**
- Weekend pricing is configured per villa in the admin panel
- Example: If base price is ₹5000 and weekend percentage is 25%, weekend price = ₹6250

### 2. Date-Specific Pricing
- If date-specific pricing is set for a villa or room, it takes priority
- Weekend pricing is applied on top of date-specific pricing

### 3. Multiple Rooms Support
- Book multiple rooms in a single request
- Each room can have different quantities
- Example: 2 Deluxe Rooms + 1 Suite Room

### 4. Coupon Validation
- Validates coupon code exists and is active
- Checks coupon validity dates
- Validates minimum purchase amount
- Supports both percentage and fixed amount discounts
- Applies maximum discount limit if configured

### 5. Price Breakdown
- **Base Amount**: Total before taxes and discounts (weekend pricing automatically applied per day)
- **GST**: Calculated based on average price per night (5% if < ₹7500, 12% if >= ₹7500)
- **Subtotal**: Base + GST
- **Coupon Discount**: Applied discount amount
- **Final Total**: Amount to be paid by customer

## Examples

### Example 1: Villa Property (Whole Villa Booking)
```bash
curl -X POST http://your-domain.com/customer/calculate-price-with-coupon/ \
  -H "Content-Type: application/json" \
  -d '{
    "villa_id": 1,
    "check_in": "2024-12-20",
    "check_out": "2024-12-25"
  }'
```

### Example 2: Resort/Couple Stay with Multiple Rooms
```bash
curl -X POST http://your-domain.com/customer/calculate-price-with-coupon/ \
  -H "Content-Type: application/json" \
  -d '{
    "villa_id": 3,
    "check_in": "2026-01-08",
    "check_out": "2026-01-25",
    "rooms": [
      {"room_id": 1},
      {"room_id": 2}
    ],
    "coupon_code": "DISCOUNT10"
  }'
```

### Example 3: Resort/Couple Stay with Quantities
```bash
curl -X POST http://your-domain.com/customer/calculate-price-with-coupon/ \
  -H "Content-Type: application/json" \
  -d '{
    "villa_id": 3,
    "check_in": "2026-01-08",
    "check_out": "2026-01-25",
    "rooms": [
      {"room_id": 1, "quantity": 2},
      {"room_id": 2, "quantity": 1}
    ]
  }'
```

## Price Calculation Logic

1. **Daily Price Calculation** (calculated internally, not returned):
   - For each day in the booking period:
     - Check for date-specific pricing (VillaPricing or RoomPricing)
     - If no date-specific pricing, use base price
     - If date is weekend (Fri/Sat/Sun) and weekend_percentage is set:
       - Apply weekend multiplier: `price = base_price * (1 + weekend_percentage / 100)`

2. **Base Amount**:
   - Sum of all daily prices (weekend pricing automatically included)

3. **GST Calculation**:
   - Average price per night = base_amount / nights
   - If average < ₹7500: GST = 5%
   - If average >= ₹7500: GST = 12%
   - GST amount = base_amount * gst_percentage

4. **Coupon Application**:
   - Subtotal = base_amount + gst_amount
   - If coupon type is "percent":
     - Discount = subtotal * (discount_percentage / 100)
     - If max_discount is set: discount = min(discount, max_discount)
   - If coupon type is "amount":
     - Discount = discount_amount
   - Final total = subtotal - discount

## Notes

- Weekend pricing is applied per day, so a booking spanning weekdays and weekends will have different prices for each day
- Coupon discount is applied to the subtotal (base + GST), not just the base amount
- The API does not create a booking, it only calculates the price
- Use this API before creating the actual booking to show the customer the final price
- All amounts are in INR (₹)

## Integration

After getting the price calculation, you can:
1. Display the price breakdown to the user
2. Show coupon discount if applied
3. Use the `final_total` for payment processing
4. Create the actual booking using the booking creation API with the calculated amounts

