# capsule-care-backend
Capsule Care Backend

A comprehensive REST API for managing medication reminders, prescriptions, doctors, and health tracking.

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Installation

1. Clone the repository and create the project structure:
```bash
mkdir medication-api && cd medication-api
```

2. Create all the necessary files as provided

3. Start the services:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword"
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>
```

---

### Users

#### Get User Profile
```http
GET /api/users/profile
Authorization: Bearer <token>
```

#### Update User Profile
```http
PUT /api/users/profile
Authorization: Bearer <token>

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "language": "en"
}
```

#### User Settings
```http
GET /api/users/settings
POST /api/users/settings
PUT /api/users/settings/:id
DELETE /api/users/settings/:id
Authorization: Bearer <token>
```

#### Emergency Contacts
```http
GET /api/users/emergency-contacts
POST /api/users/emergency-contacts
GET /api/users/emergency-contacts/:id
PUT /api/users/emergency-contacts/:id
DELETE /api/users/emergency-contacts/:id
Authorization: Bearer <token>
```

#### Activity Logs
```http
GET /api/users/activity-logs?page=1&per_page=20
Authorization: Bearer <token>
```

---

### Medications

#### Get All Medications
```http
GET /api/medications?page=1&per_page=20&search=aspirin
Authorization: Bearer <token>
```

#### Get Medication by ID
```http
GET /api/medications/:id
Authorization: Bearer <token>
```

#### Create Medication
```http
POST /api/medications
Authorization: Bearer <token>

{
  "name": "Aspirin",
  "generic_name": "Acetylsalicylic acid",
  "brand_name": "Bayer",
  "description": "Pain reliever and anti-inflammatory",
  "dosage_form": "Tablet",
  "strength": "100mg",
  "requires_prescription": false
}
```

#### Update Medication
```http
PUT /api/medications/:id
Authorization: Bearer <token>
```

#### Delete Medication
```http
DELETE /api/medications/:id
Authorization: Bearer <token>
```

#### User Medications (Personal medication list)
```http
GET /api/medications/user
POST /api/medications/user
GET /api/medications/user/:id
PUT /api/medications/user/:id
DELETE /api/medications/user/:id
Authorization: Bearer <token>
```

---

### Doctors

#### Get All Doctors
```http
GET /api/doctors?page=1&per_page=20&search=cardiology
Authorization: Bearer <token>
```

#### Get Doctor by ID
```http
GET /api/doctors/:id
Authorization: Bearer <token>
```

#### Create Doctor
```http
POST /api/doctors
Authorization: Bearer <token>

{
  "first_name": "Jane",
  "last_name": "Smith",
  "specialty": "Cardiology",
  "license_number": "MD12345",
  "phone": "+1234567890",
  "email": "dr.smith@example.com",
  "address": "123 Medical Plaza"
}
```

#### Update Doctor
```http
PUT /api/doctors/:id
Authorization: Bearer <token>
```

#### Delete Doctor
```http
DELETE /api/doctors/:id
Authorization: Bearer <token>
```

#### User Doctors (Personal doctor relationships)
```http
GET /api/doctors/user
POST /api/doctors/user
GET /api/doctors/user/:id
PUT /api/doctors/user/:id
DELETE /api/doctors/user/:id
Authorization: Bearer <token>
```

---

### Reminders

#### Get All Reminders
```http
GET /api/reminders
Authorization: Bearer <token>
```

#### Get Reminder by ID
```http
GET /api/reminders/:id
Authorization: Bearer <token>
```

#### Create Reminder
```http
POST /api/reminders
Authorization: Bearer <token>

