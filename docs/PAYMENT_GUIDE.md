# Payment Guide – Razorpay Integration

This document describes how to complete **online payment** for villa/resort/couple-stay bookings using **Razorpay**. It covers all payment-related APIs, request/response formats, and frontend integration.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Payment Flow Summary](#2-payment-flow-summary)
3. [APIs Used for Payment](#3-apis-used-for-payment)
4. [Step 1: Create Booking (Get Razorpay Order)](#4-step-1-create-booking-get-razorpay-order)
5. [Step 2: Open Razorpay Checkout (Frontend)](#5-step-2-open-razorpay-checkout-frontend)
6. [Step 3: Verify Payment (Backend)](#6-step-3-verify-payment-backend)
7. [Webhook (Server-to-Server)](#7-webhook-server-to-server)
8. [Payment Status Values](#8-payment-status-values)
9. [Environment Variables](#9-environment-variables)
10. [Error Handling](#10-error-handling)
11. [Quick Reference](#11-quick-reference)

---

## 1. Overview

- **Payment gateway:** Razorpay  
- **Currency:** INR  
- **Flow:** Create booking → Razorpay order created → User pays on Razorpay Checkout → Verify payment on your backend → (Optional) Webhook updates status  
- **Authentication:** All payment APIs (except webhook) require **Bearer token** in `Authorization` header.

---

## 2. Payment Flow Summary

```
┌─────────────┐     POST /bookings/      ┌─────────────┐     Razorpay Order     ┌─────────────┐
│   Frontend  │ ───────────────────────► │   Backend   │ ────────────────────► │  Razorpay   │
│             │   (booking details)      │             │   (order created)     │             │
└─────────────┘                          └─────────────┘                        └─────────────┘
       │                                        │                                      │
       │  ◄── order_id, razorpay_key_id         │                                      │
       │                                        │                                      │
       │     Open Checkout (key, order_id)       │                                      │
       │ ─────────────────────────────────────►│                                      │
       │                                        │         User pays                    │
       │  ◄── razorpay_payment_id, signature ───│◄─────────────────────────────────────│
       │                                        │                                      │
       │     POST /bookings/verify-payment/      │                                      │
       │ ─────────────────────────────────────► │   (verify signature, mark paid)     │
       │  ◄── success, booking                  │                                      │
       │                                        │  ◄──── Webhook (payment.captured)   │
```

---

## 3. APIs Used for Payment

| Purpose              | Method | Endpoint                                                    | Auth   |
|----------------------|--------|-------------------------------------------------------------|--------|
| Create booking + order | POST   | `/customer/villa-resort-and-couple-stay/bookings/`          | Yes    |
| Verify payment       | POST   | `/customer/villa-resort-and-couple-stay/bookings/verify-payment/` | Yes    |
| Webhook (Razorpay → you) | POST | `/customer/booking/webhook/`                                | No (signature) |
| List bookings        | GET    | `/customer/villa-resort-and-couple-stay/bookings/`          | Yes    |
| Get booking details  | GET    | `/customer/villa-resort-and-couple-stay/bookings/<id>/`     | Yes    |

**Base URL examples:**  
- Production: `https://admin.villaguru.in`  
- Local: `http://127.0.0.1:8000`  
- Ngrok: `https://your-subdomain.ngrok-free.dev`

---

## 4. Step 1: Create Booking (Get Razorpay Order)

Creating a booking also creates a **Razorpay order** and returns the data needed to open the payment UI.

### Endpoint

```
POST /customer/villa-resort-and-couple-stay/bookings/
```

### Headers

- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

### Request Body (example – whole villa)

```json
{
  "villa": 1,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 4,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "john.doe@example.com",
  "special_request": "Late check-in",
  "payment_type": "online"
}
```

### Request Body (example – resort/couple stay with rooms)

```json
{
  "villa": 2,
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  "guest_count": 2,
  "child_count": 0,
  "is_for_self": true,
  "first_name": "Jane",
  "last_name": "Doe",
  "phone_number": "+919876543210",
  "email": "jane.doe@example.com",
  "payment_type": "online",
  "rooms": [
    { "room_id": 5, "quantity": 1 },
    { "room_id": 6, "quantity": 1 }
  ]
}
```

### Important fields for payment

- `payment_type`: Use `"online"` for Razorpay. Use `"cash"` for pay-at-property (no Razorpay).
- All other booking fields (villa, dates, guests, contact, rooms for resort/couple stay) are as per the main booking API.

### Response (201 Created) – payment-related fields

```json
{
  "id": 42,
  "booking_id": "RS-BK0042",
  "order_id": "order_xxxxxxxxxxxx",
  "total_amount": "15000.00",
  "payment_status": "pending",
  "payment_type": "online",
  "razorpay_key_id": "rzp_live_xxxxxxxxxxxx",
  "currency": "INR",
  "villa_details": { ... },
  "check_in": "2026-02-01",
  "check_out": "2026-02-05",
  ...
}
```

### What to store for payment

- `id` – booking ID (needed for verify-payment).
- `order_id` – Razorpay order ID (use in Checkout).
- `razorpay_key_id` – Razorpay key (use in Checkout).
- `currency` – `"INR"`.
- `total_amount` – for display only; amount is already in the order.

### cURL example

```bash
curl -X POST 'https://admin.villaguru.in/customer/villa-resort-and-couple-stay/bookings/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "villa": 1,
    "check_in": "2026-02-01",
    "check_out": "2026-02-05",
    "guest_count": 4,
    "child_count": 0,
    "is_for_self": true,
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+919876543210",
    "email": "john.doe@example.com",
    "payment_type": "online"
  }'
```

---

## 5. Step 2: Open Razorpay Checkout (Frontend)

After you get the create-booking response:

1. Load Razorpay Checkout script (or use npm package).
2. Open Checkout with `key` and `order_id` from the response.
3. On success, you get `razorpay_payment_id` and `razorpay_signature` (and `razorpay_order_id`); send these to your verify-payment API.

### Script tag (browser)

```html
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
```

### JavaScript example

```javascript
const options = {
  key: response.razorpay_key_id,        // from create booking response
  amount: response.total_amount * 100,  // already in order; optional for display
  currency: response.currency,          // INR
  order_id: response.order_id,          // from create booking response
  name: "Villa Guru",
  description: "Booking " + response.booking_id,
  prefill: {
    name: response.first_name + " " + response.last_name,
    email: response.email,
    contact: response.phone_number,
  },
  handler: function (res) {
    // res.razorpay_payment_id
    // res.razorpay_order_id
    // res.razorpay_signature
    // Call your verify-payment API with these + booking id
    verifyPayment(response.id, res.razorpay_order_id, res.razorpay_payment_id, res.razorpay_signature);
  },
  modal: {
    ondismiss: function () {
      // User closed checkout without paying
    },
  },
};

const rzp = new Razorpay(options);
rzp.open();
```

### React example (using razorpay package)

```javascript
import Razorpay from "razorpay";

const handlePay = () => {
  const options = {
    key: bookingResponse.razorpay_key_id,
    amount: Number(bookingResponse.total_amount) * 100,
    currency: bookingResponse.currency,
    order_id: bookingResponse.order_id,
    name: "Villa Guru",
    handler: (res) => {
      verifyPayment({
        booking_id: bookingResponse.id,
        razorpay_order_id: res.razorpay_order_id,
        razorpay_payment_id: res.razorpay_payment_id,
        razorpay_signature: res.razorpay_signature,
      });
    },
  };
  const rzp = new window.Razorpay(options);
  rzp.open();
};
```

---

## 6. Step 3: Verify Payment (Backend)

After the user pays successfully in Razorpay Checkout, call the verify-payment API with the IDs and signature from the `handler`. This marks the booking as paid on your server (and creates/updates a payment transaction).

### Endpoint

```
POST /customer/villa-resort-and-couple-stay/bookings/verify-payment/
```

### Headers

- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

### Request Body

```json
{
  "booking_id": 42,
  "razorpay_order_id": "order_xxxxxxxxxxxx",
  "razorpay_payment_id": "pay_xxxxxxxxxxxx",
  "razorpay_signature": "xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

| Field                 | Type   | Required | Description                          |
|-----------------------|--------|----------|--------------------------------------|
| `booking_id`         | number | Yes      | Booking ID from create response      |
| `razorpay_order_id`  | string | Yes      | From Razorpay success handler        |
| `razorpay_payment_id`| string | Yes      | From Razorpay success handler        |
| `razorpay_signature` | string | Yes      | From Razorpay success handler        |

### Response (200 OK) – success

```json
{
  "success": true,
  "message": "Payment verified.",
  "booking": {
    "id": 42,
    "booking_id": "RS-BK0042",
    "payment_status": "paid",
    "payment_type": "online",
    "order_id": "order_xxxxxxxxxxxx",
    "total_amount": "15000.00",
    ...
  }
}
```

### Error responses

- **400** – Missing parameters or invalid signature:
  - `{ "success": false, "error": "booking_id, razorpay_order_id, razorpay_payment_id and razorpay_signature are required." }`
  - `{ "success": false, "error": "Invalid payment signature." }`
- **404** – Booking not found or not owned by user:
  - `{ "success": false, "error": "Booking not found or access denied." }`

### cURL example

```bash
curl -X POST 'https://admin.villaguru.in/customer/villa-resort-and-couple-stay/bookings/verify-payment/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "booking_id": 42,
    "razorpay_order_id": "order_xxxxxxxxxxxx",
    "razorpay_payment_id": "pay_xxxxxxxxxxxx",
    "razorpay_signature": "xxxxxxxxxxxxxxxxxxxxxxxx"
  }'
```

---

## 7. Webhook (Server-to-Server)

Razorpay sends payment events to your webhook URL. The backend verifies the signature and updates the booking and payment transaction. You do not call this URL from your app; only Razorpay does.

### Webhook URL

```
POST /customer/booking/webhook/
```

Full URL examples:

- Production: `https://admin.villaguru.in/customer/booking/webhook/`
- Ngrok: `https://your-subdomain.ngrok-free.dev/customer/booking/webhook/`

### Headers (from Razorpay)

- `X-Razorpay-Signature` – HMAC signature of the body using your webhook secret.

### Events handled

- `payment.captured` → booking `payment_status` = `paid`
- `payment.authorized` → `pending`
- `payment.failed` → `failed`
- `payment.refunded` → `refunded`

### Setup in Razorpay Dashboard

1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com/).
2. Go to **Settings** → **Webhooks** (or **Developers** → **Webhooks**).
3. Add webhook URL: `https://your-domain.com/customer/booking/webhook/`
4. Select events: `payment.captured`, `payment.authorized`, `payment.failed`, `payment.refunded`.
5. Copy the **Webhook Secret** and set it in your app as `RAZORPAY_WEBHOOK_SECRET`.

### Backend behaviour

- Verifies `X-Razorpay-Signature` using `RAZORPAY_WEBHOOK_SECRET`.
- Reads `booking_id` from `payload.payment.entity.notes.booking_id`.
- Updates `VillaBooking` (payment_status, payment_id, order_id, payment_type, paid_at) and creates/updates `PaymentTransaction`.

---

## 8. Payment Status Values

| Status    | Meaning                                      |
|-----------|----------------------------------------------|
| `pending` | Order created; payment not completed         |
| `paid`    | Payment successful (captured)                |
| `failed`  | Payment failed                                |
| `refunded`| Payment was refunded                         |

Booking response fields related to payment:

- `payment_status` – one of the above.
- `payment_type` – `"online"` (Razorpay) or `"cash"`.
- `order_id` – Razorpay order ID (set after create).
- `payment_id` – Razorpay payment ID (set after verify or webhook).
- `paid_at` – datetime when payment was marked paid (if applicable).

---

## 9. Environment Variables

Configure these in your backend (e.g. `.env` or server environment):

| Variable                 | Description                    | Example (masked)        |
|--------------------------|--------------------------------|-------------------------|
| `RAZORPAY_KEY_ID`        | Razorpay API key (public)     | `rzp_live_xxxx`         |
| `RAZORPAY_KEY_SECRET`    | Razorpay API secret           | `xxxxxxxxxxxxxxxx`      |
| `RAZORPAY_WEBHOOK_SECRET`| Webhook signing secret        | From Dashboard → Webhooks |

- **Key ID** is sent to the frontend (in create-booking response); **Key Secret** and **Webhook Secret** must stay server-side only.

---

## 10. Error Handling

### Create booking

- **400** – Validation errors (e.g. dates, villa, rooms). Response body contains field-wise errors.
- **401** – Missing or invalid token.
- **201** – Success; use `order_id` and `razorpay_key_id` from response for Checkout.

### Verify payment

- **400** – Missing parameters or signature verification failed. Do not mark the booking as paid in your UI.
- **404** – Booking not found or not owned by the user.
- **200** – Success; show success screen and use `booking` in response to show updated `payment_status: "paid"`.

### Webhook

- **400** – Invalid signature or missing booking_id; Razorpay may retry.
- **500** – Server error; Razorpay may retry. Check logs and fix before next delivery.

---

## 11. Quick Reference

### Payment-related APIs

| What              | Method | URL                                                                 |
|-------------------|--------|---------------------------------------------------------------------|
| Create booking    | POST   | `/customer/villa-resort-and-couple-stay/bookings/`                  |
| Verify payment    | POST   | `/customer/villa-resort-and-couple-stay/bookings/verify-payment/`   |
| Webhook           | POST   | `/customer/booking/webhook/`                                        |
| List my bookings  | GET    | `/customer/villa-resort-and-couple-stay/bookings/`                  |
| Get one booking   | GET    | `/customer/villa-resort-and-couple-stay/bookings/<id>/`             |

### Create booking → payment flow (short)

1. `POST .../bookings/` with booking details and `"payment_type": "online"`.
2. From response take: `id`, `order_id`, `razorpay_key_id`, `currency`.
3. Open Razorpay Checkout with `key = razorpay_key_id`, `order_id = order_id`.
4. In success handler get: `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.
5. `POST .../bookings/verify-payment/` with `booking_id`, `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.
6. On 200, show success and use `booking.payment_status === "paid"` for confirmation.

### Razorpay docs

- [Razorpay Checkout integration](https://razorpay.com/docs/payments/payment-gateway/web-integration/standard/)
- [Webhooks](https://razorpay.com/docs/webhooks/)

---

*Last updated for Villa Guru booking and Razorpay integration.*
