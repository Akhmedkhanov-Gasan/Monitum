# Monitum

Monitum is a backend service for uptime monitoring built with Django and Django REST Framework.

The goal of the project is to implement a real-world monitoring backend that can:

- Track monitored targets (websites / endpoints)
- Periodically check availability
- Store check results
- Expose structured REST API
- Provide a foundation for alerts and observability features

This is a backend-focused pet project evolving toward a production-grade monitoring service.

---

## Core Idea

Monitum is designed as a monitoring backend similar in concept to services like UptimeRobot or Pingdom, but implemented from scratch to explore:

- Django ORM mechanics
- Clean REST API design
- Ownership and multi-user isolation
- Background processing architecture (future-ready)
- Extensible domain models

The project prioritizes architectural clarity and explicit control over abstractions.

---

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- Token Authentication
- SQLite (development)
- Modular app structure

Planned:

- PostgreSQL
- Celery (periodic checks)
- Redis
- Docker
- CI/CD

---

## Main Domain Concepts

### 1. Users

Each user owns their monitored resources.

Ownership is enforced at the ORM level to ensure data isolation.

---

### 2. Monitored Targets

Users can register targets (e.g., URLs or endpoints) that need to be checked.

Each target:

- Belongs to a specific user
- Stores metadata (URL, interval, status, etc.)
- Acts as a parent entity for monitoring checks

---

### 3. Monitoring Checks

Checks represent individual availability tests.

A check typically stores:

- Timestamp
- Status (UP / DOWN)
- Response time
- Error message (if failed)

This creates a time-series-like structure inside relational storage.

---

### 4. REST API

The backend exposes structured API endpoints for:

- Creating monitoring targets
- Retrieving user-specific data
- Accessing historical check results
- Updating configuration
- Removing monitored resources

Ownership is enforced via:

```python
Note.objects.filter(owner=request.user)
```

Equivalent SQL logic:

```sql
SELECT *
FROM monitored_target
WHERE owner_id = <request.user.id>;
```

This ensures strict multi-user data isolation.

---

## Project Structure

```
backend/
│
├── uptime/                # Django project configuration
│
└── apps/
    ├── notes/             # Experimental / learning API module
    └── ...                # Monitoring-related apps (core logic)
```

The `notes` module was used as an isolated learning sandbox to deeply understand:

- CRUD mechanics
- ForeignKey relationships
- Reverse relations
- Query optimization
- N+1 problem
- select_related()

It does not represent the core monitoring logic of the project.

---

## Authentication

Token-based authentication is used.

Header example:

```
Authorization: Token <your_token>
```

All user data is scoped to `request.user`.

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

## Architectural Principles

- Explicit over implicit
- ORM-level ownership enforcement
- No hidden permission magic
- Clear domain modeling
- Backend-first thinking
- Scalable structure for future background workers

---

## Roadmap

Planned improvements:

- Background worker for periodic checks (Celery)
- Status aggregation logic
- Alerting system (email / webhook)
- Rate limiting
- Pagination and filtering
- PostgreSQL migration
- Dockerized setup
- Production-ready settings split
- Metrics and observability

---

## Status

Monitum is under active development as a backend-focused pet project.

The current stage focuses on:

- Solid domain modeling
- Correct data isolation
- Clean API foundations
- Performance awareness (query optimization)

---

Author: Gasan Akhmedkhanov  
GitHub: https://github.com/Akhmedkhanov-Gasan