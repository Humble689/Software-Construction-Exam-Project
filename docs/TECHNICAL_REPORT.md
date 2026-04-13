# CineQuest - Technical Report
## Software Construction Final Year Project

**Date:** April 2026
**Project:** CineQuest - Movie Discovery Platform
**Team Size:** 10 Members
**Technology Stack:** Django REST Framework + Next.js with TypeScript

---

## Executive Summary

CineQuest is a comprehensive full-stack movie discovery platform developed as a final year software construction project. The platform integrates with The Movie Database (TMDB) API to provide users with intelligent movie recommendations, mood-based discovery, watchlist management, and movie comparison features. During the development and testing phases, 11 critical and medium-severity bugs were identified and systematically resolved. This report documents the bug analysis, refactoring decisions, architectural approach, and the innovative mood-based discovery feature that differentiates CineQuest from conventional movie platforms.

The project demonstrates sound software engineering practices including proper separation of concerns between frontend and backend, comprehensive error handling, and user-centric feature design. The mood-based discovery feature represents a novel approach to addressing decision paralysis in media selection, addressing a real user pain point through emotional context awareness rather than purely algorithmic recommendation.

---

## Bug Analysis & Fixes

During development and testing, 11 bugs were identified across the backend and frontend. Each bug has been documented with analysis, impact assessment, and the implemented fix.

### Bug #1: App Name Typo in INSTALLED_APPS

**Severity:** Critical - Django crash on startup

**Location:** `backend/core/settings.py`

**Problem:**
The INSTALLED_APPS configuration contained a typo with the movie app listed as `'movie'` instead of `'movies'`:

```python
# BEFORE (Broken)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'movie',  # WRONG - should be 'movies'
    'users',
    'recommendations',
]
```

**Impact:** Django failed to start with a ModuleNotFoundError, making the entire backend inaccessible.

**Root Cause:** Typo during initial setup - the actual app directory is named `movies/` but the configuration referenced `movie`.

**Solution:**

```python
# AFTER (Fixed)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'movies',  # CORRECT
    'users',
    'recommendations',
]
```

**Resolution:** Changed app name from `'movie'` to `'movies'` to match the actual application directory. This is a lesson in consistency - app names must match their directory names.

---

### Bug #2: Missing CorsMiddleware

**Severity:** Critical - Frontend blocked from accessing backend

**Location:** `backend/core/settings.py`

**Problem:**
CorsMiddleware was completely missing from the MIDDLEWARE configuration, causing cross-origin requests from the Next.js frontend to be blocked:

```python
# BEFORE (Broken)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # CorsMiddleware missing!
]
```

**Impact:** Frontend requests to the API received CORS (Cross-Origin Resource Sharing) errors, making all API calls fail even though the endpoints existed.

**Root Cause:** CorsMiddleware was not added during initial Django setup. This is common in development when CORS is temporarily ignored.

**Solution:**

```python
# AFTER (Fixed)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ADDED - must be early in stack
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

**Key Consideration:** CorsMiddleware must appear before CommonMiddleware in the MIDDLEWARE list to function properly.

---

### Bug #3: Insufficient max_length for Movie Title Field

**Severity:** High - Runtime crashes for long movie titles

**Location:** `backend/movies/models.py`

**Problem:**
The Movie model's title field had a maximum length of 50 characters, which is insufficient for many real movie titles:

```python
# BEFORE (Broken)
class Movie(models.Model):
    title = models.CharField(max_length=50)  # TOO SHORT!
    description = models.TextField()
    release_date = models.DateField()
    rating = models.FloatField()
```

**Impact:** Movies with titles longer than 50 characters would fail to save, causing data integrity issues and sync failures from TMDB.

**Root Cause:** During initial model design, max_length was set to an arbitrary value without analyzing typical movie title lengths. Titles like "The Chronicles of Narnia: The Lion, the Witch and the Wardrobe" exceed 50 characters.

**Solution:**

```python
# AFTER (Fixed)
class Movie(models.Model):
    title = models.CharField(max_length=500)  # INCREASED - accommodates lengthy titles
    description = models.TextField()
    release_date = models.DateField()
    rating = models.FloatField()
```

**Migration Required:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Best Practice:** When designing CharField constraints, research typical data lengths and add reasonable buffer (10-20% extra).

---

### Bug #4: Hardcoded SECRET_KEY

**Severity:** Critical - Security vulnerability

**Location:** `backend/core/settings.py`

**Problem:**
The Django SECRET_KEY was hardcoded in the settings file instead of using environment variables:

```python
# BEFORE (Broken - SECURITY RISK)
SECRET_KEY = 'django-insecure-abc123xyz456...'  # EXPOSED
DEBUG = True
```

**Impact:**
- Security vulnerability - the key was exposed in version control
- Same key used across development, staging, and production
- If compromised, all sessions and tokens become vulnerable

**Root Cause:** Convenience during initial development - hardcoding is faster than setting environment variables.

**Solution:**

```python
# AFTER (Fixed - SECURE)
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

