# Event Management API

A RESTful Event Management API built with **FastAPI** and **PostgreSQL**.

This application supports:

- User registration & authentication (JWT)
- Event creation and management
- RSVP functionality
- Organiser statistics
- Health check endpoint for deployment environments
- Async database connection pooling
- Environment-based configuration (12-factor compliant)

---

# Tech Stack

- **Python 3.11+**
- **FastAPI**
- **PostgreSQL**
- **psycopg (async)**
- **JWT authentication**
- **bcrypt password hashing**
- **AsyncConnectionPool**

---

# Project Structure

```
.
├── db/
│   ├── connection.py
│   └── seeds/
├── app/
│   └── events_app.py
├── main.py
├── .env.example
└── README.md
```

---

# Running the Application Locally

## 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

---

## 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a file called:

```
.env
```

Copy the contents from `.env.example` and provide real values.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/events_db

DB_NAME=events_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

JWT_SECRET=your_super_secret_key
```

⚠️ The `.env` file must NOT be committed to Git.

---

# Environment Variables

The application uses environment variables for all configuration.

| Variable | Description |
|----------|-------------|
| DATABASE_URL | Full PostgreSQL connection string used by the async connection pool |
| DB_NAME | PostgreSQL database name (used for seed scripts) |
| DB_USER | PostgreSQL username |
| DB_PASSWORD | PostgreSQL password |
| DB_HOST | PostgreSQL host |
| DB_PORT | PostgreSQL port |
| JWT_SECRET | Secret key used to sign JWT tokens |

Example `DATABASE_URL` format:

```
postgresql://username:password@host:5432/database_name
```

This design follows 12-factor app principles and allows seamless deployment to AWS.

---

# Database Setup

Ensure PostgreSQL is running locally.

Create your database:

```sql
CREATE DATABASE events_db;
```

---

## Seed the Database

Run:

```bash
python main.py
```

This will:

- Drop existing tables
- Recreate schema
- Seed users, events, and RSVPs

---

# Running the API

Start the server:

```bash
uvicorn main:app --reload --port 5431
```

API will be available at:

```
http://127.0.0.1:5431
```

---

# API Documentation

Interactive Swagger UI:

```
http://127.0.0.1:5431/docs
```

ReDoc:

```
http://127.0.0.1:5431/redoc
```

---

# Health Check Endpoint

```
GET /api/health
```

Returns:

```json
{
  "status": "ok"
}
```

This endpoint:

- Does NOT query the database
- Always returns HTTP 200
- Is intended for AWS load balancer health checks

---

# Authentication

Authentication uses:

- bcrypt for password hashing
- JWT tokens (HS256)

Login endpoint:

```
POST /auth/login
```

Returns:

```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

Authenticated routes require:

```
Authorization: Bearer <token>
```

---

# Features

## Public Endpoints

- `GET /events`
- `GET /events/{id}`
- `GET /api/health`

## Authenticated Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /api/events`
- `PATCH /api/events/{event_id}`
- `POST /api/events/{event_id}/rsvp`
- `DELETE /api/events/{event_id}/rsvp/me`
- `GET /api/events/{event_id}/attendees`
- `GET /api/user/me/events`
- `GET /api/organisers/{id}/stats`

---

# Architecture Notes

- Uses async PostgreSQL connection pooling
- Uses dependency injection (`Depends`)
- JWT authentication via OAuth2PasswordBearer
- In-memory caching for event list endpoint
- Environment-variable driven configuration
- Health endpoint for container orchestration systems

---

# Deployment Ready

The application:

- Uses environment variables only (no hardcoded credentials)
- Includes a lightweight health check endpoint
- Supports async connection pooling
- Is suitable for Docker and AWS ECS/EC2 deployment

---

# Security Notes

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes
- Sensitive configuration is never stored in source control

---

# Bucket Names

- The S3 Bucket must be unique
- Replace the bucket name in backend.tf with a unique name in your AWS account before running 'terraform init'

## EC2 Configuration

- Instance Type: t2.micro (AWS Free Tier eligible)
- Operating System: Ubuntu Server 22.04 LTS (Latest Stable)
- AMI Source: AWS SSM Parameter Store (Canonical official Ubuntu AMI)
- Region: eu-west-2

## EC2 Deployment

- Instance Type: t3.micro (Free Tier eligible)
- OS: Ubuntu 22.04 LTS
- FastAPI running on port 8000
- HTTP security group allows 0.0.0.0/0 on port 8000
- SSH restricted to my IP

## Accessing the API

The API can be accessed at:

http://<EC2_PUBLIC_IP>:8000

Example:
http://18.175.xx.xx:8000