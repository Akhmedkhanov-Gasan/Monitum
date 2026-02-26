# Monitum

Monitum is a backend pet project built with Django and Django REST Framework.

The main goal of this project is to deeply understand:

- Django ORM at the SQL logic level
- ForeignKey mechanics and ownership
- REST API lifecycle
- Authentication and access control
- Avoiding hidden abstractions and “magic”

This project is developed step-by-step with explicit logic and architectural clarity (APIView instead of ViewSet where possible).

---

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- TokenAuthentication
- SQLite (development)

---

## Core Features

### 1. Notes CRUD (Manual APIView Implementation)

Endpoints:

- GET `/api2/notes/`
- POST `/api2/notes/`
- GET `/api2/notes/<id>/`
- PATCH `/api2/notes/<id>/`
- DELETE `/api2/notes/<id>/`

No routers.  
No generic shortcuts.  
Explicit request handling and validation flow.

---

### 2. Ownership (User-bound Notes)

Each note belongs to a specific user.

```python
owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="notes"
)
```

Behavior:

- `owner` is automatically assigned:

```python
ser.save(owner=request.user)
```

- Users can only see their own notes
- Accessing another user's note returns `404`
- Filtering is enforced at the ORM level

SQL-equivalent logic:

```sql
SELECT *
FROM notes_note
WHERE id = <pk>
AND owner_id = <request.user.id>;
```

---

### 3. ORM Deep Understanding

This project intentionally explores:

- `owner` vs `owner_id`
- How ForeignKey works internally
- Reverse relations via `related_name`
- `user.notes.all()` mechanics
- N+1 query problem
- `select_related("owner")`

The goal is to understand what SQL Django generates and why.

---

## Project Structure

```
backend/
│
├── uptime/               # Django project
│
└── apps/
    └── notes/
        ├── models.py
        ├── api/
        │   ├── views.py
        │   ├── serializers.py
        │   └── urls.py
```

---

## Authentication

Token-based authentication.

Header example:

```
Authorization: Token <your_token>
```

---

## Example Request

Create note:

```json
POST /api2/notes/

{
  "title": "Example",
  "body": "Text"
}
```

Owner is assigned automatically from `request.user`.

---

## Running the Project

```bash
git clone https://github.com/Akhmedkhanov-Gasan/Monitum.git
cd Monitum
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Purpose of This Project
Monitum is not just a CRUD demo.

It is a structured backend training environment focused on:

- Understanding how Django translates Python into SQL
- Manual control over request handling
- Proper ownership enforcement
- Clean REST design
- Building architectural intuition

---

## Future Roadmap

Planned improvements:

- Pagination
- Permission abstraction
- Service layer separation
- PostgreSQL support
- Docker setup
- Celery for background tasks
- Monitoring features aligned with the Monitum concept

---

Author: Gasan Akhmedkhanov  
GitHub: https://github.com/Akhmedkhanov-Gasan