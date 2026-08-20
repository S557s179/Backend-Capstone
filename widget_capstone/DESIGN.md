# FlyRank Capstone Widget — Design Document

## 1. Overview

This project is an embeddable widget and lead-capture platform.

A customer can create a widget through an authenticated API and receive a single `<script>` tag that can be placed on another website. Visitors can interact with the widget and submit information.

The backend will validate and protect incoming submissions, enrich them with location data, store them, and expose the submissions through authenticated dashboard endpoints.

The system is designed to safely handle requests coming from websites that the backend does not control.

## 2. Technology Stack

* Python
* FastAPI
* PostgreSQL
* Docker
* SQLAlchemy
* JWT authentication
* HTML/CSS/JavaScript for the customer test page

## 3. Core Data Model

### User

Represents a widget owner.

Fields:

* `id`
* `email`
* `password_hash`
* `created_at`

### Widget

Represents an embeddable widget owned by a user.

Fields:

* `id`
* `owner_id`
* `name`
* `type`
* `title`
* `description`
* `button_text`
* `form_fields`
* `display_options`
* `created_at`
* `updated_at`

The `owner_id` associates every widget with its owner.

### Submission

Represents information submitted by a visitor through a widget.

Fields:

* `id`
* `widget_id`
* `owner_id`
* `data`
* `ip_address`
* `country`
* `city`
* `created_at`

Submissions are associated with both the widget and its owner so that tenant isolation can be enforced.

## 4. Tenant Isolation

Every authenticated widget-management and dashboard query will be restricted to the authenticated user's `owner_id`.

A user must never be able to read, modify, or delete another user's widgets or submissions.

Tenant isolation will be enforced by the backend rather than relying on the frontend.

## 5. Request Paths

The system has three major request paths.

### Path 1 — Widget Owner

The authenticated owner manages their widgets.

```text
POST   /api/widgets
GET    /api/widgets
GET    /api/widgets/{id}
PUT    /api/widgets/{id}
DELETE /api/widgets/{id}
```

These endpoints require authentication.

### Path 2 — Customer Website

A website loads the widget and its configuration.

```text
GET /widget.js?id={widget_id}
GET /api/widgets/{id}/config
```

These endpoints are public.

The configuration endpoint will use HTTP cache headers, and the widget JavaScript will be versioned or cache-busted.

### Path 3 — Website Visitor

A visitor submits the widget.

```text
POST /api/submissions
```

This endpoint is public and must support cross-origin requests.

The request processing pipeline is:

```text
Request
   ↓
Input validation
   ↓
CORS
   ↓
Rate limiting
   ↓
Spam protection
   ↓
Geo enrichment
   ↓
Store submission
   ↓
Email/webhook side effect
```

Failure of geo enrichment or the secondary side effect must not cause the primary submission to fail.

## 6. Widget Embed Flow

The customer first creates a widget through the authenticated API.

The API returns a widget identifier and embed snippet.

Example:

```html
<script src="http://localhost:8000/widget.js?id=123"></script>
```

The customer places this script on a separate HTML page.

The flow is:

```text
Customer
   ↓
Create widget
   ↓
Receive script snippet
   ↓
Customer website loads widget.js
   ↓
widget.js requests widget configuration
   ↓
Configuration is returned
   ↓
Widget renders
   ↓
Visitor submits form
   ↓
Submission API processes request
   ↓
Submission stored
```

## 7. Submission Protection

The public submission endpoint will not trust client input.

It will implement:

* Request validation
* Payload size limits
* CORS handling
* Rate limiting per IP and/or widget
* A honeypot spam field
* Appropriate HTTP status codes
* JSON error responses

Invalid requests should return clean 4xx responses instead of causing server errors.

Rate-limited requests should return HTTP `429`.

## 8. Geo Enrichment

The submission pipeline will use an IP-to-location fallback chain.

```text
Provider A
    ↓ failure
Provider B
    ↓ failure
No geo data
```

If Provider A fails, Provider B will be attempted.

If both providers fail, the submission will still be stored successfully without location data.

Automated tests will use mocked providers so the fallback behavior is deterministic.

## 9. Safe Side Effects

After a submission has been stored, the system will perform a secondary notification action.

This can initially be represented by a local email catcher or a logged notification.

The important behavior is:

```text
Store submission
      ↓
Attempt notification
      ↓
Notification succeeds → continue
Notification fails    → submission remains successful
```

A failure in the secondary action must never prevent the primary submission from being stored.

## 10. Dashboard API

Authenticated widget owners will be able to retrieve their submissions and basic analytics.

The dashboard API will provide:

* Submission counts
* Submissions over time
* Per-widget statistics
* Geographic breakdowns

The frontend dashboard will remain minimal because the primary focus of this project is the backend.

## 11. Non-Goal

This project will not implement a full visual form builder or a production CDN.

The widget interface will remain intentionally simple, and the customer website will be represented by a separate local HTML page served from a different origin.

## 12. Architecture

```text
                    ┌─────────────────────┐
                    │    Widget Owner     │
                    └──────────┬──────────┘
                               │ JWT
                               ▼
                    ┌─────────────────────┐
                    │ Widget Management   │
                    │        API          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    PostgreSQL       │
                    └─────────────────────┘


┌─────────────────────┐
│ Customer Website    │
│  Different Origin   │
└──────────┬──────────┘
           │
           │ widget.js
           ▼
┌─────────────────────┐
│ Public Widget       │
│ Delivery API        │
└──────────┬──────────┘
           │
           │ configuration
           ▼
      Render Widget
           │
           │ visitor submits
           ▼
┌─────────────────────┐
│ Public Submission   │
│        API          │
└──────────┬──────────┘
           │
           ├── Validation
           ├── CORS
           ├── Rate Limiting
           ├── Spam Protection
           ├── Geo Provider A
           ├── Geo Provider B
           └── PostgreSQL
                    │
                    ▼
             Notification
             Side Effect
```

## 13. Initial Success Criteria

The first implementation will be considered successful when:

1. An authenticated user can create a widget.
2. A user can only access their own widgets.
3. A widget can generate an embed snippet.
4. A separate-origin HTML page can load the widget.
5. The widget can submit data to the API.
6. Invalid submissions are rejected.
7. Rate limiting can return `429`.
8. Spam submissions can be detected.
9. Geo provider fallback works.
10. A failed notification does not cause submission failure.
11. Submissions can be retrieved through the dashboard API.
12. Automated tests cover the required failure cases.

## 14. Development Approach

The project will be built incrementally.

The implementation order will be:

1. Project setup
2. Database and models
3. Authentication
4. Widget CRUD
5. Embed snippet
6. Widget configuration and JavaScript
7. Public submission endpoint
8. Validation and CORS
9. Rate limiting and spam protection
10. Geo enrichment and fallback
11. Notification side effect
12. Dashboard endpoints
13. Automated tests
14. Documentation and evidence
15. Final acceptance testing
