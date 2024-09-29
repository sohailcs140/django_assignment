# Django Assignment

# Stock Trading API - API Documentation

## Table of Contents
- [Django Assignment](#django-assignment)
- [Stock Trading API - API Documentation](#stock-trading-api---api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Tech Stack](#tech-stack)
  - [Setup Guide](#setup-guide)
    - [Pre-requisites](#pre-requisites)
    - [Installation](#installation)
    - [Running the Project](#running-the-project)
  - [API Endpoints](#api-endpoints)
  - [Data Models](#data-models)
    - [User Model](#user-model)
    - [StockData Model](#stockdata-model)
    - [Transaction Model](#transaction-model)
  - [Caching with Redis](#caching-with-redis)
  - [Task Queue with Celery](#task-queue-with-celery)
    - [Monitoring Celery Tasks](#monitoring-celery-tasks)
  - [Docker Compose File](#docker-compose-file)
  - [Unit Testing](#unit-testing)
  - [Assumptions](#assumptions)

---

## Project Overview
This is a stock trading api built using Django REST Framework (DRF) that allows users to:
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
   ```
   git clone https://github.com/sohailcs140/stock-trading-platform.git
   cd stock-trading-platform
   ```

2. **Create and Activate Virtual Environment**:
   ```
    python -m venv venv
    venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL Database: Ensure PostgreSQL is running and create a database for the project**:
   ```
     psql -U postgres
     CREATE DATABASE db_stock;
   ```

5. **Run Migrations**:
   ```
    python manage.py migrate
   ```


### Running the Project


1. **Start Django Development Server**:
   ```
   python manage.py runserver
   ```

2. **Run Redis (if not using Docker)**:
   ```
   redis-server
   ```

3. **Start Celery Worker**:
   ```
   celery -A config worker -l info --pool=solo
   ```


4. **Start Flower for Monitoring Celery**:
   ```
   celery -A config flower
   ```

5. Access Swagger API Documentation: Visit `http://localhost:8000/swagger/` for interactive API documentation.


## API Endpoints

1. **Users**:
   - POST /users/: Register a new user with a username and balance.
   - GET /users/{username}/: Retrieve user details by username (Cached).
2. **Stock Data**:
   - POST /stocks/: Ingest stock data.
   - GET /stocks/: Retrieve all stock data (Cached).
   - GET /stocks/{ticker}/: Retrieve stock data for a specific ticker (Cached).
3. **Transactions**:
   - POST /transactions/: Create a buy/sell transaction.
   - GET /transactions/{user_id}/: Get all transactions for a specific user.
   - GET /transactions/{user_id}/{start_timestamp}/{end_timestamp}/: Get user transactions within a date range.
  


## Data Models

### User Model
```
class User(models.Model):
    user_id = models.CharField(primary_key=True,max_length=36, default=uuid4)
    username = models.CharField(max_length=50, unique=True,blank=False, null=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])
```

### StockData Model
```
class StockData(models.Model):
    ticker = models.CharField(max_length=15, unique=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])
    close_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2,validators=[MinValueValidator(0.0)])
    volume = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
```


### Transaction Model
```
class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    ticker = models.CharField(max_length=10)
    transaction_type = models.CharField(max_length=4, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    transaction_volume = models.IntegerField()
    transaction_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
```


## Caching with Redis
   - Users,StockData and Transaction are cached to optimize performance using Redis
   - The cache is updated upon creation of new users or stock entries or transaction.
   - Cache keys
      - ***Users***: `{username}`
      - ***StockData***: `{ticker}`, `{stock_data}`
      - ***Trsactioins***: `{username}`_transactions, `{username}`_`{start_timestamp}`_`{end_timestamp}`_transactions


## Task Queue with Celery
   - Transactions are processed asynchronously using Celery.
   - Upon transaction creation, a Celery task is dispatched for
      - Calculating the transaction price.
      - Updating the user’s balance.
      - Updating the stock base on transaction type.


### Monitoring Celery Tasks
 
   - Visit http://localhost:5555 to access the Flower dashboard for task monitoring.

## Docker Compose File
```
version: '3.8'

services:
  db:
    image: postgres
    environment:
      POSTGRES_DB: db_stock
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: root
    ports:
      - "5432:5432"

  redis:
    image: redis
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker -l info --pool=solo
    depends_on:
      - web
      - redis

  flower:
    build: .
    command: celery -A config flower
    ports:
      - "5555:5555"
    depends_on:
      - celery
```


## Unit Testing
Unit tests for the APIs are written using pytest and DRF's test client. To run the tests:
***Tests are included for***:
  - User creation and retrieval.
  - Stock data creation and retrieval.
  - Transaction creation and validation.


## Assumptions

1. The user's balance is updated only after a successful transaction.
2. Stock data is considered immutable; once added, it cannot be changed.
3. Stock data volume is updated base on the transaction type.
4. Celery handles all asynchronous operations for transactions.
5. Redis caching is used for optimizing frequent data access.
