from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

# ==================== CATEGORY MODEL ====================

class Category(models.Model):
    """Kategoriya modeli"""
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi", unique=True)
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL slugi")
    description = models.TextField(blank=True, verbose_name="Tavsifi")
    icon = models.CharField(max_length=50, default="movie", verbose_name="Ikonka (Material Icons)")
    color = models.CharField(max_length=7, default="#4b8eff", verbose_name="Rang (Hex)")
    order = models.IntegerField(default=0, verbose_name="Tartibi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


# ==================== CINEMA MODELS ====================

class Movie(models.Model):
    """Film modeli"""
    title = models.CharField(max_length=200, verbose_name="Film nomi")
    description = models.TextField(verbose_name="Tavsifi")
    genre = models.CharField(max_length=100, verbose_name="Janri")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='movies', verbose_name="Kategoriya")
    duration = models.IntegerField(verbose_name="Davomiyligi (minutlarda)")
    rating = models.FloatField(default=0, verbose_name="Reytingi")
    poster = models.ImageField(upload_to='movies/posters/', null=True, blank=True, verbose_name="Poster rasm (Fayl)")
    poster_url = models.URLField(blank=True, verbose_name="Poster rasm (URL)")
    trailer_url = models.URLField(blank=True, verbose_name="Trailer URL")
    release_date = models.DateField(verbose_name="Chiqarilish sanasi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Film"
        verbose_name_plural = "Filmlar"
        ordering = ['-release_date']
    
    def __str__(self):
        return self.title
    
    def get_poster_url(self):
        """Poster URL ni qaytarish - fayl yoki URL"""
        if self.poster:
            return self.poster.url
        elif self.poster_url:
            return self.poster_url
        else:
            return 'https://via.placeholder.com/300x450?text=No+Image'
            
    def save(self, *args, **kwargs):
        # YouTube oddiy linklarini avtomatik iframe (embed) formatiga o'girish
        if self.trailer_url:
            if "watch?v=" in self.trailer_url:
                video_id = self.trailer_url.split("watch?v=")[1].split("&")[0]
                self.trailer_url = f"https://www.youtube.com/embed/{video_id}"
            elif "youtu.be/" in self.trailer_url:
                video_id = self.trailer_url.split("youtu.be/")[1].split("?")[0]
                self.trailer_url = f"https://www.youtube.com/embed/{video_id}"
            elif "shorts/" in self.trailer_url:
                video_id = self.trailer_url.split("shorts/")[1].split("?")[0]
                self.trailer_url = f"https://www.youtube.com/embed/{video_id}"
        super().save(*args, **kwargs)


class Cinema(models.Model):
    """Kinoteatr modeli"""
    name = models.CharField(max_length=200, verbose_name="Kinoteatr nomi")
    location = models.CharField(max_length=300, verbose_name="Joylashgan joyi")
    city = models.CharField(max_length=100, verbose_name="Shahar")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.CharField(max_length=300, verbose_name="Manzil")
    
    class Meta:
        verbose_name = "Kinoteatr"
        verbose_name_plural = "Kinoteatrlar"
    
    def __str__(self):
        return self.name


class Hall(models.Model):
    """Zal modeli"""
    HALL_TYPES = [
        ('standard', 'Standard'),
        ('imax', 'IMAX'),
        ('3d', '3D'),
    ]
    
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name='halls', verbose_name="Kinoteatr")
    name = models.CharField(max_length=100, verbose_name="Zal nomi")
    hall_type = models.CharField(max_length=20, choices=HALL_TYPES, verbose_name="Zal turi")
    total_seats = models.IntegerField(default=0, blank=True, verbose_name="Umumiy o'rindiqlar soni")
    rows = models.IntegerField(default=10, verbose_name="Qatorlar soni")
    columns = models.IntegerField(default=12, verbose_name="Ustunlar soni")
    
    class Meta:
        verbose_name = "Zal"
        verbose_name_plural = "Zallar"
    
    def __str__(self):
        return f"{self.cinema.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.total_seats = self.rows * self.columns
        super().save(*args, **kwargs)
        
        # Agar zal o'lchamlari (qator/ustun) o'zgargan bo'lsa, o'rindiqlarni qaytadan chizamiz
        if self.seats.count() != self.total_seats:
            # Eski o'rindiqlarni tozalash (yangilash uchun)
            self.seats.all().delete()
            
            row_labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            seats_to_create = []
            for r in range(min(self.rows, 26)):
                row_label = row_labels[r]
                for c in range(1, self.columns + 1):
                    seats_to_create.append(
                        Seat(hall=self, row=row_label, number=c, seat_type='regular', is_available=True)
                    )
            if seats_to_create:
                Seat.objects.bulk_create(seats_to_create)


class Seat(models.Model):
    """O'rindiq modeli"""
    SEAT_TYPES = [
        ('regular', 'Oddiy'),
        ('vip', 'VIP'),
        ('couple', 'Juftlik'),
    ]
    
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats', verbose_name="Zal")
    row = models.CharField(max_length=2, verbose_name="Qator")
    number = models.IntegerField(verbose_name="Raqami")
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPES, default='regular', verbose_name="O'rindiq turi")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Narxi")
    
    class Meta:
        unique_together = ('hall', 'row', 'number')
        verbose_name = "O'rindiq"
        verbose_name_plural = "O'rindiqlar"
    
    def __str__(self):
        return f"{self.hall.name} - Qator {self.row}, O'rindiq {self.number}"


class Showtime(models.Model):
    """Seans modeli"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes', verbose_name="Film")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='showtimes', verbose_name="Zal")
    start_time = models.DateTimeField(verbose_name="Boshlanish vaqti")
    end_time = models.DateTimeField(verbose_name="Tugash vaqti")
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=45000, verbose_name="Chipta narxi")
    available_seats = models.IntegerField(verbose_name="Mavjud o'rindiqlar")
    
    class Meta:
        unique_together = ('hall', 'start_time')
        verbose_name = "Seans"
        verbose_name_plural = "Seanslar"
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time}"
    
    def is_available(self):
        return self.available_seats > 0 and self.start_time > timezone.now()


class Booking(models.Model):
    """Broniya modeli"""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('cancelled', 'Bekor qilinga'),
        ('completed', 'Yakunlangan'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Foydalanuvchi")
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings', verbose_name="Seans")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umumiy narx")
    number_of_seats = models.IntegerField(verbose_name="O'rindiqlar soni")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Broniya sanasi")
    booking_reference = models.CharField(max_length=20, unique=True, verbose_name="Broniya raqami")
    
    class Meta:
        verbose_name = "Broniya"
        verbose_name_plural = "Broniyalar"
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Broniya {self.booking_reference} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"CK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Ticket(models.Model):
    """Chipta modeli"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets', verbose_name="Broniya")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, verbose_name="O'rindiq")
    ticket_number = models.CharField(max_length=50, unique=True, verbose_name="Chipta raqami")
    qr_code = models.TextField(blank=True, verbose_name="QR kod")
    is_used = models.BooleanField(default=False, verbose_name="Ishlatilib bo'ldi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    
    class Meta:
        verbose_name = "Chipta"
        verbose_name_plural = "Chiptalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chipta {self.ticket_number}"


class Review(models.Model):
    """Foydalanuvchilarning kinolarga qoldirgan izohlari"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', verbose_name="Film")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    text = models.TextField(verbose_name="Izoh matni")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5, verbose_name="Baho (1-5)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yozilgan vaqt")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"
        
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"