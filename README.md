# CommunityBoard Backend (Django)

A small community discussion board API — users register/log in, post to categorized
boards, and comment on posts. This service was rewritten from FastAPI to **Django +
Django REST Framework**, keeping the exact same URL paths, JSON contract, JWT format,
and pagination envelope, so existing frontend clients require no changes.

## Contents

- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Database schema](#database-schema)
- [API reference](#api-reference)
- [Authentication](#authentication)
- [Pagination](#pagination)
- [Seeding data](#seeding-data)
- [Docker](#docker)
- [Notes on the FastAPI → Django migration](#notes-on-the-fastapi--django-migration)

## Tech stack

| Concern         | Choice                                             |
|-----------------|-----------------------------------------------------|
| Framework       | Django 5.2 (LTS)                                   |
| API layer       | Django REST Framework                              |
| Database        | PostgreSQL                                         |
| Auth            | Stateless JWT (PyJWT, HS256) via a custom DRF `Authentication` class |
| Password hashing| bcrypt via `passlib` (compatible with the original Spring/FastAPI hashes) |
| CORS            | `django-cors-headers`                              |
| WSGI server     | gunicorn (production / Docker)                     |

## Project structure

```
backend-python/
├── communityboard/        # Project config
│   ├── settings.py
│   ├── urls.py             # All routes are declared here
│   ├── wsgi.py / asgi.py
├── accounts/               # Custom User model, JWT issuing/verification, register & login
│   ├── models.py           # User (AbstractBaseUser), Role choices
│   ├── managers.py         # UserManager (create_user / create_superuser)
│   ├── jwt_auth.py         # generate_token / decode_token
│   ├── authentication.py   # DRF JWTAuthentication class
│   ├── serializers.py
│   ├── views.py            # RegisterView, LoginView
│   └── fixtures/seed_data.json
├── categories/             # Category model + read-only list endpoint
├── posts/                  # Post model, CRUD endpoints, pagination
│   └── pagination.py       # Spring-style Page<T> envelope
├── comments/               # Comment model, list-by-post endpoint
├── manage.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

Each Django app follows the same shape: `models.py` (schema), `serializers.py`
(request/response shape), `views.py` (endpoint logic), `migrations/` (schema
history), and — where seed data applies — `fixtures/seed_data.json`.

## Getting started

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ running locally (or reachable via `DATABASE_URL`)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then edit values as needed

# Create the database (adjust to your local Postgres setup)
createdb communityboard

python manage.py migrate
python manage.py loaddata seed_data   # optional: seed categories/users/posts
python manage.py runserver 8080
```

The API is now available at `http://localhost:8080/api/...`.

### Creating an admin user manually (alternative to the fixture)

```bash
python manage.py createsuperuser
# prompts for: email, name, password
```

This sets `role=ADMIN` on the created user (see `accounts/managers.py`).

## Environment variables

| Variable               | Default                                                    | Purpose |
|-------------------------|-------------------------------------------------------------|---------|
| `DJANGO_SECRET_KEY`     | dev-only insecure key                                       | Django's cryptographic signing key. Set a real secret in production. |
| `DJANGO_DEBUG`          | `true`                                                      | Django debug mode. Set `false` in production. |
| `DJANGO_ALLOWED_HOSTS`  | `*`                                                          | Comma-separated allowed `Host` headers. |
| `DATABASE_URL`          | `postgresql://postgres:postgres@localhost:5432/communityboard` | PostgreSQL connection string. |
| `JWT_SECRET`            | `communityboard-secret-key-amalitech-2024`                   | HS256 signing secret for auth tokens. **Must match** if migrating in place with tokens already issued. |
| `JWT_EXPIRATION_MS`     | `86400000` (24h)                                            | Token lifetime, in milliseconds (kept in ms to match the original config). |
| `CORS_ALLOWED_ORIGINS`  | unset → allow all origins                                    | Comma-separated allow-list. Leave unset in dev to mirror the original app's permissive CORS policy. |

See `.env.example` for a ready-to-copy template.

## Database schema

PostgreSQL, 4 tables, all managed by Django migrations (`*/migrations/0001_initial.py`).
Equivalent raw SQL:

```sql
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       VARCHAR(254) NOT NULL UNIQUE,
    name        VARCHAR(255) NOT NULL,
    password    VARCHAR(128) NOT NULL,             -- bcrypt hash
    role        VARCHAR(10)  NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    last_login  TIMESTAMPTZ
    -- unique constraint on `email` doubles as its lookup index
);

CREATE TABLE categories (
    id           BIGSERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(255)
    -- unique constraint on `name` doubles as its lookup index
);

CREATE TABLE posts (
    id           BIGSERIAL PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    content      TEXT NOT NULL,
    category_id  BIGINT REFERENCES categories(id) ON DELETE SET NULL,
    author_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Feed query: "all posts, newest first" (default list + pagination)
CREATE INDEX posts_created_at_idx        ON posts (created_at DESC);
-- "posts in category X, newest first" — also covers plain category_id lookups
CREATE INDEX posts_category_created_idx  ON posts (category_id, created_at DESC);
-- "posts by author X, newest first" — also covers plain author_id lookups
CREATE INDEX posts_author_created_idx    ON posts (author_id, created_at DESC);

CREATE TABLE comments (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    post_id     BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id   BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- "comments for post X, oldest first" and per-post comment counts
CREATE INDEX comments_post_created_idx ON comments (post_id, created_at);
-- comments.author_id keeps Django's default single-column FK index
```

### Relations

```mermaid
erDiagram
    USERS ||--o{ POSTS : authors
    USERS ||--o{ COMMENTS : authors
    CATEGORIES |o--o{ POSTS : categorizes
    POSTS ||--o{ COMMENTS : has

    USERS {
        bigint id PK
        varchar email UK
        varchar name
        varchar password
        varchar role
        timestamptz created_at
    }
    CATEGORIES {
        bigint id PK
        varchar name UK
        varchar description
    }
    POSTS {
        bigint id PK
        varchar title
        text content
        bigint category_id FK
        bigint author_id FK
        timestamptz created_at
        timestamptz updated_at
    }
    COMMENTS {
        bigint id PK
        text content
        bigint post_id FK
        bigint author_id FK
        timestamptz created_at
    }
```

### Design notes

- **`posts.category_id` is nullable with `ON DELETE SET NULL`**: deleting a category
  un-categorizes its posts instead of deleting them.
- **`posts.author_id` / `comments.author_id`/`post_id` are `ON DELETE CASCADE`**:
  deleting a user or post cleans up their dependent posts/comments.
- **Composite indexes lead with the foreign key column** (`category_id, created_at`
  / `author_id, created_at` / `post_id, created_at`), so they satisfy both the
  filtered+sorted queries the API actually runs *and* plain foreign-key lookups,
  without a redundant duplicate single-column index alongside them.
- **`users.email` and `categories.name` are `UNIQUE`**, which Postgres backs with
  a unique index automatically — no separate index is declared for those.

## API reference

Base path: `/api`. No trailing slashes (matches the original Spring/FastAPI routes).

| Method | Path                          | Auth        | Description |
|--------|-------------------------------|-------------|-------------|
| POST   | `/auth/register`               | —           | Create an account, returns a JWT |
| POST   | `/auth/login`                  | —           | Exchange credentials for a JWT |
| GET    | `/categories`                  | —           | List all categories |
| GET    | `/posts?page=0&size=10`        | —           | Paginated post feed, newest first |
| POST   | `/posts`                       | Bearer JWT  | Create a post |
| GET    | `/posts/{id}`                  | —           | Get a single post |
| PUT    | `/posts/{id}`                  | Bearer JWT  | Update a post (author only) |
| DELETE | `/posts/{id}`                  | Bearer JWT  | Delete a post (author or `ADMIN`) |
| GET    | `/posts/{id}/comments`         | —           | List a post's comments, oldest first |

### Example: register

```http
POST /api/auth/register
Content-Type: application/json

{ "name": "Ada Lovelace", "email": "ada@example.com", "password": "hunter22" }
```

```json
{ "token": "<jwt>", "email": "ada@example.com", "name": "Ada Lovelace", "role": "USER" }
```

### Example: create a post

```http
POST /api/posts
Authorization: Bearer <jwt>
Content-Type: application/json

{ "title": "Hello", "content": "First post!", "categoryId": 1 }
```

```json
{
  "id": 5,
  "title": "Hello",
  "content": "First post!",
  "categoryName": "General",
  "categoryId": 1,
  "authorName": "Ada Lovelace",
  "authorEmail": "ada@example.com",
  "createdAt": "2026-09-13T10:00:00Z",
  "updatedAt": "2026-09-13T10:00:00Z",
  "commentCount": 0
}
```

Not yet implemented (kept as `# TODO` in the source, matching the original app's
scope): admin category CRUD, creating/deleting comments, and post search.

## Authentication

Tokens are plain HS256 JWTs, issued and verified the same way the original
Spring/FastAPI service did:

- Claims: `sub` (email), `role`, `iat`, `exp`.
- Verified by `accounts/authentication.py`'s `JWTAuthentication`, a DRF
  `Authentication` class that reads the `Authorization: Bearer <token>` header,
  decodes it with `JWT_SECRET`, and looks the user up by the `sub` email claim.
- A missing/invalid/expired token resolves to `AnonymousUser` rather than raising —
  endpoints that require a user set `permission_classes = [IsAuthenticated]`, which
  then produces the `401`.
- Post update is restricted to the post's author; delete is restricted to the
  author or a user with `role="ADMIN"` — enforced in `posts/views.py`, returning
  `403` via DRF's `PermissionDenied`.

Passwords are hashed with bcrypt via `passlib`, matching the original hashing
scheme exactly, so pre-existing password hashes (e.g. from the seed data) verify
correctly without any migration step.

## Pagination

`GET /api/posts` mirrors the original Spring Data `Page<T>` JSON shape exactly
(zero-indexed `page`, default `size=10`):

```json
{
  "content": [ /* PostResponse objects */ ],
  "pageable": { "pageNumber": 0, "pageSize": 10, "offset": 0, "sort": { "...": "..." }, "paged": true, "unpaged": false },
  "totalElements": 42,
  "totalPages": 5,
  "size": 10,
  "number": 0,
  "sort": { "...": "..." },
  "first": true,
  "last": false,
  "numberOfElements": 10,
  "empty": false
}
```

See `posts/pagination.py`.

## Seeding data

Sample categories, two users (`admin@amalitech.com` / `user@amalitech.com`, both
with password `password123`), and two starter posts are provided as Django
fixtures (one per app, all named `seed_data.json`):

```bash
python manage.py loaddata seed_data
```

`loaddata` runs inside a single transaction with foreign-key checks deferred
until commit, so load order across the `accounts` / `categories` / `posts`
fixtures doesn't matter.

## Docker

```bash
docker build -t communityboard-backend .
docker run --env-file .env -p 8080:8080 communityboard-backend
```

The container runs `migrate` on startup, then serves via `gunicorn`. Point
`DATABASE_URL` at a reachable Postgres instance (e.g. a `postgres` service in
docker-compose, or a managed database).

## Notes on the FastAPI → Django migration

- **Same contract, different framework.** Routes, JSON field names (including the
  original's camelCase aliases like `categoryId`/`createdAt`), status codes, and
  the JWT format are all preserved, so this is a drop-in replacement for any
  existing frontend.
- **Improved error handling.** The original FastAPI services raised bare
  `RuntimeError`s for "not found" / "unauthorized" / "invalid credentials", which
  FastAPI (with no exception handlers registered) would have surfaced as `500`.
  This version raises DRF's `NotFound` (`404`), `PermissionDenied` (`403`), and
  `AuthenticationFailed`/validation errors (`401`/`400`) instead — same triggers,
  correct HTTP semantics.
- **No Django admin.** Since auth is JWT-only and the API doesn't use Django
  sessions, `django.contrib.admin`/`sessions`/`messages` were left out rather than
  half-wired against the lean custom `User` model — the original app had no admin
  UI either.
- **Explicit indexes over ORM defaults.** Foreign keys that already have a
  composite index leading with that column have their automatic single-column
  index disabled (`db_index=False`) to avoid duplicate indexes — see
  [Database schema](#database-schema).
