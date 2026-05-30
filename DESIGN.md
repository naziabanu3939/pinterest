# Design Document: Pinterest Life-Quotes Uploader

## 1. Overview

This document outlines the architecture and implementation strategy for a web application that enables users to create aesthetic quote images and post them to Pinterest programmatically.

**Goal**: Provide a safe, copyright-compliant tool for uploading life quotes with aesthetic pictures to Pinterest.

---

## 2. Architecture

### 2.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React/HTML)                   │
│  - Quote entry form                                         │
│  - Image upload/selection                                   │
│  - Preview canvas                                           │
│  - Schedule UI                                              │
│  - Board selection                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                  Backend (Flask/Python)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Auth Module (OAuth 2.0)                                │ │
│  │ - Authorization code flow                              │ │
│  │ - Token storage/refresh                                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Image Processor (Pillow)                               │ │
│  │ - Compose image + quote overlay                        │ │
│  │ - Apply filters/effects                                │ │
│  │ - Export for upload                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Copyright Checker                                      │ │
│  │ - Validate image sources (CC0, user-uploaded)         │ │
│  │ - Validate quote origins                              │ │
│  │ - Flag ambiguous content for review                   │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Scheduler (APScheduler / Celery)                       │ │
│  │ - Queue posts for later                                │ │
│  │ - Background job executor                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Pinterest API Client                                   │ │
│  │ - POST /v5/pins endpoint                               │ │
│  │ - Board management                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼──┐    ┌─────▼────┐   ┌─────▼────┐
    │ SQLite│    │ Pinterest│   │   Cloud  │
    │  (DB) │    │   API    │   │ Storage  │
    │       │    │          │   │ (Images) │
    └───────┘    └──────────┘   └──────────┘
```

### 2.2 Data Model

**User**
- id (PK)
- email
- encrypted_pinterest_token
- encrypted_pinterest_refresh_token
- created_at
- updated_at

**Quote**
- id (PK)
- user_id (FK)
- text
- author
- source (URL or 'user_input')
- license (CC0, public_domain, copyrighted, unknown)
- review_status (approved, pending_review, rejected)
- created_at

**Image**
- id (PK)
- user_id (FK)
- source_url or local_path
- license (CC0, permissive_stock, user_uploaded, unknown)
- review_status (approved, pending_review, rejected)
- created_at

**Post**
- id (PK)
- user_id (FK)
- quote_id (FK)
- image_id (FK)
- pin_id (from Pinterest)
- board_id (on Pinterest)
- status (draft, scheduled, posted, failed)
- scheduled_time
- posted_time
- created_at

---

## 3. Workflow

### 3.1 User Journey

1. **Authenticate**: User clicks "Login with Pinterest" → OAuth flow → store access token
2. **Create Post**:
   - Enter quote text + author
   - Upload or select image from permissive sources
   - System validates copyright/license
   - If flagged, user reviews and approves or cancels
3. **Preview**: Renders image with quote overlay
4. **Post**:
   - Immediately post to Pinterest, OR
   - Schedule for later
5. **Confirmation**: Pin URL + board link shown to user

### 3.2 Copyright Validation Flow

```
User submits quote + image
        │
        ▼
┌───────────────────┐
│ Quote Check       │
│ - Is it public    │
│ - domain? OR      │
│ - >= 70 yrs old?  │
└───────────────────┘
        │
        ├─ YES ──► APPROVED
        │
        ├─ UNKNOWN ──► FLAG FOR REVIEW
        │
        └─ NO ──► REJECT / ERROR
        
Image Validation (similar logic):
- User uploaded ──► APPROVED
- CC0/Pixabay/Pexels ──► APPROVED (with license check)
- Stock image (commercial use) ──► APPROVED (if license permits)
- Unknown source ──► FLAG FOR REVIEW
- Copyrighted (Getty, etc.) ──► REJECT
```

---

## 4. OAuth 2.0 Integration with Pinterest

### 4.1 Authorization Code Flow

1. **User clicks "Login with Pinterest"**
   - Redirect to: `https://api.pinterest.com/oauth/`
   - Params: client_id, redirect_uri, scope, state