**.env file:**
```env
SECRET_KEY=your-super-secret-key-generated-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,127.0.0.1:8000
```

**Preventive Measure:** Use the `python-decouple` package to manage all environment-specific settings. Never commit sensitive data to version control.

---

### Bug #5: Wrong HTTP Methods for Search and Trending Endpoints

**Severity:** High - Frontend requests fail with 405 errors

**Location:** `backend/movies/urls.py` and `backend/movies/views.py`

**Problem:**
The search_movies and trending_movies endpoints were configured to accept POST requests when they should accept GET:

```python
# BEFORE (Broken)
@api_view(['POST'])  # WRONG - should be GET
def search_movies(request):
    query = request.data.get('query')  # POST body
    # ...

@api_view(['POST'])  # WRONG - should be GET
def trending_movies(request):
    time_window = request.data.get('time_window')  # POST body
    # ...
```

**Impact:** Frontend JavaScript/TypeScript code making GET requests received 405 Method Not Allowed errors.

**Root Cause:** Confusion about HTTP semantics. Fetching/retrieving data should use GET; modifications should use POST/PUT/DELETE.

**Solution:**

```python
# AFTER (Fixed)
@api_view(['GET'])  # CORRECT
def search_movies(request):
    query = request.query_params.get('query')  # GET query string
    results = Movie.objects.filter(title__icontains=query)
    serializer = MovieSerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])  # CORRECT
def trending_movies(request):
    time_window = request.query_params.get('time_window', 'week')
    # Fetch trending data from cache or TMDB
    # ...
    return Response(data)
```

**URL configuration:**
```python
urlpatterns = [
    path('search/', search_movies, name='search_movies'),  # GET with ?query=X
    path('trending/', trending_movies, name='trending_movies'),  # GET with ?time_window=X
]
```

**Frontend usage (now works correctly):**
```typescript
// Frontend - now using GET
const response = await fetch(`/api/movies/search/?query=${searchTerm}`, {
    method: 'GET'
});
```

---

### Bug #6: Duplicate compare_movies Functions

**Severity:** Medium - Code duplication, maintainability issue

**Location:** `backend/movies/views.py`

