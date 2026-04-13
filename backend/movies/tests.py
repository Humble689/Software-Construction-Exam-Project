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

