# 🛒 Modular Django E-Commerce Backend

A production-aware, modular backend service built with **Django**, **Django REST Framework (DRF)**, and **Docker**. Designed with a clean domain-driven structure (`shop`), optimized database queries, and robust multi-service orchestration.

---

## 🚀 Key Features & Architecture

- **Modular Domain Structure:** Encapsulated `shop` domain containing decoupled models, serializers, service layers, and API views to ensure high maintainability and scalability.
- **Optimized Performance:** Avoids N+1 query overhead by leveraging prefetching and efficient serializer fields (`ReadOnlyField` for stock state).
- **Custom Business Logic & Services:** Dedicated service layers for filtering, category hierarchies, and cart/checkout workflows.
- **Dockerized Environment:** Fully containerized setup featuring multi-service orchestration (Django, MySQL, Redis) with healthchecks and smart database readiness polling (`docker-entrypoint.sh`).
- **Clean RESTful APIs:** Well-structured DRF endpoints for products, categories, tags, search metadata, and cart management.

---

## 🛠 Tech Stack

- **Framework:** Python 3.12, Django 5.x, Django REST Framework
- **Database:** MySQL 8.0
- **Caching / Broker:** Redis
- **Containerization:** Docker & Docker Compose

---

## 📂 Project Structure
```text
backend_django/
├── shop/                  # Core e-commerce domain module
│   ├── api_views/         # DRF API endpoint views
│   ├── models/            # Modular database models (Product, Cart, Category, etc.)
│   ├── serializers/       # DRF serializers with optimized fields
│   ├── services/          # Business logic & filter services
│   ├── views/             # Template/HTML views & helpers
│   └── migrations/        # Database migration history
├── Dockerfile             # Production-ready Python slim image
├── docker-entrypoint.sh   # Smart database readiness & auto-migration script
└── manage.py
docker-compose.yml         # Local development service orchestration