**Problem:**
Two nearly identical functions existed for comparing movies, violating DRY (Don't Repeat Yourself) principle:

```python
# BEFORE (Broken)
def compare_movies(request, movie1_id, movie2_id):
    """Compare two movies"""
    movie1 = get_object_or_404(Movie, id=movie1_id)
    movie2 = get_object_or_404(Movie, id=movie2_id)
    serializer = MovieComparisonSerializer([movie1, movie2], many=True)
    return Response(serializer.data)

def compare_two_movies(request, movie1_id, movie2_id):
    """Compare two movies (identical to above)"""
    movie1 = get_object_or_404(Movie, id=movie1_id)
    movie2 = get_object_or_404(Movie, id=movie2_id)
    serializer = MovieComparisonSerializer([movie1, movie2], many=True)
    return Response(serializer.data)
```

**Impact:**
- Code maintenance nightmare - bug fixes need to be applied twice
- Confusion for developers about which function to use
- Unnecessary code bloat

**Root Cause:** Accidental duplication during development, or incomplete refactoring.

**Solution:**

```python
# AFTER (Fixed)
@api_view(['GET'])
def compare_movies(request, movie1_id, movie2_id):
    """
    Compare two movies side-by-side.
    Returns detailed information for comparison view.
    """
    movie1 = get_object_or_404(Movie, id=movie1_id)
    movie2 = get_object_or_404(Movie, id=movie2_id)
    serializer = MovieComparisonSerializer([movie1, movie2], many=True)
    return Response({
        'results': serializer.data,
        'comparison_score': calculate_similarity(movie1, movie2)
    })

# Remove compare_two_movies function entirely
```

**URL configuration (simplified):**
```python
urlpatterns = [
    path('compare/<int:movie1_id>/<int:movie2_id>/', compare_movies, name='compare_movies'),
]
```

---

### Bug #7: Cryptic Variable Names in Views

**Severity:** Medium - Code readability and maintainability

**Location:** `backend/movies/views.py`

**Problem:**
Single-letter variable names were used in now_playing and top_rated views, making code difficult to understand:

```python
# BEFORE (Broken - Poor readability)
def now_playing(request):
    p = request.GET.get('page', 1)  # What is 'p'?
    d = Movie.objects.filter(now_playing=True)
    s = 20
    start = (int(p) - 1) * s
    end = start + s
    r = d[start:end]  # What is 'r'?
    x = MovieSerializer(r, many=True)
    return Response(x.data)

def top_rated(request):
    p = request.GET.get('page', 1)
    d = Movie.objects.filter(rating__gte=8.0)
    s = 20
    start = (int(p) - 1) * s
    end = start + s
    r = d[start:end]
    x = MovieSerializer(r, many=True)
    return Response(x.data)
```

**Impact:**
- Difficult for other developers to understand code
- Higher bug introduction risk during maintenance
- Reduced code review effectiveness

**Root Cause:** Lazy variable naming - developers prioritized speed over clarity.

**Solution:**

```python
# AFTER (Fixed - Clear naming)
@api_view(['GET'])
def now_playing(request):
    """Get movies currently playing in theaters with pagination."""
    page_number = request.GET.get('page', 1)
    movies_queryset = Movie.objects.filter(now_playing=True).order_by('-release_date')
    page_size = 20

    start_index = (int(page_number) - 1) * page_size
    end_index = start_index + page_size
    paginated_movies = movies_queryset[start_index:end_index]

    serializer = MovieSerializer(paginated_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def top_rated(request):
    """Get top-rated movies with pagination."""
    page_number = request.GET.get('page', 1)
    movies_queryset = Movie.objects.filter(rating__gte=8.0).order_by('-rating')
    page_size = 20

    start_index = (int(page_number) - 1) * page_size
    end_index = start_index + page_size
    paginated_movies = movies_queryset[start_index:end_index]

    serializer = MovieSerializer(paginated_movies, many=True)
    return Response(serializer.data)
```

**Alternative (Even Better - Using DRF Pagination):**

```python
from rest_framework.pagination import PageNumberPagination

class MoviePagination(PageNumberPagination):
    page_size = 20

@api_view(['GET'])
def now_playing(request):
    """Get movies currently playing in theaters."""
    movies = Movie.objects.filter(now_playing=True).order_by('-release_date')
    paginator = MoviePagination()
    paginated_movies = paginator.paginate_queryset(movies, request)
    serializer = MovieSerializer(paginated_movies, many=True)
    return paginator.get_paginated_response(serializer.data)
```

**Best Practice:** Use meaningful variable names that clearly indicate purpose and type.

---

### Bug #8: Missing .env File

**Severity:** High - Default configuration issues

**Location:** `backend/` (root)

**Problem:**
No `.env` file existed, causing TMDB_API_KEY to default to empty string:

```python
# BEFORE (Broken)
# In settings.py
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')  # Defaults to empty!
```

**Impact:**
- All TMDB API calls failed silently with authentication errors
- Movie sync failed
- Users couldn't see movie data

**Root Cause:** `.env` file was in `.gitignore` (correct), but no `.env.example` template provided for reference.

**Solution:**

**Create `.env.example` (template - checked into git):**
```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# TMDB API
TMDB_API_KEY=your_tmdb_api_key_here

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Setup instructions in README:**
```bash
# Copy example and fill in values
cp .env.example .env
nano .env  # Edit with your actual credentials
```

**Updated settings.py:**
```python
from decouple import config

TMDB_API_KEY = config('TMDB_API_KEY')  # Will error if missing - which is correct!
```

**This way:**
- `.env` is in `.gitignore` (never committed)
- `.env.example` shows required variables
- Developers get clear error if they forget to create `.env`

---

### Bug #9: Unused dj_database_url Import

**Severity:** Low - Code cleanliness

**Location:** `backend/core/settings.py`

**Problem:**
An unused import was left in the settings file:

```python
# BEFORE (Broken - code smell)
import dj_database_url  # Imported but never used
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Impact:**
- Unnecessary dependency in requirements.txt
- Confuses developers about database configuration
- Adds to code bloat

**Root Cause:** Library was imported during development for potential use but ultimately not needed.

**Solution:**

```python
# AFTER (Fixed)
# Removed: import dj_database_url
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Also update requirements.txt** to remove dj-database-url if it's not used elsewhere.

---

### Bug #10: Frontend Trending State Type Mismatch

**Severity:** High - TypeScript compilation error, runtime crashes

**Location:** `frontend/src/pages/index.tsx`

**Problem:**
The trending state was initialized as an empty object `{}` but the component expected an array `MovieCompact[]`:

```typescript
// BEFORE (Broken)
import { useState } from 'react';
import { MovieCompact } from '@/types';

export default function Home() {
  const [trending, setTrending] = useState({});  // WRONG - should be array!

  // HeroSection tries to use trending as array
  return (
    <HeroSection
      movies={trending}  // Type error!
    />
  );
}

// HeroSection component expects array
interface HeroSectionProps {
  movies: MovieCompact[];  // Array type
}

export function HeroSection({ movies }: HeroSectionProps) {
  return (
    <div>
      {movies.map((movie) => (  // Crash - can't map over object
        <MovieCard key={movie.id} movie={movie} />
      ))}
    </div>
  );
}
```

**Impact:**
- TypeScript compiler error
- Runtime crash: "movies.map is not a function"
- Page fails to load

**Root Cause:** Inconsistent initialization of state with component prop requirements.

**Solution:**

```typescript
// AFTER (Fixed)
import { useState, useEffect } from 'react';
import { MovieCompact } from '@/types';

export default function Home() {
  const [trending, setTrending] = useState<MovieCompact[]>([]);  // CORRECT - empty array

  useEffect(() => {
    fetchTrendingMovies();
  }, []);

  const fetchTrendingMovies = async () => {
    try {
      const response = await fetch('/api/movies/trending/');
      const data = await response.json();
      setTrending(data.results || []);
    } catch (error) {
      console.error('Failed to fetch trending movies:', error);
      setTrending([]);
    }
  };

  return (
    <HeroSection movies={trending} />
  );
}
```

**Type Definition (TypeScript):**
```typescript
// In types/index.ts
export interface MovieCompact {
  id: number;
  title: string;
  poster_path: string;
  rating: number;
}
```

**Best Practice:** Always initialize state with the correct type that matches component prop expectations.

---

### Bug #11: Missing WatchlistItem TypeScript Interface

**Severity:** High - TypeScript compilation error

**Location:** `frontend/src/types/index.ts`

**Problem:**
The WatchlistItem type was used in components but not defined, causing TypeScript compilation errors:

```typescript
// BEFORE (Broken)
// In useWatchlist hook:
import { WatchlistItem } from '@/types';  // DOESN'T EXIST!

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);  // Type error
  // ...
}
```

**Impact:**
- TypeScript compiler error: "Cannot find module '@/types' or its corresponding type declarations"
- Build fails
- Development cannot proceed

**Root Cause:** Type definition was not created, likely due to incomplete implementation.

**Solution:**

```typescript
// AFTER (Fixed)
// In types/index.ts

