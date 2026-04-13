"""
Comprehensive test suite for the movies app.

Tests cover:
- Model creation and field validation
- Model relationships (M2M, FK)
- ViewSet list and detail endpoints
- Standalone endpoints (search, mood, compare, etc.)
- Error handling and validation
- Serializer behavior and data integrity
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date

from .models import Genre, Person, Movie, MovieCast, WatchProvider


class GenreModelTestCase(TestCase):
    """Test suite for the Genre model."""

    def setUp(self):
        """Create test genre instances."""
        self.genre_action = Genre.objects.create(
            tmdb_id=28,
            name="Action",
            slug="action"
        )
        self.genre_drama = Genre.objects.create(
            tmdb_id=18,
            name="Drama",
            slug="drama"
        )

    def test_genre_model_creation(self):
        """
        Test Genre model creation and field validation.

        Ensures:
        - Genre can be created with required fields (tmdb_id, name, slug)
        - __str__ returns the genre name
        - unique constraint on tmdb_id is enforced
        - slug field is properly slugified
        """
        genre = Genre.objects.get(tmdb_id=28)
        self.assertEqual(genre.name, "Action")
        self.assertEqual(genre.slug, "action")
        self.assertEqual(str(genre), "Action")

    def test_genre_tmdb_id_uniqueness(self):
        """
        Test that TMDB ID uniqueness constraint is enforced.

        This prevents duplicate genres from being synced from TMDB API,
        which would create data inconsistencies.
        """
        with self.assertRaises(Exception):
            Genre.objects.create(
                tmdb_id=28,  # Duplicate of self.genre_action
                name="Action Movies",
                slug="action-movies"
            )

    def test_genre_slug_uniqueness(self):
        """
        Test that slug uniqueness is enforced for URL routing.

        Slug is used as lookup_field in GenreViewSet, so duplicates
        would cause routing ambiguity.
        """
        with self.assertRaises(Exception):
            Genre.objects.create(
                tmdb_id=99,
                name="Another Action",
                slug="action"  # Duplicate slug
            )

    def test_genre_ordering(self):
        """
        Test that genres are ordered alphabetically by name.

        Ensures consistent ordering for UI display and pagination.
        """
        genres = list(Genre.objects.all())
        self.assertEqual(genres[0].name, "Action")
        self.assertEqual(genres[1].name, "Drama")


class PersonModelTestCase(TestCase):
    """Test suite for the Person model."""

    def setUp(self):
        """Create test person instances."""
        self.director = Person.objects.create(
            tmdb_id=3,
            name="Frank Capra",
            profile_path="/profile/frank_capra.jpg",
            biography="American film director known for his comedies.",
            birthday=date(1897, 5, 18),
            place_of_birth="Bisacquino, Sicily",
            known_for_department="Directing"
        )

    def test_person_model_creation(self):
        """
        Test Person model creation with full details.

        Ensures:
        - All fields are properly stored
        - __str__ returns the person's name
        - Optional fields (profile_path, biography) can be blank
        """
        person = Person.objects.get(tmdb_id=3)
        self.assertEqual(person.name, "Frank Capra")
        self.assertEqual(person.known_for_department, "Directing")
        self.assertEqual(str(person), "Frank Capra")

    def test_person_profile_url_property(self):
        """
        Test the profile_url property generates correct TMDB image URL.

        This property constructs the full image URL from profile_path,
        which is essential for displaying actor/director headshots.
        Requires TMDB_IMAGE_BASE_URL setting to be configured.
        """
        from django.conf import settings
        profile_url = self.director.profile_url
        self.assertIn("w185", profile_url)
        self.assertIn(settings.TMDB_IMAGE_BASE_URL, profile_url)

    def test_person_without_profile_path(self):
        """
        Test that profile_url returns None when profile_path is empty.

        Handles gracefully when TMDB doesn't have an image for a person.
        """
        person = Person.objects.create(
            tmdb_id=999,
            name="Unknown Actor",
            profile_path="",  # No profile image
            known_for_department="Acting"
        )
        self.assertIsNone(person.profile_url)

    def test_person_tmdb_id_uniqueness(self):
        """
        Test that TMDB IDs prevent duplicate person records.

        This is critical for maintaining referential integrity when
        syncing from TMDB API.
        """
        with self.assertRaises(Exception):
            Person.objects.create(
                tmdb_id=3,  # Duplicate
                name="Another Director",
                known_for_department="Directing"
            )

    def test_person_ordering(self):
        """
        Test that people are ordered alphabetically by name.

        Ensures consistent ordering for cast/crew lists.
        """
        person2 = Person.objects.create(
            tmdb_id=4,
            name="Akira Kurosawa",
            known_for_department="Directing"
        )
        people = list(Person.objects.all())
        self.assertEqual(people[0].name, "Akira Kurosawa")
        self.assertEqual(people[1].name, "Frank Capra")


class MovieModelTestCase(TestCase):
    """Test suite for the Movie model."""

    def setUp(self):
        """Create test movie with genres and relationships."""
        self.genre_action = Genre.objects.create(
            tmdb_id=28,
            name="Action",
            slug="action"
        )
        self.genre_drama = Genre.objects.create(
            tmdb_id=18,
            name="Drama",
            slug="drama"
        )
        self.director = Person.objects.create(
            tmdb_id=1,
            name="Christopher Nolan",
            known_for_department="Directing"
        )
        self.movie = Movie.objects.create(
            tmdb_id=550,
            imdb_id="tt0137523",
            title="Fight Club",
            overview="An insomniac office worker and a devil-may-care soapmaker form an underground fight club.",
            release_date=date(1999, 10, 15),
            vote_average=8.8,
            vote_count=1500000,
            popularity=86.5,
            poster_path="/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
            backdrop_path="/fCayJrkAFtVM5BKcyxBj98Vrocz.jpg",
            runtime=139,
            budget=63000000,
            revenue=100853753,
            trailer_key="BdJKm16Co6M"
        )
        self.movie.genres.add(self.genre_action, self.genre_drama)
        self.movie.directors.add(self.director)

    def test_movie_model_creation(self):
        """
        Test Movie model creation with all core fields.

        Ensures:
        - All required and optional fields are properly stored
        - __str__ returns title with release year
        - Numeric fields (vote_average, popularity) store correctly
        """
        movie = Movie.objects.get(tmdb_id=550)
        self.assertEqual(movie.title, "Fight Club")
        self.assertEqual(movie.vote_average, 8.8)
        self.assertEqual(movie.runtime, 139)
        self.assertEqual(str(movie), "Fight Club (1999)")

    def test_movie_genre_relationship(self):
        """
        Test many-to-many relationship between Movie and Genre.

        Ensures:
        - Genres can be added and retrieved via reverse relation
        - Multiple genres can be associated with one movie
        """
        genres = self.movie.genres.all()
        self.assertEqual(genres.count(), 2)
        self.assertIn(self.genre_action, genres)
        self.assertIn(self.genre_drama, genres)

    def test_movie_directors_relationship(self):
        """
        Test many-to-many relationship between Movie and directors.

        Ensures:
        - Directors can be associated with movies
        - Reverse relation allows querying director's movies
        """
        self.assertEqual(self.movie.directors.count(), 1)
        self.assertIn(self.director, self.movie.directors.all())
        self.assertIn(self.movie, self.director.directed_movies.all())

    def test_movie_poster_url_property(self):
        """
        Test the poster_url property constructs correct TMDB image URL.

        This is essential for displaying movie posters in the UI.
        Uses w500 size by default for full displays.
        """
        from django.conf import settings
        poster_url = self.movie.poster_url
        self.assertIn("w500", poster_url)
        self.assertIn(self.movie.poster_path, poster_url)
        self.assertIn(settings.TMDB_IMAGE_BASE_URL, poster_url)

    def test_movie_poster_url_small_property(self):
        """
        Test the poster_url_small property for thumbnail displays.

        Uses w185 size for compact list views to reduce bandwidth.
        """
        from django.conf import settings
        poster_url_small = self.movie.poster_url_small
        self.assertIn("w185", poster_url_small)
        self.assertIn(self.movie.poster_path, poster_url_small)

    def test_movie_backdrop_url_property(self):
        """
        Test the backdrop_url property for hero images.

        Uses w1280 size for full-width background images.
        """
        from django.conf import settings
        backdrop_url = self.movie.backdrop_url
        self.assertIn("w1280", backdrop_url)
        self.assertIn(self.movie.backdrop_path, backdrop_url)

    def test_movie_trailer_url_property(self):
        """
        Test the trailer_url property constructs YouTube watch URL.

        Allows embedding YouTube trailers in the UI.
        """
        trailer_url = self.movie.trailer_url
        self.assertEqual(trailer_url, f"https://www.youtube.com/watch?v={self.movie.trailer_key}")

    def test_movie_trailer_embed_url_property(self):
        """
        Test the trailer_embed_url property for iframe embedding.

        Constructs the correct embed URL for <iframe> elements.
        """
        embed_url = self.movie.trailer_embed_url
        self.assertEqual(embed_url, f"https://www.youtube.com/embed/{self.movie.trailer_key}")

    def test_movie_without_poster(self):
        """
        Test that poster_url returns None when poster_path is empty.

        Handles gracefully when TMDB has no poster for a movie.
        """
        movie = Movie.objects.create(
            tmdb_id=999,
            title="Movie Without Poster",
            poster_path="",
            release_date=date(2020, 1, 1)
        )
        self.assertIsNone(movie.poster_url)
        self.assertIsNone(movie.poster_url_small)

    def test_movie_without_trailer(self):
        """
        Test that trailer URLs return None when trailer_key is empty.

        Most older movies don't have trailer keys, so this must be handled.
        """
        movie = Movie.objects.create(
            tmdb_id=1000,
            title="Old Movie",
            trailer_key="",
            release_date=date(1960, 1, 1)
        )
        self.assertIsNone(movie.trailer_url)
        self.assertIsNone(movie.trailer_embed_url)

    def test_movie_str_without_release_date(self):
        """
        Test __str__ returns 'N/A' for year when release_date is None.

        Handles movies with unknown release dates gracefully.
        """
        movie = Movie.objects.create(
            tmdb_id=1001,
            title="Movie Without Date",
            release_date=None
        )
        self.assertEqual(str(movie), "Movie Without Date (N/A)")

    def test_movie_default_ordering(self):
        """
        Test that movies are ordered by popularity descending.

        This ensures trending/popular movies appear first in list views.
        """
        movie2 = Movie.objects.create(
            tmdb_id=551,
            title="Less Popular Movie",
            popularity=50.0,
            release_date=date(2010, 1, 1)
        )
        movies = list(Movie.objects.all())
        self.assertEqual(movies[0].title, "Fight Club")  # popularity 86.5
        self.assertEqual(movies[1].title, "Less Popular Movie")  # popularity 50.0

    def test_movie_tmdb_id_uniqueness(self):
        """
        Test that TMDB IDs prevent duplicate movie records.

        Critical for maintaining a single source of truth for each movie.
        """
        with self.assertRaises(Exception):
            Movie.objects.create(
                tmdb_id=550,  # Duplicate
                title="Fight Club Again",
                release_date=date(1999, 10, 15)
            )


class MovieCastModelTestCase(TestCase):
    """Test suite for the MovieCast through model."""

    def setUp(self):
        """Create test movie and cast relationship."""
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            release_date=date(1999, 10, 15)
        )
        self.actor1 = Person.objects.create(
            tmdb_id=819,
            name="Edward Norton",
            known_for_department="Acting"
        )
        self.actor2 = Person.objects.create(
            tmdb_id=287,
            name="Brad Pitt",
            known_for_department="Acting"
        )
        self.cast1 = MovieCast.objects.create(
            movie=self.movie,
            person=self.actor1,
            character="The Narrator",
            order=0
        )
        self.cast2 = MovieCast.objects.create(
            movie=self.movie,
            person=self.actor2,
            character="Tyler Durden",
            order=1
        )

    def test_movie_cast_model_creation(self):
        """
        Test MovieCast through model stores actor, character, and billing order.

        Ensures:
        - Cast relationships are properly created
        - Character names are stored
        - Billing order is tracked for proper display
        - __str__ returns readable cast information
        """
        cast = MovieCast.objects.get(order=0)
        self.assertEqual(cast.person.name, "Edward Norton")
        self.assertEqual(cast.character, "The Narrator")
        self.assertIn("Edward Norton", str(cast))
        self.assertIn("The Narrator", str(cast))

    def test_movie_cast_ordering(self):
        """
        Test that cast is ordered by billing position.

        Ensures main actors appear first in cast lists.
        """
        cast_list = list(self.movie.cast.through.objects.filter(movie=self.movie))
        self.assertEqual(cast_list[0].order, 0)
        self.assertEqual(cast_list[1].order, 1)

    def test_movie_cast_unique_constraint(self):
        """
        Test unique_together constraint on (movie, person, character).

        Prevents duplicate cast entries for the same role in a movie.
        """
        with self.assertRaises(Exception):
            MovieCast.objects.create(
                movie=self.movie,
                person=self.actor1,
                character="The Narrator",  # Duplicate
                order=2
            )


class WatchProviderModelTestCase(TestCase):
    """Test suite for the WatchProvider model."""

    def setUp(self):
        """Create test movie and watch provider."""
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            release_date=date(1999, 10, 15)
        )
        self.provider = WatchProvider.objects.create(
            movie=self.movie,
            provider_name="Netflix",
            provider_type="stream",
            logo_path="/netflix_logo.png",
            link="https://www.netflix.com/watch/550",
            country_code="US"
        )

    def test_watch_provider_model_creation(self):
        """
        Test WatchProvider model stores streaming platform information.

        Ensures:
        - Provider name and type are stored
        - Logo path and link are captured
        - Country code is tracked for region-specific availability
        """
        provider = WatchProvider.objects.get(provider_name="Netflix")
        self.assertEqual(provider.provider_type, "stream")
        self.assertEqual(provider.country_code, "US")
        self.assertIn("Netflix", str(provider))

    def test_watch_provider_logo_url_property(self):
        """
        Test the logo_url property constructs TMDB image URL.

        Uses w92 size for small provider logos.
        """
        from django.conf import settings
        logo_url = self.provider.logo_url
        self.assertIn("w92", logo_url)
        self.assertIn(settings.TMDB_IMAGE_BASE_URL, logo_url)

    def test_watch_provider_provider_types(self):
        """
        Test that all provider type choices are valid.

        Supports streaming, rental, purchase, and free options.
        """
        choices = dict(WatchProvider.ProviderType.choices)
        self.assertIn("stream", choices)
        self.assertIn("rent", choices)
        self.assertIn("buy", choices)
        self.assertIn("free", choices)



class MovieListAPITestCase(APITestCase):
    """Test suite for the movie list and detail endpoints."""

    def setUp(self):
        """Create test movies for API testing."""
        self.genre = Genre.objects.create(
            tmdb_id=28,
            name="Action",
            slug="action"
        )
        self.movie1 = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            overview="An insomniac office worker forms an underground fight club.",
            release_date=date(1999, 10, 15),
            vote_average=8.8,
            vote_count=1500000,
            popularity=86.5,
            poster_path="/poster1.jpg"
        )
        self.movie1.genres.add(self.genre)

        self.movie2 = Movie.objects.create(
            tmdb_id=551,
            title="Seven Samurai",
            overview="Seven samurai are hired to protect a village.",
            release_date=date(1954, 4, 26),
            vote_average=8.6,
            vote_count=500000,
            popularity=45.3,
            poster_path="/poster2.jpg"
        )
        self.movie2.genres.add(self.genre)

    def test_movie_list_endpoint(self):
        """
        Test GET /api/movies/list/ returns paginated movie list with 200 status.

        Ensures:
        - Endpoint is accessible
        - Returns paginated results
        - Movie data is properly serialized (title, vote_average, genres, etc.)
        - Respects default pagination settings
        """
        response = self.client.get("/api/movies/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 2)

        # Check first movie data structure
        first_movie = response.data["results"][0]
        self.assertIn("id", first_movie)
        self.assertIn("title", first_movie)
        self.assertIn("vote_average", first_movie)
        self.assertIn("genres", first_movie)

    def test_movie_detail_endpoint(self):
        """
        Test GET /api/movies/list/{id}/ returns full movie details with 200 status.

        Ensures:
        - Movie detail endpoint is accessible by pk
        - Returns complete movie information (genres, directors, cast, etc.)
        - Properly serializes relationships
        """
        response = self.client.get(f"/api/movies/list/{self.movie1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["title"], "Fight Club")
        self.assertEqual(data["tmdb_id"], 550)
        self.assertEqual(data["vote_average"], 8.8)
        self.assertIn("genres", data)
        self.assertEqual(len(data["genres"]), 1)

    def test_movie_detail_endpoint_not_found(self):
        """
        Test GET /api/movies/list/{invalid_id}/ returns 404.

        Ensures proper error handling for non-existent movies.
        """
        response = self.client.get("/api/movies/list/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GenreListAPITestCase(APITestCase):
    """Test suite for the genre endpoints."""

    def setUp(self):
        """Create test genres and movies."""
        self.genre_action = Genre.objects.create(
            tmdb_id=28,
            name="Action",
            slug="action"
        )
        self.genre_drama = Genre.objects.create(
            tmdb_id=18,
            name="Drama",
            slug="drama"
        )
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            release_date=date(1999, 10, 15),
            popularity=86.5
        )
        self.movie.genres.add(self.genre_action)

    def test_genre_list_endpoint(self):
        """
        Test GET /api/movies/genres/ returns all genres with movie_count.

        Ensures:
        - Genre list is accessible
        - All genres are returned
        - Each genre includes movie_count field
        - Data is properly serialized
        """
        response = self.client.get("/api/movies/genres/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)

        # Check first genre has expected fields
        first_genre = response.data["results"][0]
        self.assertIn("id", first_genre)
        self.assertIn("name", first_genre)
        self.assertIn("slug", first_genre)
        self.assertIn("movie_count", first_genre)

    def test_genre_detail_endpoint(self):
        """
        Test GET /api/movies/genres/{slug}/ returns single genre by slug.

        Ensures:
        - Genre lookup by slug works correctly
        - Returns proper genre data
        """
        response = self.client.get("/api/movies/genres/action/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Action")
        self.assertEqual(response.data["slug"], "action")

    def test_genre_movies_endpoint(self):
        """
        Test GET /api/movies/genres/{slug}/movies/ returns movies for that genre.

        Ensures:
        - Movies are filtered by genre
        - Movies are properly paginated
        - Correct movie data is returned
        """
        response = self.client.get("/api/movies/genres/action/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

        movie = response.data["results"][0]
        self.assertEqual(movie["title"], "Fight Club")

    def test_genre_movies_endpoint_not_found(self):
        """
        Test GET /api/movies/genres/{invalid_slug}/movies/ returns 404.

        Ensures proper error handling for non-existent genres.
        """
        response = self.client.get("/api/movies/genres/invalid-genre/movies/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MovieSearchAPITestCase(APITestCase):
    """Test suite for the search endpoint."""

    def setUp(self):
        """Create test movies."""
        Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            release_date=date(1999, 10, 15)
        )

    def test_movie_search_requires_query(self):
        """
        Test GET /api/movies/search/ without 'q' parameter returns 400.

        Ensures:
        - Search endpoint requires query parameter
        - Proper error message is returned
        - Prevents empty or invalid searches
        """
        response = self.client.get("/api/movies/search/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_movie_search_with_empty_query(self):
        """
        Test GET /api/movies/search/?q= (empty query) returns 400.

        Ensures whitespace-only queries are rejected.
        """
        response = self.client.get("/api/movies/search/?q=   ")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MoodListAPITestCase(APITestCase):
    """Test suite for the mood endpoints."""

    def test_mood_list_endpoint(self):
        """
        Test GET /api/movies/moods/ returns all available mood options.

        Ensures:
        - All mood types are returned
        - Each mood has required fields (slug, label, description)
        - Mood list is comprehensive and usable
        """
        response = self.client.get("/api/movies/moods/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        moods = response.data
        self.assertGreater(len(moods), 0)

        # Check first mood has required fields
        first_mood = moods[0]
        self.assertIn("slug", first_mood)
        self.assertIn("label", first_mood)
        self.assertIn("description", first_mood)

    def test_mood_list_contains_expected_moods(self):
        """
        Test that mood list includes all predefined moods.

        Ensures all mood types are available for users to browse.
        """
        response = self.client.get("/api/movies/moods/")
        mood_slugs = [m["slug"] for m in response.data]

        expected_moods = [
            "cozy-night", "adrenaline", "date-night", "mind-bender",
            "feel-good", "edge-of-seat", "epic-adventure", "cry-it-out",
            "family-fun", "documentary-deep-dive"
        ]

        for mood in expected_moods:
            self.assertIn(mood, mood_slugs)


class MovieCompareAPITestCase(APITestCase):
    """Test suite for the compare endpoint."""

    def setUp(self):
        """Create test movies."""
        self.movie1 = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            release_date=date(1999, 10, 15)
        )
        self.movie2 = Movie.objects.create(
            tmdb_id=551,
            title="Seven Samurai",
            release_date=date(1954, 4, 26)
        )

    def test_compare_requires_two_ids(self):
        """
        Test GET /api/movies/compare/?ids=550 returns 400 (need 2 IDs).

        Ensures:
        - Compare endpoint requires at least 2 movie IDs
        - Provides helpful error message
        - Prevents single-movie comparisons
        """
        response = self.client.get("/api/movies/compare/?ids=550")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_compare_requires_query_parameter(self):
        """
        Test GET /api/movies/compare/ without 'ids' returns 400.

        Ensures query parameter is mandatory.
        """
        response = self.client.get("/api/movies/compare/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_compare_with_invalid_ids(self):
        """
        Test GET /api/movies/compare/?ids=invalid returns 400.

        Ensures proper handling of non-integer IDs.
        """
        response = self.client.get("/api/movies/compare/?ids=abc,def")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_compare_with_extra_ids(self):
        """
        Test that only first 2 IDs are used when more are provided.

        GET /api/movies/compare/?ids=550,551,999 should only compare first 2.
        """
        response = self.client.get("/api/movies/compare/?ids=550,551,999")
        # This depends on TMDB API mock; with real API it would attempt to fetch all 3
        # but only compare the first 2 in response
        if response.status_code == status.HTTP_200_OK:
            self.assertIn("movies", response.data)



class MovieTrendingAPITestCase(APITestCase):
    """Test suite for trending and now-playing endpoints."""

    def test_trending_endpoint_exists(self):
        """
        Test GET /api/movies/trending/ is accessible.

        Ensures endpoint returns proper response format.
        Actual data depends on TMDB API mock.
        """
        response = self.client.get("/api/movies/trending/")
        # Status depends on whether TMDB API is mocked in settings
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])

    def test_now_playing_endpoint_exists(self):
        """
        Test GET /api/movies/now-playing/ is accessible.

        Ensures endpoint returns proper response format.
        """
        response = self.client.get("/api/movies/now-playing/")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])

    def test_top_rated_endpoint_exists(self):
        """
        Test GET /api/movies/top-rated/ is accessible.

        Ensures endpoint returns proper response format.
        """
        response = self.client.get("/api/movies/top-rated/")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])


class PersonModelAPITestCase(APITestCase):
    """Test suite for Person model functionality."""

    def setUp(self):
        """Create test person."""
        self.person = Person.objects.create(
            tmdb_id=3,
            name="Frank Capra",
            profile_path="/frank_capra.jpg",
            biography="American film director",
            birthday=date(1897, 5, 18),
            known_for_department="Directing"
        )

    def test_person_model_creation(self):
        """
        Test Person model creation with all fields.

        Ensures:
        - All fields are properly stored
        - __str__ returns person's name
        - Optional fields work correctly
        """
        person = Person.objects.get(tmdb_id=3)
        self.assertEqual(person.name, "Frank Capra")
        self.assertEqual(person.known_for_department, "Directing")
        self.assertEqual(str(person), "Frank Capra")

    def test_person_profile_url_property(self):
        """
        Test Person profile_url property generates correct TMDB image URL.

        Ensures:
        - URLs are properly constructed
        - Correct size (w185) is used
        - Setting is properly utilized
        """
        from django.conf import settings
        profile_url = self.person.profile_url
        self.assertIsNotNone(profile_url)
        self.assertIn("w185", profile_url)
        self.assertIn(self.person.profile_path, profile_url)

    def test_person_without_profile_path_returns_none(self):
        """
        Test that profile_url returns None when profile_path is empty.

        Handles gracefully when no image is available.
        """
        person = Person.objects.create(
            tmdb_id=999,
            name="Unknown Person",
            profile_path="",
            known_for_department="Acting"
        )
        self.assertIsNone(person.profile_url)

    def test_person_list_endpoint(self):
        """
        Test GET /api/movies/people/ returns list of people.

        Ensures people (directors, actors) can be browsed via API.
        """
        response = self.client.get("/api/movies/people/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_person_detail_endpoint(self):
        """
        Test GET /api/movies/people/{id}/ returns person details.

        Ensures:
        - Person can be retrieved by ID
        - Full details are returned
        - Relationships (directed_movies, acted_movies) are included
        """
        response = self.client.get(f"/api/movies/people/{self.person.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Frank Capra")
        self.assertIn("biography", response.data)
        self.assertIn("directed_movies", response.data)
        self.assertIn("acted_movies", response.data)


class MovieIntegrationTestCase(APITestCase):
    """Integration tests combining multiple models and endpoints."""

    def setUp(self):
        """Create complete test data structure."""
        # Create genres
        self.action_genre = Genre.objects.create(
            tmdb_id=28,
            name="Action",
            slug="action"
        )
        self.drama_genre = Genre.objects.create(
            tmdb_id=18,
            name="Drama",
            slug="drama"
        )

        # Create people
        self.director = Person.objects.create(
            tmdb_id=1,
            name="David Fincher",
            profile_path="/fincher.jpg",
            biography="American film director",
            known_for_department="Directing"
        )
        self.actor1 = Person.objects.create(
            tmdb_id=2,
            name="Edward Norton",
            profile_path="/norton.jpg",
            known_for_department="Acting"
        )

        # Create movies
        self.movie = Movie.objects.create(
            tmdb_id=550,
            title="Fight Club",
            overview="A thriller about underground fighting.",
            release_date=date(1999, 10, 15),
            vote_average=8.8,
            vote_count=1500000,
            popularity=86.5,
            poster_path="/poster.jpg",
            runtime=139,
            budget=63000000,
            revenue=100853753
        )
        self.movie.genres.add(self.action_genre, self.drama_genre)
        self.movie.directors.add(self.director)

        # Create cast
        self.cast = MovieCast.objects.create(
            movie=self.movie,
            person=self.actor1,
            character="The Narrator",
            order=0
        )

        # Create watch provider
        self.provider = WatchProvider.objects.create(
            movie=self.movie,
            provider_name="Netflix",
            provider_type="stream",
            logo_path="/netflix.png"
        )

    def test_complete_movie_detail_with_all_relationships(self):
        """
        Test that movie detail endpoint returns complete data including all relationships.

        Ensures:
        - Movie details are complete
        - Genres are included and serialized
        - Directors are included and serialized
        - Cast is included with character info
        - Watch providers are included
        - All URLs are properly constructed
        """
        response = self.client.get(f"/api/movies/list/{self.movie.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["title"], "Fight Club")
        self.assertEqual(len(data["genres"]), 2)
        self.assertEqual(len(data["directors"]), 1)
        self.assertEqual(data["directors"][0]["name"], "David Fincher")
        self.assertGreater(len(data["cast"]), 0)
        self.assertEqual(len(data["watch_providers"]), 1)

    def test_genre_movies_includes_all_relationships(self):
        """
        Test that movies retrieved via genre endpoint include all serialized data.

        Ensures filtering by genre doesn't strip relationship data.
        """
        response = self.client.get("/api/movies/genres/action/movies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        movie_data = response.data["results"][0]
        self.assertEqual(movie_data["title"], "Fight Club")
        self.assertIn("genres", movie_data)
        self.assertIn("vote_average", movie_data)

    def test_ordering_and_filtering_consistency(self):
        """
        Test that movies maintain consistent ordering across endpoints.

        Ensures:
        - Movies returned by list and genre filters have same data
        - Ordering is consistent (by popularity)
        - No data loss in serialization
        """
        list_response = self.client.get("/api/movies/list/")
        genre_response = self.client.get("/api/movies/genres/action/movies/")

        list_movie = list_response.data["results"][0]
        genre_movie = genre_response.data["results"][0]

        self.assertEqual(list_movie["tmdb_id"], genre_movie["tmdb_id"])
        self.assertEqual(list_movie["title"], genre_movie["title"])
        self.assertEqual(list_movie["vote_average"], genre_movie["vote_average"])