{
  "user_medication_id": 1,
  "title": "Take morning medication",
  "description": "Take with food",
  "reminder_time": "08:00:00",
  "frequency_type": "daily",
  "frequency_value": 1,
  "start_date": "2025-01-01",
  "push_notification": true,
  "email_notification": false
}
```

#### Update Reminder
```http
PUT /api/reminders/:id
Authorization: Bearer <token>
```

#### Delete Reminder
```http
DELETE /api/reminders/:id
Authorization: Bearer <token>
```

#### Reminder Logs
```http
GET /api/reminders/:reminder_id/logs?page=1&per_page=20
PUT /api/reminders/logs/:log_id
Authorization: Bearer <token>
```

---

### Prescriptions

#### Get All Prescriptions
```http
GET /api/prescriptions?status=active
Authorization: Bearer <token>
```

#### Get Prescription by ID
```http
GET /api/prescriptions/:id
Authorization: Bearer <token>
```

#### Create Prescription
```http
POST /api/prescriptions
Authorization: Bearer <token>

{
  "doctor_id": 1,
  "medication_id": 1,
  "prescription_number": "RX123456",
  "prescribed_date": "2025-01-01",
  "expiry_date": "2026-01-01",
  "dosage": "100mg",
  "frequency": "twice daily",
  "quantity": 60,
  "refills_remaining": 3,
  "instructions": "Take with food",
  "status": "active"
}
```

#### Update Prescription
```http
PUT /api/prescriptions/:id
Authorization: Bearer <token>
```

#### Delete Prescription
```http
DELETE /api/prescriptions/:id
Authorization: Bearer <token>
```

---

### Notifications

#### Get All Notifications
```http
GET /api/notifications?page=1&per_page=20&unread_only=true
Authorization: Bearer <token>
```

#### Get Notification by ID
```http
GET /api/notifications/:id
Authorization: Bearer <token>
```

#### Mark as Read
```http
PUT /api/notifications/:id/read
Authorization: Bearer <token>
```

#### Mark All as Read
```http
PUT /api/notifications/mark-all-read
Authorization: Bearer <token>
```

#### Delete Notification
```http
DELETE /api/notifications/:id
Authorization: Bearer <token>
```

#### Medication Intake Tracking
```http
GET /api/notifications/intake?page=1&per_page=20
POST /api/notifications/intake
PUT /api/notifications/intake/:id
Authorization: Bearer <token>
```

Example Create Intake:
```json
{
  "user_medication_id": 1,
  "status": "taken",
  "dosage_taken": "100mg",
  "status_at": "2025-01-15T08:00:00Z",
  "notes": "Felt fine after taking",
  "side_effects_reported": null
}
```

---

### Media Files

#### Get All Media Files
```http
GET /api/media?page=1&per_page=20&entity_type=prescription&entity_id=1
Authorization: Bearer <token>
```

#### Get Media File by ID
```http
GET /api/media/:id
Authorization: Bearer <token>
```

#### Create Media File
```http
POST /api/media
Authorization: Bearer <token>

{
  "related_entity_id": 1,
  "related_entity_type": "prescription",
  "original_name": "prescription_scan.pdf",
  "file_path": "/uploads/prescriptions/123.pdf",
  "file_type": "document",
  "mime_type": "application/pdf",
  "file_size": 1024000,
  "description": "Prescription from Dr. Smith"
}
```

#### Update Media File
```http
PUT /api/media/:id
Authorization: Bearer <token>
```

#### Delete Media File
```http
DELETE /api/media/:id
Authorization: Bearer <token>
```

---

## 📊 Database Models

### Core Models

- **User** - User accounts with authentication
- **Medication** - Medication catalog
- **Doctor** - Healthcare provider information
- **UserMedication** - User's personal medication list
- **UserDoctor** - User-doctor relationships
- **Prescription** - Prescription records
- **Reminder** - Medication reminders
- **ReminderLog** - Reminder execution history
- **Notification** - System notifications
- **MedicationIntake** - Medication intake tracking
- **MediaFile** - File attachments (prescriptions, images, etc.)
- **UserSetting** - User preferences
- **EmergencyContact** - Emergency contacts
- **ActivityLog** - User activity audit log

---

## 🔐 Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require JWT authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

Tokens expire after 1 hour (configurable in `config.py`).

---

## 🛠️ Project Structure

```
medication-api/
├── docker-compose.yml
└── api/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── __init__.py
    ├── config.py
    ├── extensions.py
    ├── models.py
    └── routes/
        ├── __init__.py
        ├── auth.py
        ├── main.py
        ├── medications.py
        ├── doctors.py
        ├── reminders.py
        ├── prescriptions.py
        ├── users.py
        ├── notifications.py
        └── media.py
