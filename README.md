# CineQuest - Movie Discovery Platform

![CineQuest Badge](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Node.js](https://img.shields.io/badge/Node.js-18+-green)
![Django](https://img.shields.io/badge/Django-5.0+-darkred)
![Next.js](https://img.shields.io/badge/Next.js-14+-black)

CineQuest is a modern cinematic movie discovery platform that leverages the TMDB (The Movie Database) API to provide users with personalized movie recommendations, intelligent search, mood-based discovery, and comprehensive movie information including trailers and comparisons.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Innovation Feature: Mood-Based Movie Discovery](#innovation-feature-mood-based-movie-discovery)
- [Team Members](#team-members)
- [License](#license)

## Project Overview

CineQuest is a full-stack web application built with:

- **Backend:** Django REST Framework with Python
- **Frontend:** Next.js with TypeScript
- **Database:** PostgreSQL (recommended) / SQLite (development)
- **External API:** The Movie Database (TMDB) API v3

The platform addresses the challenge of movie discovery by providing multiple pathways for users to find movies that match their preferences, mood, and interests.

## Features

- **Movie Search** - Search the entire TMDB movie database with advanced filtering
- **Mood-Based Recommendations** - Discover movies based on your current mood (10 preset moods with intelligent genre mapping)
- **Trending Movies** - Real-time trending movies data
- **Now Playing** - Currently showing movies in theaters
- **Top Rated** - Critically acclaimed and highly-rated movies
- **Watchlist Management** - Save and manage your personal watchlist
- **Movie Comparison** - Compare multiple movies side-by-side
- **Trailer Playback** - Integrated trailer viewing
- **Personalized Recommendations** - AI-driven suggestions based on viewing history
- **Responsive Design** - Fully responsive frontend for all devices

## Architecture Overview

### Backend Structure

The Django backend is organized into modular applications:

```
Backend (Django)
├── movies/          # Movie database, TMDB sync, search endpoints
├── users/           # User profiles and authentication
├── recommendations/ # Recommendation engine and mood-based discovery
├── api/             # API routing and versioning
└── core/            # Settings, middleware, utilities
```

### Frontend Structure

```
Frontend (Next.js + TypeScript)
├── pages/           # Route components
├── components/      # Reusable UI components
├── hooks/           # Custom React hooks
├── services/        # API client
├── types/           # TypeScript interfaces
└── styles/          # CSS modules and styling
```

### Data Flow

1. User interacts with Next.js frontend
2. Frontend calls Django REST API endpoints
3. Django fetches/processes data from TMDB API
4. Data is stored in local database for caching
5. Response returned as JSON to frontend
6. Frontend renders data in interactive UI

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **Node.js 18 or higher**
- **npm 9 or higher**
- **git**
- **pip** (Python package manager)
- **A TMDB API key** (free registration at [themoviedb.org](https://www.themoviedb.org/))

## Backend Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Software-Construction-Exam-Project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the backend directory. Reference `.env.example` for required variables:

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your TMDB API key
nano .env  # or your preferred editor
```

Required variables in `.env`:
- `TMDB_API_KEY` - Your API key from TMDB
- `SECRET_KEY` - Django secret key (will be generated if missing)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - Database connection string (optional)

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Sync Movies from TMDB

```bash
# Populate initial movie data from TMDB
python manage.py sync_movies
```

### Step 7: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 8: Start Development Server

```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Step 4: Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run start
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/movies/` | List all movies with pagination |
| GET | `/api/movies/{id}/` | Get movie details |
| POST | `/api/movies/search/` | Search movies by title/keyword |
| GET | `/api/movies/trending/` | Get trending movies |
| GET | `/api/movies/now-playing/` | Get movies currently in theaters |
| GET | `/api/movies/top-rated/` | Get top-rated movies |
| GET | `/api/recommendations/mood-list/` | Get available mood presets |
| GET | `/api/recommendations/mood-movies/?mood=happy` | Get movies for specific mood |
| GET | `/api/recommendations/personalized/` | Get personalized recommendations |
| GET | `/api/movies/{id}/compare/` | Compare movie |
| POST | `/api/watchlist/` | Add movie to watchlist |
| GET | `/api/watchlist/` | Get user's watchlist |
| DELETE | `/api/watchlist/{id}/` | Remove from watchlist |
| GET | `/api/users/profile/` | Get user profile |
| POST | `/api/users/profile/` | Update user profile |

## Project Structure

```
Software-Construction-Exam-Project/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── middleware/
│   ├── movies/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── management/commands/
│   │   │   └── sync_movies.py
│   │   └── tests.py
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── recommendations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── mood_mapping.py
│   │   └── engine.py
│   └── api/
│       └── urls.py
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── .env.local
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── search.tsx
│   │   ├── movies/[id].tsx
│   │   ├── mood.tsx
│   │   ├── watchlist.tsx
│   │   └── compare.tsx
│   ├── components/
│   │   ├── Layout.tsx
│   │   ├── MovieCard.tsx
│   │   ├── SearchBar.tsx
│   │   ├── MoodSelector.tsx
│   │   └── TrailerPlayer.tsx
│   ├── hooks/
│   │   ├── useMovies.ts
│   │   ├── useMoods.ts
│   │   └── useWatchlist.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   └── styles/
│       └── globals.css
├── docs/
│   └── TECHNICAL_REPORT.md
├── README.md
└── LICENSE
```

## Environment Variables

### Backend (.env)

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# TMDB API
TMDB_API_KEY=your_tmdb_api_key_here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (.env.local)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Testing

### Backend Testing

Run all backend tests:

```bash
python manage.py test movies
python manage.py test users
python manage.py test recommendations
```

Run specific test:

```bash
python manage.py test movies.tests.MovieModelTest
```

Generate coverage report:

```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Testing

Run frontend tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm test -- --watch
```

Generate coverage report:

```bash
npm test -- --coverage
```

## Innovation Feature: Mood-Based Movie Discovery

### Problem Statement

Movie selection paralysis is a common problem - users face decision fatigue when choosing what to watch. Traditional recommendation systems rely on viewing history, which is not always available for new users and doesn't account for the user's current emotional state.

### Solution Overview

CineQuest introduces **Mood-Based Movie Discovery**, which maps emotional states to carefully curated movie selections. The system includes:

- **10 Mood Presets:** Happy, Sad, Thrilled, Relaxed, Inspired, Scared, Angry, Romantic, Thoughtful, Energetic
- **Intelligent Genre Mapping:** Each mood is mapped to genres and filters that enhance the emotional experience
- **Real-time Curation:** Movies are fetched from TMDB and filtered based on mood parameters
- **User-Friendly Interface:** Emoji-styled mood buttons for intuitive selection

### Technical Implementation

**Backend (mood_mapping.py):**

```python
MOOD_MAP = {
    'happy': {
        'genres': ['Comedy', 'Family', 'Animation'],
        'sort_by': 'popularity.desc',
        'min_rating': 6.0
    },
    # ... other moods
}
```

**Endpoints:**
- `GET /api/recommendations/mood-list/` - Returns available moods
- `GET /api/recommendations/mood-movies/?mood=happy` - Returns curated movies

**Frontend:**
- Dedicated mood selection page with emoji buttons
- Results displayed in an engaging grid format
- Seamless integration with watchlist

## Team Members

| ID | Name | Role |
|----|----|------|
| 1 | Team Member 1 | Full Stack Developer |
| 2 | Team Member 2 | Backend Developer |
| 3 | Team Member 3 | Frontend Developer |
| 4 | Team Member 4 | UI/UX Designer |
| 5 | Team Member 5 | Database Manager |
| 6 | Team Member 6 | API Integration Specialist |
| 7 | Team Member 7 | QA/Testing Engineer |
| 8 | Team Member 8 | DevOps Engineer |
| 9 | Team Member 9 | Documentation Specialist |
| 10 | Team Member 10 | Project Manager |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**For detailed technical information, bugs found and fixed, and architectural decisions, please refer to [TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md).**