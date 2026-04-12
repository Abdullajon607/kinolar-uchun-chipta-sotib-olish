from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cinema.models import Category, Cinema, Hall, Movie, Showtime


class SmokePageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_and_search(self):
        self.assertEqual(self.client.get(reverse("cinema:home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cinema:search")).status_code, 200)

    def test_auth_pages(self):
        self.assertEqual(self.client.get(reverse("cinema:login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cinema:register")).status_code, 200)

    def test_api_movies_json(self):
        r = self.client.get(reverse("cinema:api_movies"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"][:16], "application/json")


class RegisterValidationTests(TestCase):
    def test_register_rejects_short_password(self):
        c = Client()
        r = c.post(
            reverse("cinema:register"),
            {
                "username": "newuser_xyz",
                "email": "newuser_xyz@example.com",
                "password": "short",
                "password_confirm": "short",
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser_xyz").exists())


class MovieAccessTests(TestCase):
    def test_inactive_movie_404_for_guest(self):
        cat = Category.objects.create(name="T", slug="t-test", is_active=True)
        m = Movie.objects.create(
            title="Hidden",
            description="d",
            genre="g",
            category=cat,
            duration=90,
            rating=0,
            release_date="2020-01-01",
            is_active=False,
        )
        r = self.client.get(reverse("cinema:movie_detail", args=[m.id]))
        self.assertEqual(r.status_code, 404)


class ShowtimeSeatTests(TestCase):
    def test_past_showtime_redirects_from_seat_selection(self):
        cinema = Cinema.objects.create(
            name="C",
            location="L",
            city="T",
            phone="1",
            address="A",
        )
        hall = Hall.objects.create(
            cinema=cinema,
            name="H",
            hall_type="standard",
            total_seats=10,
            rows=2,
            columns=5,
        )
        cat = Category.objects.create(name="T2", slug="t2-test", is_active=True)
        movie = Movie.objects.create(
            title="M",
            description="d",
            genre="g",
            category=cat,
            duration=90,
            rating=5,
            release_date="2020-01-01",
            is_active=True,
        )
        past = timezone.now() - timezone.timedelta(days=1)
        st = Showtime.objects.create(
            movie=movie,
            hall=hall,
            start_time=past,
            end_time=past + timezone.timedelta(hours=2),
            ticket_price=10000,
            available_seats=10,
        )
        r = self.client.get(reverse("cinema:select_seats", args=[st.id]))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("cinema:movie_detail", args=[movie.id]), r.url)