```

---

## 🧪 Testing the API

### Using cURL

**Register a user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**Get medications (with auth):**
```bash
curl -X GET http://localhost:5000/api/medications \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman

1. Import the endpoints into Postman
2. Set up an environment variable for the token
3. Use `{{token}}` in the Authorization header

---

## ⚙️ Configuration

Edit `api/config.py` to customize:

- **Database URL** - PostgreSQL connection string
- **JWT Secret Key** - Secret for token signing
- **Token Expiration** - Access token lifetime
- **Debug Mode** - Enable/disable debug mode

### Environment Variables

Set these in `docker-compose.yml`:

```yaml
environment:
  DATABASE_URL: postgresql://user:pass@db:5432/dbname
  JWT_SECRET_KEY: your-super-secret-key
  SECRET_KEY: your-flask-secret-key
  FLASK_ENV: development
```

---

## 🔄 Database Migrations

The database tables are automatically created when the app starts. For production, consider using Alembic for migrations:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## 📝 Response Formats

### Success Response
```json
{
  "message": "Operation successful",
  "data": { }
}
```

### Error Response
```json
{
  "error": "Error message describing what went wrong"
}
```

### Paginated Response
```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

---

## 🚦 HTTP Status Codes

- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🔒 Security Best Practices

1. **Change default secrets** in production
2. **Use HTTPS** in production
3. **Implement rate limiting** for API endpoints
4. **Enable CORS** only for trusted domains
5. **Validate all input** data
6. **Use strong passwords** (implement password strength validation)
7. **Implement refresh tokens** for better security
8. **Add request logging** for audit trails

---

## 🚀 Production Deployment

### Recommended Setup

1. **Use environment variables** for all sensitive config
2. **Enable PostgreSQL SSL** connections
3. **Set up Nginx** as reverse proxy
4. **Implement Redis** for caching
5. **Add Celery** for background tasks (reminder notifications)
6. **Configure logging** with rotation
7. **Set up monitoring** (Sentry, Datadog, etc.)
8. **Use Docker secrets** instead of environment variables

### Docker Production Example

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_user
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./api
    environment:
      FLASK_ENV: production
    secrets:
      - jwt_secret
    command: gunicorn -w 4 -b 0.0.0.0:5000 app:app

secrets:
  db_user:
    external: true
  db_password:
    external: true
  jwt_secret:
    external: true
```

---

## 📦 Dependencies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **psycopg2-binary** - PostgreSQL adapter
- **Flask-CORS** - CORS support
- **python-dotenv** - Environment variables

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

MIT License - feel free to use this project for your own purposes.

---

## 🐛 Troubleshooting

### Database connection issues
```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs db

# Restart services
docker-compose restart
```

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 instead of 5000
```

### Token expired
```bash
# Adjust token expiration in config.py
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
```

---

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review the code comments

---

## 🎯 Roadmap

- [ ] Add email notifications for reminders
- [ ] Implement SMS notifications
- [ ] Add AI-powered medication interaction checker
- [ ] Create mobile app integration
- [ ] Add analytics dashboard
- [ ] Implement family/caregiver accounts
- [ ] Add pharmacy integration
- [ ] Implement medication adherence reports
- [ ] Add multi-language support
- [ ] Create backup/export functionality

---

**Built with ❤️ for better medication management**