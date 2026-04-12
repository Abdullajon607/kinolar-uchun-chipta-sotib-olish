from django.contrib import admin
from .models import Category, Movie, Cinema, Hall, Seat, Showtime, Booking, Ticket, Review

# ==================== CATEGORY ADMIN ====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order', 'color')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Dizayn', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Holati', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'movie__title', 'text')


# ==================== CINEMA ADMIN ====================

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'genre', 'rating', 'release_date', 'is_active')
    list_filter = ('category', 'genre', 'is_active', 'release_date')
    search_fields = ('title', 'description', 'genre')
    ordering = ('-release_date',)
    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('title', 'category', 'genre', 'rating', 'duration')
        }),
        ('Tavsiflar', {
            'fields': ('description',)
        }),
        ('Media', {
            'fields': ('poster', 'poster_url', 'trailer_url')
        }),
        ('Holati', {
            'fields': ('release_date', 'is_active')
        }),
    )


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'location')
    list_filter = ('city',)
    search_fields = ('name', 'location', 'address')
    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('name', 'city')
        }),
        ('Kontakt', {
            'fields': ('phone', 'address', 'location')
        }),
    )


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'cinema', 'hall_type', 'total_seats', 'rows', 'columns')
    list_filter = ('cinema', 'hall_type')
    search_fields = ('name', 'cinema__name')
    readonly_fields = ('total_seats',)
    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('cinema', 'name', 'hall_type')
        }),
        ('O\'rindiqlar', {
            'fields': ('rows', 'columns', 'total_seats')
        }),
    )


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hall', 'seat_type', 'is_available', 'price')
    list_filter = ('hall', 'seat_type', 'is_available')
    search_fields = ('hall__name', 'row')
    fieldsets = (
        ('O\'rindiq ma\'lumot', {
            'fields': ('hall', 'row', 'number', 'seat_type')
        }),
        ('Narxi', {
            'fields': ('price',)
        }),
        ('Holati', {
            'fields': ('is_available',)
        }),
    )

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'ticket_price', 'available_seats')
    list_filter = ('movie', 'hall', 'start_time')
    search_fields = ('movie__title', 'hall__name')
    fieldsets = (
        ('Seans ma\'lumot', {
            'fields': ('movie', 'hall')
        }),
        ('Vaqt', {
            'fields': ('start_time', 'end_time')
        }),
        ('Narxi va o\'rindiqlar', {
            'fields': ('ticket_price', 'available_seats')
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'showtime', 'status', 'total_price', 'booking_date')
    list_filter = ('status', 'booking_date')
    search_fields = ('booking_reference', 'user__username')
    readonly_fields = ('booking_reference', 'booking_date')
    fieldsets = (
        ('Broniya ma\'lumot', {
            'fields': ('booking_reference', 'user', 'status')
        }),
        ('Seans va narx', {
            'fields': ('showtime', 'number_of_seats', 'total_price')
        }),
        ('Vaqt', {
            'fields': ('booking_date',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'booking', 'seat', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('ticket_number', 'booking__booking_reference')
    readonly_fields = ('ticket_number', 'qr_code', 'created_at')
    fieldsets = (
        ('Chipta ma\'lumot', {
            'fields': ('ticket_number', 'booking', 'seat')
        }),
        ('QR kod', {
            'fields': ('qr_code',)
        }),
        ('Holati', {
            'fields': ('is_used', 'created_at')
        }),
    )