export interface MovieCompact {
  id: number;
  title: string;
  poster_path: string;
  rating: number;
}

export interface MovieDetail extends MovieCompact {
  description: string;
  release_date: string;
  runtime: number;
  genres: string[];
  director: string;
  cast: string[];
}

export interface WatchlistItem {
  id: number;
  movie: MovieCompact;
  added_date: string;
  watched: boolean;
  rating?: number;
}

export interface APIResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

**Updated useWatchlist hook:**
```typescript
import { useState, useEffect } from 'react';
import { WatchlistItem } from '@/types';

export function useWatchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/watchlist/');
      const data = await response.json();
      setWatchlist(data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  return { watchlist, isLoading, error, refetch: fetchWatchlist };
}
```

**Best Practice:** Define all types/interfaces before using them. Create a comprehensive `types/index.ts` file that serves as the single source of truth for all TypeScript types.

---

## Refactoring Decisions

Beyond bug fixes, several refactoring improvements were made to enhance code quality:

### 1. Removed Duplicate compare_movies Function
Consolidated two identical comparison functions into a single, well-documented version with improved error handling and additional comparison metrics.

### 2. Renamed All Cryptic Variables
Applied meaningful naming conventions throughout the codebase:
- `p` → `page_number`
- `d` → `movies_queryset` or `database_query`
- `r` → `paginated_movies` or `results`
- `s` → `page_size`
- `x` → `serializer` or `serialized_data`

### 3. Added Comprehensive Docstrings
Updated all API views with detailed docstrings explaining purpose, parameters, and return values:

```python
@api_view(['GET'])
def now_playing(request):
    """
    Retrieve movies currently playing in theaters.

    Query Parameters:
        page (int): Page number for pagination (default: 1)

    Returns:
        Response: Paginated list of movie objects with pagination metadata

    Status Codes:
        200: Success
        400: Invalid page parameter
    """
```

### 4. Improved Error Status Codes
Replaced generic 200 OK responses with appropriate HTTP status codes:

```python
# BEFORE - always returns 200
if not user:
    return Response({'error': 'Not found'})  # Still 200!

# AFTER - proper status codes
from rest_framework import status

if not user:
    return Response(
        {'error': 'User not found'},
        status=status.HTTP_404_NOT_FOUND
    )
```

### 5. Extracted Magic Numbers to Constants
Moved hardcoded values to named constants:

```python
# BEFORE
paginate_queryset = movies[0:20]

# AFTER
PAGE_SIZE = 20
MINIMUM_RATING = 6.0
TMDB_REQUEST_TIMEOUT = 10

movies_page = movies[:PAGE_SIZE]
```

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Client                       │
│              (Next.js with TypeScript)                    │
├─────────────────────────────────────────────────────────┤
│  Pages: Home, Search, MovieDetail, Mood, Watchlist, etc  │
│  Components: MovieCard, SearchBar, MoodSelector          │
│  Services: API client with axios/fetch                   │
│  State: React Context + hooks (useMovies, useMoods)      │
└──────────────────┬──────────────────────────────────────┘
                   │ REST API calls
                   │ (JSON over HTTP)
