# Restaurant & Food Business Website Builder SaaS

A multi-tenant SaaS backend built with **Django**, **Django REST Framework**, and **PostgreSQL** that enables restaurants, cafés, and food businesses to manage their business profiles, team memberships, product catalogs, customer orders, websites, and WhatsApp order notifications.

> **Project Status:** Early-stage backend foundation. The relational database schema, Django migrations, Django Admin registrations, Docker Compose environment, and core multi-tenant permission classes are implemented. Public/tenant REST API routing, authentication endpoints, WhatsApp delivery workers, subscription enforcement, and automated tests are not yet implemented.

---

## Table of Contents

1. [Project Overview & Purpose](#project-overview--purpose)
2. [Current Implementation Status](#current-implementation-status)
3. [Technology Stack](#technology-stack)
4. [Repository Structure](#repository-structure)
5. [Architecture Overview](#architecture-overview)
6. [Implemented Database & Domain Components](#implemented-database--domain-components)
7. [Local Development Setup (Docker Compose)](#local-development-setup-docker-compose)
8. [Environment Configuration](#environment-configuration)
9. [Common Management Commands](#common-management-commands)
10. [Current Limitations & Incomplete Features](#current-limitations--incomplete-features)
11. [Roadmap & Planned Milestones](#roadmap--planned-milestones)
12. [Project Documentation](#project-documentation)

---

## Project Overview & Purpose

Small and medium food businesses (restaurants, cafés, bakeries) often need a simple way to publish an online storefront, manage menus with variants, and receive customer orders—especially via WhatsApp—without building custom software from scratch.

This platform is designed around a multi-tenant architecture where:

- A **User** can own or belong to multiple **Businesses** with role-based access (`Owner`, `Manager`, `Staff`).
- Each **Business** has one **Website** backed by a configurable **Theme**, ordered **WebsiteSections**, and **Domains**.
- Each **Business** manages its own **Categories**, **Products**, **ProductVariants**, **Customers**, and **Orders**.
- **Subscriptions** and **Plans** are modeled to support tiered capabilities (such as Basic, Standard, and Premium plans).
- **WhatsApp** notifications and an outbox/audit log are modeled to support reliable order notifications.

---

## Current Implementation Status

| Area | Status | Details |
| :--- | :--- | :--- |
| **Database Schema & Migrations** | Implemented | All 7 Django apps have models, constraints, indexes, and migrations. |
| **Custom User Model** | Implemented | UUID-based custom User model with email as USERNAME_FIELD (`accounts.User`) with `UserAdmin`. |
| **Django Admin** | Implemented | All domain models are registered in `admin.py` across all 7 apps. |
| **Multi-Tenant Permissions** | Implemented | `IsActiveBusinessMember`, `IsBusinessManagerOrOwner`, `IsBusinessOwner` in `businesses/permissions.py`. |
| **Docker & Env Configuration** | Implemented | `docker-compose.yml` (PostgreSQL 17 + Django), `backend/Dockerfile`, `.env.example`, and `django-environ` settings. |
| **Serializers & Views (`accounts`, `businesses`)** | Partial | `UserSerializer`, `RegisterSerializer`, `PasswordReset*`, `BusinessSerializer`, `MembershipSerializer`, and `BusinessViewSet` exist, but are not yet wired into `urls.py`. |
| **REST API Routing & Endpoints** | Not Implemented | `config/urls.py` only mounts `/admin/`. `catalog`, `orders`, `subscriptions`, `websites`, and `integrations` have placeholder `views.py` files. |
| **Authentication Endpoints** | Not Implemented | No login, logout, or token/JWT endpoints exist yet. |
| **WhatsApp Delivery Worker** | Not Implemented | Models exist (`WhatsappIntegration`, `NotificationOutBox`, `NotificationLog`), but no background worker or provider integration is implemented. |
| **Subscription Plan Enforcement** | Not Implemented | `Plan`, `PlanFeature`, and `Subscription` models exist, but no feature-gating logic is implemented. |
| **Automated Tests** | Not Implemented | All `tests.py` files are currently empty placeholders. |

---

## Technology Stack

- **Current Backend Foundation:**
  - **Language:** Python 3.12 (configured in [`backend/Dockerfile`](backend/Dockerfile))
  - **Web Framework:** Django (`>=6.1,<6.2`)
  - **API Framework:** Django REST Framework (`>=3.18,<3.19`)
  - **Database:** PostgreSQL 17 (`postgres:17-alpine` in [`docker-compose.yml`](docker-compose.yml))
  - **Database Driver:** `psycopg[binary]` (`>=3.3,<3.4`)
  - **Environment Management:** `django-environ` (`>=0.12`)
  - **Containerization:** Docker & Docker Compose
- **Planned Frontend & Future Infrastructure** *(per [Milestone 2 Architecture Plan](docs/milestones/milestone_2/Milestone_2_Backend_First_Architecture_Plan.pdf))*:
  - **Frontend:** Next.js + TypeScript (React), to be built after backend completion and verification
  - **Async Notifications:** Redis + background worker (at the integration stage)
  - **Media Storage:** Local development storage; S3-compatible object storage in production

---

## Repository Structure

```text
business_website_builder_saas/
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── docker-compose.yml              # PostgreSQL 17 + Django backend services
├── docs/
│   ├── db_design/
│   │   ├── Restaurant Website Builder SaaS.png
│   │   ├── mermaid-diagram.png
│   │   └── saas_database_design_redesigned.pdf
│   └── milestones/
│       ├── milestone_1/
│       │   ├── Milestone_1_Final_PostgreSQL_Schema_and_ERD.pdf
│       │   └── Milestone_1_Restaurant_SaaS_Database_Design.pdf
│       └── milestone_2/
│           └── Milestone_2_Backend_First_Architecture_Plan.pdf
└── backend/
    ├── .dockerignore               # Excludes .venv, caches, and env files from Docker builds
    ├── Dockerfile                  # Python 3.12-slim image for Django backend
    ├── manage.py                   # Django management CLI
    ├── requirements.txt            # Python dependencies
    ├── config/                     # Django project configuration
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py                 # Currently exposes /admin/ only
    │   └── wsgi.py
    └── apps/                       # Modular domain applications
        ├── accounts/               # Custom User model, admin, auth serializers/views (unwired)
        ├── businesses/             # Business, Membership, BusinessHours, RBAC permissions
        ├── catalog/                # Category, Product, ProductVariant
        ├── integrations/           # WhatsappIntegration, NotificationOutBox, NotificationLog, AuditLog
        ├── orders/                 # Customer, Order, OrderItem, OrderStatusHistory
        ├── subscriptions/          # Plan, PlanFeature, Subscription
        └── websites/               # Theme, Website, WebsiteSection, Domain
```

---

## Architecture Overview

The backend follows a **modular monolith** layout under `backend/apps/`:

- **Project Configuration (`backend/config/`)**: Centralizes settings via `django-environ`, reading from the root `.env` (or `backend/.env`).
- **Multi-Tenancy (`apps.businesses`)**: Tenant isolation is centered around `Business` and `Membership`. A user can hold multiple memberships across businesses with `owner`, `manager`, or `staff` roles and `active`, `invited`, or `suspended` statuses.
- **Object-Level RBAC (`apps.businesses.permissions`)**: Reusable DRF permission classes (`IsActiveBusinessMember`, `IsBusinessManagerOrOwner`, `IsBusinessOwner`) resolve the target `Business` from either a `Business` instance or a related model with a `.business` attribute.
- **UUID Primary Keys**: All domain models use `uuid.UUIDField` primary keys.

---

## Implemented Database & Domain Components

1. **`apps.accounts`**
   - `User`: Custom `AbstractUser` with UUID primary key, email login (`USERNAME_FIELD = "email"`), and `username = None`.
2. **`apps.businesses`**
   - `Business`: Tenant entity with slug, business type, contact details, currency (`EGP` default), and timezone (`Africa/Cairo` default).
   - `Membership`: Links `User` and `Business` with `role` (`owner`, `manager`, `staff`) and `status` (`active`, `invited`, `suspended`).
   - `BusinessHours`: Per-weekday opening/closing times and closed flags.
3. **`apps.catalog`**
   - `Category`: Menu/catalog categories scoped to a business.
   - `Product`: Menu items with price (`>= 0` check constraint), availability, and ordering position.
   - `ProductVariant`: Size/option variants with optional per-product SKU and `price_delta`.
4. **`apps.orders`**
   - `Customer`: Per-business customer contact records.
   - `Order`: Tracks status (`Pending`, `Confirmed`, `Preparing`, `Ready`, `Completed`, `Cancelled`), channel (`Website`, `Admin`), delivery type (`Pickup`, `Delivery`), idempotency key, and non-negative monetary totals.
   - `OrderItem`: Line items referencing optional `Product`/`ProductVariant` with snapshot fields (`product_name`, `unit_price`, `line_total`, `selected_options`).
   - `OrderStatusHistory`: Audit trail of order status transitions.
5. **`apps.subscriptions`**
   - `Plan`: Subscription tiers with billing interval (`Monthly`, `Yearly`, `Free`) and pricing.
   - `PlanFeature`: Key/value JSON feature definitions per plan.
   - `Subscription`: Tracks a business's active/trialing/canceled subscription period and external provider reference.
6. **`apps.websites`**
   - `Theme`: Reusable website theme definitions with JSON `default_config`.
   - `Website`: One-to-one website per `Business` with draft/published configuration snapshots and status (`Draft`, `Published`, `Suspended`).
   - `WebsiteSection`: Ordered sections (`Hero`, `Product_grid`, `Gallery`) belonging to a website.
   - `Domain`: Platform or custom hostnames with verification status and a single-primary-domain constraint per website.
7. **`apps.integrations`**
   - `WhatsappIntegration`: One-to-one per business storing mode, phone number, provider metadata, and connection status.
   - `NotificationOutBox`: Transactional outbox table with deduplication key, retry count, and scheduling timestamp.
   - `NotificationLog`: Delivery log per order/channel/event.
   - `AuditLog`: General action audit log per business and actor user.

---

## Local Development Setup (Docker Compose)

### Prerequisites

- **Docker** and **Docker Compose** installed and running.
- (Optional, for running commands outside Docker) **Python 3.12+** and a reachable **PostgreSQL 17** instance.

### Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd business_website_builder_saas
   ```

2. **Create your local `.env` file from `.env.example`:**
   - **Bash / macOS / Linux:**
     ```bash
     cp .env.example .env
     ```
   - **PowerShell (Windows):**
     ```powershell
     Copy-Item .env.example .env
     ```
   Update `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` in `.env` with local development values. Keep `DB_HOST=db` when running via Docker Compose.

3. **Build and start the services:**
   ```bash
   docker compose up --build
   ```
   This starts:
   - `db`: PostgreSQL 17 Alpine with a `pg_isready` healthcheck.
   - `backend`: Django development server on `http://localhost:8000` (waits until `db` is healthy).

   > **Note:** These Docker Compose commands are derived from [`docker-compose.yml`](docker-compose.yml) and [`backend/Dockerfile`](backend/Dockerfile), and still need to be verified in an environment with Docker available.

4. **Apply database migrations:**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create a Django superuser (for Django Admin):**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
   You will be prompted for an email address and password.

6. **Access Django Admin:**
   Open `http://localhost:8000/admin/` in your browser and sign in with your superuser credentials.

---

## Environment Configuration

### Required & Standard Variables (Defined in [`.env.example`](.env.example))

The following nine variables are defined in [`.env.example`](.env.example):

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | **Required.** Cryptographic signing key for Django. Startup fails with `ImproperlyConfigured` if missing or empty. | *(set in `.env`)* |
| `DJANGO_DEBUG` | Enables Django debug mode (`True` for local dev, `False` for production). | `False` (code default) / `True` (`.env.example`) |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hostnames. | `localhost,127.0.0.1` |
| `POSTGRES_DB` | PostgreSQL database name. | `saas_website_builder` |
| `POSTGRES_USER` | PostgreSQL username. | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password. | *(set in `.env`)* |
| `DB_HOST` | PostgreSQL host (`db` inside Docker Compose, `localhost` for local host). | `db` |
| `DB_PORT` | PostgreSQL port. | `5432` |
| `FRONTEND_URL` | Base URL of the frontend app (used to build password reset links). | `http://localhost:3000` |

### Optional Environment Overrides

- `EMAIL_BACKEND`: Not included in `.env.example`. Supported by [`backend/config/settings.py`](backend/config/settings.py) and defaults to `django.core.mail.backends.console.EmailBackend`. Set it in `.env` only if you want to override the console email backend.

---

## Common Management Commands

Run these inside the running `backend` container via Docker Compose (or from `backend/` using your activated virtual environment when PostgreSQL is reachable):

- **Django system checks:**
  ```bash
  docker compose exec backend python manage.py check
  ```
- **Deployment readiness check:**
  ```bash
  docker compose exec backend python manage.py check --deploy
  ```
- **Check for unapplied or missing migrations:**
  ```bash
  docker compose exec backend python manage.py makemigrations --check --dry-run
  ```
- **Apply migrations:**
  ```bash
  docker compose exec backend python manage.py migrate
  ```
- **Create superuser:**
  ```bash
  docker compose exec backend python manage.py createsuperuser
  ```
- **Run test suite:**
  ```bash
  docker compose exec backend python manage.py test
  ```
  *(Note: All `tests.py` files are currently empty placeholders; no meaningful automated test cases exist yet.)*

---

## Current Limitations & Incomplete Features

- **No Mounted API Routes:** [`backend/config/urls.py`](backend/config/urls.py) only exposes `admin/`. None of the `apps/*` modules have `urls.py` files yet.
- **Unfinished App Endpoints:** `catalog`, `orders`, `subscriptions`, `websites`, and `integrations` have empty `views.py` files and no serializers.
- **No Authentication/Token Flow:** Registration/password-reset serializers and views exist in `apps.accounts`, but are not wired to URLs, and no login/JWT endpoints exist.
- **No Background Worker / WhatsApp Integration:** `NotificationOutBox` and `WhatsappIntegration` models are defined, but no task runner or WhatsApp Cloud API client exists yet.
- **No Plan Enforcement:** Basic/Standard/Premium plan gating is not yet implemented.
- **No Automated Test Coverage:** All `tests.py` files are currently empty.

---

## Roadmap & Planned Milestones

Following the backend-first delivery sequence in [`Milestone_2_Backend_First_Architecture_Plan.pdf`](docs/milestones/milestone_2/Milestone_2_Backend_First_Architecture_Plan.pdf):

1. **Milestone 2A — Project Foundation:** Finalize Docker workflow, PostgreSQL setup, environment/secret handling, custom UUID `User` model, health checks, and automated checks.
2. **Milestone 2B — Accounts & Business Ownership:** Wire registration, login/logout, password reset, cookie-based session authentication (HTTP-only + CSRF), business profiles, memberships, and tenant-isolated querysets.
3. **Milestone 2C — Website & Domain Foundation:** Implement themes, website configuration, sections, platform subdomains, and custom domain verification.
4. **Milestone 2D — Catalog & Ordering:** Implement categories, products, variants, server-side order pricing, idempotency, and order-status history.
5. **Milestone 2E — Subscriptions & Integrations:** Implement plan/feature entitlement checks and reliable asynchronous WhatsApp notification delivery via `NotificationOutBox` and `NotificationLog`. *(Online payment processing and registrar-based domain purchasing are deferred.)*
6. **Milestone 2F — Backend Verification & Frontend Handoff:** Complete automated tests, API contracts, security checks, and then begin building the **Next.js + TypeScript** frontend.

---

## Project Documentation

Architecture and database design documents are located in `docs/`:

- **Database Design:**
  - [Database Diagram (PNG)](docs/db_design/Restaurant%20Website%20Builder%20SaaS.png)
  - [Mermaid ERD Diagram (PNG)](docs/db_design/mermaid-diagram.png)
  - [Redesigned SaaS Database Design (PDF)](docs/db_design/saas_database_design_redesigned.pdf)
- **Milestones:**
  - [Milestone 1 — Final PostgreSQL Schema and ERD (PDF)](docs/milestones/milestone_1/Milestone_1_Final_PostgreSQL_Schema_and_ERD.pdf)
  - [Milestone 1 — Restaurant SaaS Database Design (PDF)](docs/milestones/milestone_1/Milestone_1_Restaurant_SaaS_Database_Design.pdf)
  - [Milestone 2 — Backend-First Architecture Plan (PDF)](docs/milestones/milestone_2/Milestone_2_Backend_First_Architecture_Plan.pdf)
