# Backend Schema — operational tables

**Owner:** Patrick Ndaziramiye (Backend)
**Schema:** `public`
**Migration:** `backend/apps/core/migrations/`

These four tables are the application's source of truth. Everything the API
reads or writes lives here. Nothing else writes to them.

```mermaid
erDiagram
    USERS      ||--o{ POSTS    : writes
    USERS      ||--o{ COMMENTS : writes
    CATEGORIES ||--o{ POSTS    : groups
    POSTS      ||--o{ COMMENTS : has

    USERS {
        bigint      id          PK
        varchar     email       UK
        varchar     name
        varchar     password
        varchar     role              "ADMIN | USER"
        boolean     is_active         "admin deactivates, never deletes"
        timestamptz created_at
    }

    CATEGORIES {
        bigint      id          PK
        varchar     name        UK    "4 seeded rows"
        varchar     description
    }

    POSTS {
        bigint      id          PK
        varchar     title
        text        content
        varchar     image             "nullable - stretch goal"
        bigint      category_id FK
        bigint      author_id   FK
        timestamptz created_at
        timestamptz updated_at
    }

    COMMENTS {
        bigint      id          PK
        text        content
        bigint      post_id     FK
        bigint      author_id   FK
        timestamptz created_at
    }
```

## Delete behaviour

| Foreign key | On delete | Reason |
| --- | --- | --- |
| `POSTS.author_id` → USERS | RESTRICT | contributor stats depend on these rows |
| `COMMENTS.author_id` → USERS | RESTRICT | same |
| `COMMENTS.post_id` → POSTS | CASCADE | an orphaned comment thread is meaningless |
| `POSTS.category_id` → CATEGORIES | RESTRICT | the four categories are fixed |

Admin "delete user" sets `is_active = false`. No user row is ever removed.

## Indexes

```sql
CREATE INDEX idx_posts_cat_created ON posts (category_id, created_at DESC);
CREATE INDEX idx_posts_author      ON posts (author_id);
CREATE INDEX idx_comments_post     ON comments (post_id, created_at);
CREATE INDEX idx_comments_created  ON comments (created_at DESC);
```

All four exist for the analytics layer as much as for the API. Do not drop
them without telling the Data Engineer.

## Category naming

The written spec lists NEWS / EVENT / DISCUSSION / ALERT. The Figma shows
Events / Lost & Found / Recommendations / Help Requests. `CATEGORIES` is a
table rather than an enum, so settling this is an `UPDATE` on four rows —
no migration, no reseed, no frontend change.

## Contract

Column names and types here are a contract with the analytics layer
(see `schema-analytics.md`). Renaming a column or changing a timestamp type
breaks the three analytics views. Flag it in the team channel before you
migrate.