┌──────────────────┴──────────────────────────────────────┐
│           Django REST Framework Backend                   │
│                   API Layer                               │
├─────────────────────────────────────────────────────────┤
│  Movies App                                               │
│  ├── Models: Movie, Genre, Review                        │
│  ├── Views: search_movies, trending, now_playing         │
│  ├── Serializers: MovieSerializer, MovieDetailSerializer │
│  └── Services: TMDB API integration                      │
│                                                           │
│  Users App                                                │
│  ├── Models: User, UserProfile, Preferences             │
│  ├── Views: user_profile, update_profile                │
│  └── Serializers: UserSerializer, ProfileSerializer     │
│                                                           │
│  Recommendations App                                      │
│  ├── Models: Recommendation, WatchlistItem              │
│  ├── Views: mood_list, mood_movies, personalized        │
│  ├── Mood Mapping: 10 mood presets                      │
│  └── Engine: Recommendation algorithm                    │
├─────────────────────────────────────────────────────────┤
│                    Business Logic                         │
│  ├── TMDB API Integration Service                        │
│  ├── Recommendation Engine                               │
│  ├── Mood-to-Genre Mapper                                │
│  └── Caching Layer                                       │
└──────────────────┬──────────────────────────────────────┘
                   │ Database queries
┌──────────────────┴──────────────────────────────────────┐
│                   PostgreSQL / SQLite                     │
│                     Database Layer                        │
├─────────────────────────────────────────────────────────┤
│  ├── movies_movie (Movie data from TMDB)                 │
│  ├── movies_genre (Genre information)                    │
│  ├── users_userprofile (User preferences)                │
│  ├── recommendations_watchlistitem (User watchlists)     │
│  └── recommendations_recommendation (AI recommendations) │
└─────────────────────────────────────────────────────────┘
                   │ External API calls
                   │
┌──────────────────┴──────────────────────────────────────┐
│         The Movie Database (TMDB) API                     │
│                                                           │
│  ├── /trending (Popular movies by time window)           │
│  ├── /now_playing (Currently in theaters)                │
│  ├── /top_rated (Best-rated movies)                      │
│  ├── /search (Movie search by title)                     │
│  └── /movie/{id} (Movie details with cast, crew)         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Example: User Searches for Movies

1. **Frontend:** User types "Inception" in search bar and presses enter
2. **Frontend:** JavaScript sends GET request to `/api/movies/search/?query=Inception`
3. **Backend:** Django URL router matches route to `search_movies` view
4. **Backend:** View extracts query parameter and filters Movie model
5. **Backend:** MovieSerializer converts movie objects to JSON
6. **Backend:** Returns JSON response with matching movies
7. **Frontend:** JavaScript receives JSON response
8. **Frontend:** React re-renders SearchResults component with new movie data
9. **User:** Sees search results displayed in grid format

### Data Flow Example: User Selects a Mood

1. **Frontend:** User clicks "Happy" mood button on mood selection page
2. **Frontend:** JavaScript sends GET request to `/api/recommendations/mood-movies/?mood=happy`
3. **Backend:** Recommendations service receives mood parameter
4. **Backend:** mood_mapping.py looks up genre and filter configuration for "happy"
5. **Backend:** Queries Movie model for movies matching genres/criteria
6. **Backend:** Returns curated list of 20-30 happy movies
7. **Frontend:** Receives JSON response with movie array
8. **Frontend:** Renders movies in appealing grid with mood-appropriate styling
9. **User:** Browses curated happy movies, can add to watchlist

---

## Innovation Feature: Mood-Based Movie Discovery

### Problem Statement

Traditional movie discovery relies on several flawed approaches:
- **Algorithm-based:** Requires extensive viewing history (not useful for new users)
- **Manual search:** Requires users to know what they want to watch
- **Browse trending:** Shows only popular content, not necessarily what fits the mood
- **Genre filtering:** Too technical and doesn't account for emotional state

Users often experience "decision paralysis" - they spend 20+ minutes browsing without finding something satisfying. This happens because movie platforms ignore the user's current emotional state.

### Solution: Mood-Based Discovery

CineQuest introduces an emotional intelligence layer to movie discovery. Rather than purely algorithmic recommendations, the system maps emotional states (moods) to movie selections that enhance or match those emotions.

**Core Concept:**
```
User Mood → Genre/Filter Mapping → Movie Query → Curated Results
  ↓
"Happy" → Comedy, Family, Animation → Filter by rating 6.0+ → 25 results
```

### Technical Architecture

#### Backend Implementation

**Mood Mapping (mood_mapping.py):**