2. **Pinterest redirects back** with authorization code
   - Exchange code for access_token + refresh_token

3. **Store tokens securely**
   - Encrypt at rest in database
   - Use environment keys for encryption

4. **Refresh flow**
   - When token expires, use refresh_token to get new access_token
   - Update database

### 4.2 Scopes Required

- `pins:read` — read user's pins
- `pins:write` — create pins
- `boards:read` — list user's boards

---

## 5. Image Processing

### 5.1 Compose Endpoint

Input:
```json
{
  "quote": "Life is what you make it.",
  "author": "Anonymous",
  "image_url": "https://...",  // or upload as file
  "bg_overlay": 0.3,           // transparency overlay
  "font_size": 48,
  "text_color": "#ffffff",
  "bg_color": "#000000"        // fallback if no image
}
```

Process:
1. Download/load image
2. Apply overlay (optional opacity layer)
3. Measure text, wrap to fit
4. Draw text centered
5. Return image (PNG/JPEG)

Output: Image file ready for Pinterest

---

## 6. Copyright & License Compliance

### 6.1 Approved Sources

**Images**:
- User-uploaded (explicit ownership claim)
- CC0 / Public Domain (Unsplash, Pexels, Pixabay)
- Stock images with commercial license (if user provides proof)

**Quotes**:
- Original text (user written)
- Public domain (> 70 years, varies by jurisdiction)
- Quotes with explicit reuse permission (Creative Commons, etc.)

### 6.2 Flagged & Rejected

- **Flagged**: Unknown source, ambiguous license → requires manual review
- **Rejected**: Known copyrighted material without permission

### 6.3 Audit Trail

Every post records:
- Quote source URL or "user_input"
- Quote license classification
- Image source URL or "user_uploaded"
- Image license
- User review status (approved / auto-approved)
- Timestamp

---

## 7. API Endpoints

### Authentication
- `POST /auth/login` — Start OAuth flow
- `GET /auth/callback` — OAuth redirect handler
- `POST /auth/logout` — Clear session

### Image Composition
- `POST /compose` — Create image with quote overlay

### Posts
- `GET /posts` — List user's posts
- `POST /posts` — Create draft post (validate quote/image)
- `POST /posts/:id/post` — Post to Pinterest immediately
- `POST /posts/:id/schedule` — Schedule for later
- `DELETE /posts/:id` — Delete draft

### Boards
- `GET /boards` — List user's Pinterest boards

### Admin/Review
- `GET /admin/flagged` — List flagged posts pending review
- `POST /admin/flagged/:id/approve` — Approve flagged post
- `POST /admin/flagged/:id/reject` — Reject flagged post

---

## 8. Security & Privacy

1. **Token Storage**: Encrypt access/refresh tokens using AES-256 at rest
2. **Session**: Use secure, HTTPOnly cookies for web sessions
3. **Rate Limiting**: 10 posts/hour per user
4. **Audit Logs**: Log all posts with user, timestamp, source data
5. **Data Deletion**: User can request data deletion (GDPR-ready)

---

## 9. Deployment

### 9.1 Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
export FLASK_ENV=development
flask run
```

### 9.2 Production

- Hosted on Heroku, AWS, or self-hosted
- Database: PostgreSQL
- Job queue: Celery + Redis (for scheduling)
- Storage: S3 (for generated images)
- Environment: .env with encrypted secrets

---

## 10. Testing Strategy

- Unit tests for image composition
- Unit tests for copyright checker
- Integration tests for Pinterest API calls (mocked)
- E2E tests for OAuth flow

---

## 11. Future Enhancements

- Batch upload (multiple quotes at once)
- Template library (pre-designed image + quote layouts)
- Analytics (impressions, saves, clicks per pin)
- AI quote generation (with source attribution)
- Cross-post to Instagram, Twitter
- Collaborate with other users on board

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-30
