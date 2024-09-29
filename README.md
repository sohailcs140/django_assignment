# Django Assignment

# Stock Trading - API Documentation

## Table of Contents
- [Django Assignment](#django-assignment)
- [Stock Trading - API Documentation](#stock-trading---api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Tech Stack](#tech-stack)
  - [Setup Guide](#setup-guide)
    - [Pre-requisites](#pre-requisites)
    - [Installation](#installation)
    - [Running the Project](#running-the-project)

---

## Project Overview
This is a stock trading platform built using Django REST Framework (DRF) that allows users to:
1. Register with initial balance.
2. Ingest and retrieve stock data.
3. Conduct buy/sell transactions.
4. Cache frequently requested data using Redis for performance improvements.
5. Process transactions asynchronously using Celery and monitor them using Flower.

---

## Tech Stack
- **Backend Framework**: Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Swagger Documentation**: drf-yasg
- **Containerization**: Docker, Docker Compose
- **Testing**: Unit tests with `pytest` and DRF's test client
- **Monitoring**: Flower (for Celery task monitoring)

---

## Setup Guide

### Pre-requisites
- Python 3.12+
- PostgreSQL
- Redis
- Celery
- Docker (if using Docker Compose)

### Installation

1. **Clone the Repository**:
   ```git clone https://github.com/sohailcs140/stock-trading-platform.git
   cd stock-trading-platform
   ```

2. **Create and Activate Virtual Environment**:
   ```python -m venv venv
    venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL Database: Ensure PostgreSQL is running and create a database for the project**:
   ```psql -U postgres
     CREATE DATABASE db_stock;
   ```

5. **Run Migrations**:
   ```python manage.py migrate
   ```


### Running the Project


1. **Start Django Development Server**:
   ```python manage.py runserver
   ```

2. **Run Redis (if not using Docker)**:
   ```redis-server
   ```

3. **Start Celery Worker**:
   ```celery -A config worker -l info --pool=solo
   ```


4. **Start Flower for Monitoring Celery**:
   ```celery -A config flower
   ```

5. Access Swagger API Documentation: Visit http://localhost:8000/swagger/ for interactive API documentation.