```python
MOOD_MAP = {
    'happy': {
        'genres': ['Comedy', 'Family', 'Animation'],
        'keywords': ['funny', 'uplifting', 'feel-good'],
        'sort_by': 'popularity.desc',
        'min_rating': 6.0,
        'exclude_genres': ['Horror', 'Thriller'],
        'description': 'Feel-good movies to lift your spirits'
    },
    'sad': {
        'genres': ['Drama'],
        'keywords': ['emotional', 'touching', 'heartwarming'],
        'sort_by': 'rating.desc',
        'min_rating': 7.0,
        'exclude_genres': [],
        'description': 'Emotional dramas to process feelings'
    },
    'thrilled': {
        'genres': ['Action', 'Adventure', 'Thriller'],
        'keywords': ['exciting', 'intense', 'adrenaline'],
        'sort_by': 'popularity.desc',
        'min_rating': 6.5,
        'exclude_genres': [],
        'description': 'Action-packed movies for adrenaline rush'
    },
    'relaxed': {
        'genres': ['Comedy', 'Animation', 'Family'],
        'keywords': ['lighthearted', 'peaceful', 'calm'],
        'sort_by': 'rating.desc',
        'min_rating': 6.0,
        'exclude_genres': ['Horror', 'Thriller', 'War'],
        'description': 'Calm, easygoing movies for relaxation'
    },
    'inspired': {
        'genres': ['Drama', 'Biography'],
        'keywords': ['inspiring', 'motivational', 'success'],
        'sort_by': 'rating.desc',
        'min_rating': 7.0,
        'exclude_genres': [],
        'description': 'Inspiring stories to motivate you'
    },
    'scared': {
        'genres': ['Horror', 'Thriller'],
        'keywords': ['suspenseful', 'scary', 'creepy'],
        'sort_by': 'rating.desc',
        'min_rating': 6.0,
        'exclude_genres': [],
        'description': 'Thrilling movies for the brave'
    },
    'angry': {
        'genres': ['Action', 'Thriller', 'Crime'],
        'keywords': ['intense', 'powerful', 'revenge'],
        'sort_by': 'rating.desc',
        'min_rating': 6.5,
        'exclude_genres': [],
        'description': 'Intense movies to channel emotions'
    },
    'romantic': {
        'genres': ['Romance', 'Comedy', 'Drama'],
        'keywords': ['love', 'romance', 'passionate'],
        'sort_by': 'rating.desc',
        'min_rating': 6.5,
        'exclude_genres': ['Horror'],
        'description': 'Romantic movies for the heart'
    },
    'thoughtful': {
        'genres': ['Drama', 'Sci-Fi', 'Thriller'],
        'keywords': ['philosophical', 'intellectual', 'complex'],
        'sort_by': 'rating.desc',
        'min_rating': 7.0,
        'exclude_genres': [],
        'description': 'Thought-provoking films for reflection'
    },
    'energetic': {
        'genres': ['Action', 'Adventure', 'Animation', 'Comedy'],
        'keywords': ['fun', 'exciting', 'dynamic'],
        'sort_by': 'popularity.desc',
        'min_rating': 6.0,
        'exclude_genres': [],
        'description': 'High-energy movies to get pumped up'
    }
}
```

**API Views:**

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

@api_view(['GET'])
def mood_list(request):
    """
    Get list of available moods for discovery.

    Returns a list of mood presets with descriptions and emoji.
    No query parameters required.
    """
    mood_presets = [
        {'key': 'happy', 'label': 'Happy', 'emoji': '😊'},
        {'key': 'sad', 'label': 'Sad', 'emoji': '😢'},
        {'key': 'thrilled', 'label': 'Thrilled', 'emoji': '😲'},
        {'key': 'relaxed', 'label': 'Relaxed', 'emoji': '😌'},
        {'key': 'inspired', 'label': 'Inspired', 'emoji': '🤩'},
        {'key': 'scared', 'label': 'Scared', 'emoji': '😨'},
        {'key': 'angry', 'label': 'Angry', 'emoji': '😠'},
        {'key': 'romantic', 'label': 'Romantic', 'emoji': '😍'},
        {'key': 'thoughtful', 'label': 'Thoughtful', 'emoji': '🤔'},
        {'key': 'energetic', 'label': 'Energetic', 'emoji': '⚡'},
    ]
    return Response(mood_presets)

@api_view(['GET'])
def mood_movies(request):
    """
    Get movies curated for a specific mood.

    Query Parameters:
        mood (str): Mood key from mood_list (required)
        limit (int): Number of movies to return (default: 20)

    Returns:
        Response: List of movies matching the mood
    """
    mood = request.query_params.get('mood')
    limit = int(request.query_params.get('limit', 20))

    if not mood or mood not in MOOD_MAP:
        return Response(
            {'error': f'Invalid mood. Choose from: {list(MOOD_MAP.keys())}'},
            status=400
        )

    # Check cache first
    cache_key = f'mood_movies_{mood}_{limit}'
    cached_movies = cache.get(cache_key)

    if cached_movies:
        return Response({
            'mood': mood,
            'description': MOOD_MAP[mood]['description'],
            'results': cached_movies,
            'count': len(cached_movies)
        })

    # Get mood parameters
    mood_params = MOOD_MAP[mood]

    # Build query
    queryset = Movie.objects.all()

    # Filter by minimum rating
    queryset = queryset.filter(rating__gte=mood_params['min_rating'])

    # Filter by genres (OR - include if any genre matches)
    from django.db.models import Q
    genre_filter = Q()
    for genre in mood_params['genres']:
        genre_filter |= Q(genres__name=genre)
    queryset = queryset.filter(genre_filter)

    # Exclude unwanted genres
    for exclude_genre in mood_params['exclude_genres']:
        queryset = queryset.exclude(genres__name=exclude_genre)

    # Order by specified criteria
    if 'popularity' in mood_params['sort_by']:
        queryset = queryset.order_by('-popularity')
    else:
        queryset = queryset.order_by('-rating')

    # Limit results
    movies = queryset[:limit]

    # Cache for 1 hour
    serializer = MovieCompactSerializer(movies, many=True)
    cache.set(cache_key, serializer.data, 3600)

    return Response({
        'mood': mood,
        'description': mood_params['description'],
        'results': serializer.data,
        'count': len(serializer.data)
    })
