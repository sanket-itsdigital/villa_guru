# Villa Guru Documentation

Welcome to the Villa Guru API documentation. This folder contains all the documentation for the Villa Guru project.

---

## 📚 Documentation Index

### 1. [API Documentation](./API_DOCUMENTATION.md)
**Complete API Reference Guide**

The main API documentation covering all endpoints including:
- Authentication APIs
- User Management APIs
- Villa/Resort/Couple Stay APIs
- Booking APIs
- Support Ticket APIs
- Master Data APIs

**Use this for:** Complete API reference, endpoint details, request/response examples

---

### 2. [Room Booking Guide](./ROOM_BOOKING_GUIDE.md)
**Step-by-Step Room Booking Guide**

Comprehensive guide explaining:
- How to book rooms in Resort and Couple Stay properties
- Understanding room types vs rooms
- Booking multiple rooms of the same type
- Complete booking flow with examples
- Error handling
- Frontend implementation tips

**Use this for:** Understanding the booking process, implementing booking functionality

---

### 3. [Room Booking API Guide](./ROOM_BOOKING_API_GUIDE.md)
**Room Booking API Reference**

Detailed API documentation for:
- Getting available rooms
- Booking rooms
- Room availability checking
- Date-based filtering

**Use this for:** Room booking API endpoints, request/response formats

---

### 4. [Property Room Types API](./PROPERTY_ROOM_TYPES_API.md)
**Property Room Types API Documentation**

Complete documentation for the room types API:
- Getting room types for a property
- Room type details with amenities
- Room type images
- Property type filtering

**Use this for:** Room type API endpoint, understanding room type structure

---

### 5. [Booking API Guide](./BOOKING_API_GUIDE.md)
**General Booking API Reference**

Documentation for booking APIs:
- Creating bookings
- Booking types (whole villa vs selected rooms)
- Booking status management
- Payment integration

**Use this for:** General booking API endpoints

---

### 6. [Price Calculation API](./PRICE_CALCULATION_API.md)
**Price Calculation Documentation**

Guide for price calculation:
- Price calculation logic
- Markup and profit margins
- Coupon/discount application
- Price recalculation

**Use this for:** Understanding pricing, implementing price calculations

---

### 7. [Production Migration Fix](./FIX_PRODUCTION_MIGRATION.md)
**Migration Troubleshooting Guide**

Documentation for fixing production migration issues:
- Common migration errors
- Data migration fixes
- Rollback procedures

**Use this for:** Troubleshooting migration issues in production

---

## 🚀 Quick Start

### For API Integration:
1. Start with [API Documentation](./API_DOCUMENTATION.md) for complete endpoint reference
2. Check [Room Booking Guide](./ROOM_BOOKING_GUIDE.md) for booking implementation
3. Refer to [Property Room Types API](./PROPERTY_ROOM_TYPES_API.md) for room type details

### For Frontend Development:
1. Read [Room Booking Guide](./ROOM_BOOKING_GUIDE.md) for booking flow
2. Use [Room Booking API Guide](./ROOM_BOOKING_API_GUIDE.md) for API calls
3. Check [API Documentation](./API_DOCUMENTATION.md) for other endpoints

### For Backend Development:
1. Review [API Documentation](./API_DOCUMENTATION.md) for endpoint structure
2. Check [Price Calculation API](./PRICE_CALCULATION_API.md) for pricing logic
3. Refer to [Production Migration Fix](./FIX_PRODUCTION_MIGRATION.md) if needed

---

## 📋 API Endpoints Summary

### Authentication
- `POST /users/signup/` - User registration
- `POST /users/login/` - User login
- `POST /users/logout/` - User logout
- `POST /users/forgot-password/` - Password reset

### Properties
- `GET /customer/villas/` - List all properties
- `GET /customer/villas/{id}/` - Get property details
- `GET /customer/available-villa-resort-and-couple-stay/` - Get available properties

### Room Types
- `GET /customer/property-room-types/?property_id={id}` - Get room types for a property

### Rooms
- `GET /customer/available-rooms/` - Get available rooms
- `GET /customer/resort-and-couple-stay/{id}/rooms/` - List rooms for a property
- `GET /customer/room/{id}/` - Get room details

### Bookings
- `POST /customer/villa-resort-and-couple-stay/bookings/` - Create booking
- `GET /customer/villa-resort-and-couple-stay/bookings/` - List bookings
- `GET /customer/villa-resort-and-couple-stay/bookings/{id}/` - Get booking details

---

## 🔗 Base URLs

- **Development:** `http://127.0.0.1:8002`
- **Production:** `https://villaguru.pythonanywhere.com`

---

## 📝 Notes

- All API endpoints require JWT Bearer Token authentication (except public endpoints)
- Date formats: Use `YYYY-MM-DD` (e.g., `2026-04-08`)
- All prices are in decimal format with 2 decimal places
- Timezone: Asia/Kolkata (IST)

---

## 🤝 Support

For issues or questions:
1. Check the relevant documentation file
2. Review API error responses
3. Check the [Production Migration Fix](./FIX_PRODUCTION_MIGRATION.md) for common issues

---

**Last Updated:** January 2026
