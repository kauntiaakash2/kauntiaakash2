# Smart Classroom Timetable Scheduler Backend

A comprehensive FastAPI backend for managing smart classroom timetable scheduling with MongoDB integration.

## Features

- **CRUD Operations** for Teachers, Classrooms, Subjects, and Batches
- **Intelligent Timetable Generation** with conflict resolution
- **RESTful API** with comprehensive documentation
- **MongoDB Integration** with async operations
- **JWT Authentication** (MVP implementation)
- **Input Validation** using Pydantic models
- **Error Handling** and logging
- **CORS Support** for web applications

## Project Structure

```
backend/
├── app/
│   ├── models/           # Pydantic data models
│   │   └── __init__.py   # All models (Teacher, Classroom, Subject, Batch, Timetable)
│   ├── routes/           # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication routes
│   │   ├── teachers.py   # Teacher CRUD operations
│   │   ├── classrooms.py # Classroom CRUD operations
│   │   ├── subjects.py   # Subject CRUD operations
│   │   ├── batches.py    # Batch CRUD operations
│   │   └── timetable.py  # Timetable generation
│   ├── utils/            # Utility modules
│   │   ├── __init__.py
│   │   ├── database.py   # MongoDB connection and utilities
│   │   ├── auth.py       # JWT authentication utilities
│   │   └── timetable.py  # Timetable generation algorithms
│   ├── __init__.py
│   └── config.py         # Configuration settings
├── .env                  # Environment variables
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud instance)
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Copy the `.env` file and update with your settings:
   ```bash
   cp .env .env.local  # Optional: create local copy
   ```
   
   Update the following variables in `.env`:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=classroom_scheduler
   SECRET_KEY=your-super-secret-jwt-key
   ```

5. **Start MongoDB**
   Ensure MongoDB is running on your system or update the `MONGODB_URL` to point to your MongoDB instance.

6. **Run the application**
   ```bash
   python main.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Teachers
- `POST /api/v1/teachers` - Create a new teacher
- `GET /api/v1/teachers` - Get all teachers (with pagination)
- `GET /api/v1/teachers/{id}` - Get teacher by ID
- `PUT /api/v1/teachers/{id}` - Update teacher
- `DELETE /api/v1/teachers/{id}` - Delete teacher

### Classrooms
- `POST /api/v1/classrooms` - Create a new classroom
- `GET /api/v1/classrooms` - Get all classrooms
- `GET /api/v1/classrooms/{id}` - Get classroom by ID
- `PUT /api/v1/classrooms/{id}` - Update classroom
- `DELETE /api/v1/classrooms/{id}` - Delete classroom

### Subjects
- `POST /api/v1/subjects` - Create a new subject
- `GET /api/v1/subjects` - Get all subjects
- `GET /api/v1/subjects/{id}` - Get subject by ID
- `PUT /api/v1/subjects/{id}` - Update subject
- `DELETE /api/v1/subjects/{id}` - Delete subject

### Batches
- `POST /api/v1/batches` - Create a new batch
- `GET /api/v1/batches` - Get all batches
- `GET /api/v1/batches/{id}` - Get batch by ID
- `PUT /api/v1/batches/{id}` - Update batch
- `DELETE /api/v1/batches/{id}` - Delete batch

### Timetable
- `POST /api/v1/timetable/generate-timetable` - Generate optimized timetable
- `GET /api/v1/timetable/health` - Timetable service health check

## Usage Examples

### 1. Authentication
```bash
# Login to get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### 2. Create a Teacher
```bash
curl -X POST "http://localhost:8000/api/v1/teachers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Dr. John Smith",
    "max_classes_per_day": 6,
    "leave_count": 0,
    "subjects": []
  }'
```

### 3. Create a Subject
```bash
curl -X POST "http://localhost:8000/api/v1/subjects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Mathematics",
    "classes_per_week": 5,
    "duration_per_class": 60,
    "assigned_teachers": []
  }'
```

### 4. Generate Timetable
```bash
curl -X POST "http://localhost:8000/api/v1/timetable/generate-timetable" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "batch_ids": ["batch_id_1", "batch_id_2"],
    "start_date": "2024-01-15",
    "end_date": "2024-01-19",
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "start_time": "09:00",
    "end_time": "17:00",
    "break_duration": 60
  }'
```

## Data Models

### Teacher
- `name`: Teacher's full name
- `max_classes_per_day`: Maximum classes per day (1-8)
- `leave_count`: Number of leave days
- `subjects`: List of subject IDs the teacher can teach

### Classroom
- `room_number`: Unique room identifier
- `capacity`: Maximum student capacity
- `section`: Section/wing of the building

### Subject
- `name`: Subject name
- `classes_per_week`: Required classes per week
- `duration_per_class`: Duration in minutes (30-180)
- `assigned_teachers`: List of teacher IDs

### Batch
- `name`: Batch name/identifier
- `subjects`: List of subject IDs for this batch
- `sections`: List of section names

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `classroom_scheduler` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` |

## Deployment

### Docker Deployment (Recommended)

1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Build and run**:
```bash
docker build -t classroom-scheduler .
docker run -p 8000:8000 --env-file .env classroom-scheduler
```

### Cloud Deployment

#### Heroku
1. Install Heroku CLI
2. Create Procfile: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy: `git push heroku main`

#### AWS EC2
1. Launch EC2 instance
2. Install Python and dependencies
3. Configure reverse proxy (nginx)
4. Use PM2 or systemd for process management

## Development

### Running in Development Mode
```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py
python main.py
```

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints
- Add docstrings to functions and classes
- Write tests for new features

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check the `MONGODB_URL` in `.env`
   - Verify network connectivity

2. **Import Errors**
   - Activate virtual environment
   - Install requirements: `pip install -r requirements.txt`

3. **Authentication Errors**
   - Check JWT secret key configuration
   - Verify token format in requests

4. **Port Already in Use**
   - Change port in `.env` file
   - Kill process using the port: `lsof -ti:8000 | xargs kill -9`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the repository or contact the development team.