```

#### Frontend Implementation

**Mood Page Component:**

```typescript
// pages/mood.tsx
import { useState, useEffect } from 'react';
import { MovieCompact } from '@/types';

interface MoodOption {
  key: string;
  label: string;
  emoji: string;
}

export default function MoodPage() {
  const [moods, setMoods] = useState<MoodOption[]>([]);
  const [selectedMood, setSelectedMood] = useState<string | null>(null);
  const [movies, setMovies] = useState<MovieCompact[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMoods();
  }, []);

  const fetchMoods = async () => {
    try {
      const response = await fetch('/api/recommendations/mood-list/');
      const data = await response.json();
      setMoods(data);
    } catch (error) {
      console.error('Failed to fetch moods:', error);
    }
  };

  const handleMoodSelect = async (moodKey: string) => {
    setSelectedMood(moodKey);
    setIsLoading(true);

    try {
      const response = await fetch(
        `/api/recommendations/mood-movies/?mood=${moodKey}&limit=30`
      );
      const data = await response.json();
      setMovies(data.results || []);
    } catch (error) {
      console.error('Failed to fetch mood movies:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mood-discovery-page">
      <h1>What's Your Mood?</h1>
      <p>Select a mood and discover movies perfectly matched to your feelings.</p>

      {/* Mood Selection Grid */}
      <div className="mood-grid">
        {moods.map((mood) => (
          <button
            key={mood.key}
            className={`mood-button ${selectedMood === mood.key ? 'active' : ''}`}
            onClick={() => handleMoodSelect(mood.key)}
          >
            <span className="mood-emoji">{mood.emoji}</span>
            <span className="mood-label">{mood.label}</span>
          </button>
        ))}
      </div>

      {/* Results */}
      {isLoading && <p>Loading movies...</p>}

      {selectedMood && !isLoading && movies.length > 0 && (
        <div className="results-section">
          <h2>Movies for your {selectedMood} mood</h2>
          <div className="movies-grid">
            {movies.map((movie) => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Styling:**

```css
.mood-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.mood-button {
  padding: 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.mood-button:hover {
  border-color: #667eea;
  background: #f5f7ff;
  transform: translateY(-2px);
}

.mood-button.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.mood-emoji {
  font-size: 2rem;
}

.mood-label {
  font-weight: 500;
}
```

### How It Enhances User Experience

1. **Eliminates Decision Paralysis:** Instead of browsing endless lists, users select an emotion and get curated results
2. **Personalization:** Acknowledges that movie choice depends on context and emotional state, not just viewing history
3. **Discovery:** Surfaces movies users wouldn't find through algorithmic recommendations
4. **Engagement:** The mood selection interface is intuitive and visually appealing
5. **Accessibility:** Works for new users without viewing history

### Competitive Advantage

While Netflix and other platforms use collaborative filtering and content-based recommendations, CineQuest's emotional intelligence layer is unique:
- Most platforms recommend "because you watched X"
- CineQuest says "based on your current mood, here's what fits"
- This combines best of both approaches: historical context + current emotional state

---

## Testing Strategy

### Backend Testing

**Test Coverage Areas:**

1. **Model Tests** (`movies/tests.py`)
   - Movie model creation with valid/invalid data
   - Cascade deletion of genres
   - Movie queryset filtering

2. **View Tests** (`movies/tests/test_views.py`)
   - Search endpoint returns correct results
   - Trending endpoint pagination works
   - Now playing filters correctly
   - Mood endpoint returns valid mood presets

3. **Serializer Tests** (`movies/tests/test_serializers.py`)
   - MovieSerializer converts models to JSON correctly
   - Nested genre serialization
   - Date field formatting

4. **Integration Tests**
   - Full API request/response cycle
   - TMDB sync command runs without errors
   - Database constraints are enforced

**Test Example:**

```python
from django.test import TestCase
from movies.models import Movie, Genre
from rest_framework.test import APIClient

class MovieSearchTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.genre = Genre.objects.create(name='Comedy')
        self.movie = Movie.objects.create(
            title='The Grand Budapest Hotel',
            description='A comedy-drama film',
            release_date='2014-03-28',
            rating=8.1
        )
        self.movie.genres.add(self.genre)

    def test_search_movies_by_title(self):
        """Test movie search endpoint"""
        response = self.client.get('/api/movies/search/', {'query': 'Budapest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'The Grand Budapest Hotel')

    def test_search_returns_empty_for_nonexistent_movie(self):
        """Test search with no results"""
        response = self.client.get('/api/movies/search/', {'query': 'XyzAbc123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
```

### Frontend Testing

**Test Coverage Areas:**

1. **Component Tests** (React Testing Library)
   - MovieCard renders movie data correctly
   - SearchBar accepts input and submits
   - MoodSelector displays all mood buttons
   - Loading states show/hide appropriately

2. **Hook Tests**
   - useMovies fetches data and updates state
   - useMoods returns mood list
   - useWatchlist adds/removes items

3. **Page Tests**
   - Home page renders hero section
   - Search page shows results
   - Mood page displays mood buttons and results

**Test Example:**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '@/components/SearchBar';

describe('SearchBar Component', () => {
  it('renders search input', () => {
    render(<SearchBar />);
    const input = screen.getByPlaceholderText('Search movies...');
    expect(input).toBeInTheDocument();
  });

  it('submits search when form is submitted', () => {
    const mockOnSearch = jest.fn();
    render(<SearchBar onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText('Search movies...');
    fireEvent.change(input, { target: { value: 'Inception' } });

    const form = screen.getByRole('search');
    fireEvent.submit(form);

    expect(mockOnSearch).toHaveBeenCalledWith('Inception');
  });
});
```

### Test Execution

**Backend:**
```bash
# Run all tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific test module
python manage.py test movies.tests.MovieSearchTestCase
```

**Frontend:**
```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

---

## Limitations & Future Improvements

### Current Limitations

1. **Database:** SQLite not suitable for production
   - Single concurrent connection limitation
   - Recommend PostgreSQL for production deployment

2. **Authentication:** Frontend lacks proper JWT/OAuth implementation
   - Currently no secure session management
   - Would need token-based auth for mobile apps

3. **Deployment:** No CI/CD pipeline
   - Manual testing and deployment
   - No automated testing on commits

4. **Caching:** Basic in-memory cache
   - Not distributed - won't work with multiple servers
   - Should use Redis for scalability

5. **Real-time:** No WebSocket implementation
   - Users don't get live updates on new trending movies
   - Watchlist changes aren't synchronized

### Future Improvements

1. **Collaborative Filtering**
   - Analyze user watchlists and ratings
   - Recommend based on similar users
   - "Users who watched X also watched Y"

2. **Advanced Mood Mapping**
   - Machine learning to improve genre/mood associations
   - User feedback to refine recommendations
   - Time-based moods (morning vs. night recommendations)

3. **Social Features**
   - User profiles and follow system
   - Share watchlists with friends
   - Group recommendations for watch parties

4. **Real-time Notifications**
   - When movies in watchlist are released
   - When friends add movies to shared lists
   - Price drop notifications for streaming services

5. **Enhanced Analytics**
   - Dashboard showing viewing patterns
   - Personal movie statistics
   - Mood-to-movie correlations

6. **Mobile Application**
   - Native iOS/Android apps
   - Offline watchlist viewing
   - Push notifications

7. **Advanced Search**
   - Filter by director, actor, production company
   - Release date range filtering
   - Runtime filtering
   - Language preferences

8. **Integration with Streaming Services**
   - Show which streaming service has each movie
   - Price comparison
   - Subscribe link integration

9. **Improved Recommendations**
   - Content-based filtering (similar movies to favorites)
   - Hybrid recommendation (combine multiple algorithms)
   - Trending within mood preferences

10. **Accessibility Improvements**
    - Closed captions for trailers
    - Screen reader optimization
    - Keyboard navigation throughout

---

## Conclusion

CineQuest successfully demonstrates full-stack web development with a practical, user-focused application. The identification and resolution of 11 bugs showcases the importance of thorough testing and code review. The innovation feature - mood-based movie discovery - shows how understanding user psychology can enhance application design beyond algorithmic recommendations.

The project architecture separates concerns effectively between frontend and backend, uses industry-standard frameworks, and provides a scalable foundation for future enhancements. The documentation, comprehensive API endpoints, and well-organized codebase make CineQuest maintainable and extensible for future developers.

**Key Takeaways:**
- Proper environment configuration prevents security vulnerabilities
- Type safety in TypeScript catches errors early
- Code readability and naming conventions improve maintainability
- User-centric features like mood discovery drive engagement
- Comprehensive testing strategy catches issues before production

---

**Report Generated:** April 2026
**Project Repository:** Software-Construction-Exam-Project
**Team:** 10 Members
**Status:** Complete with documented improvements
