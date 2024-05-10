# Canceled orders service

[![codecov](https://codecov.io/gh/goretsky-integration/canceled-orders/graph/badge.svg?token=XxdwQOzYXG)](https://codecov.io/gh/goretsky-integration/canceled-orders)
[![Test](https://github.com/goretsky-integration/canceled-orders/actions/workflows/test.yaml/badge.svg)](https://github.com/goretsky-integration/canceled-orders/actions/workflows/test.yaml)

---

## What is this service for?

This service is intended for identifying specific types of <u>canceled orders</u> for the previous day based on certain
criteria.

---

## Criteria for canceled orders:

- Criteria set #1:
    - Sales channel - restaurant
    - Order canceled by any employee.
- Criteria set #2:
    - Sales channel - delivery
    - A courier was assigned to the order.

---

## How to understand that the order was canceled by an employee?

In the order history, the third column will indicate the employee's name.
<img src="./assets/canceled-by-shift-manager.jpg" alt="order history">

---

## What data about the order is collected?

- Order ID.
- Point of sale name.
- Order number.
- Order price.
- Sales channel (restaurant, delivery).
- Existence of a cancellation receipt.
