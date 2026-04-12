from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
import uuid
import json
import qrcode
from io import BytesIO
import base64

from .models import Movie, Category, Cinema, Hall, Seat, Showtime, Booking, Ticket, Review

# ==================== CINEMA VIEWS ====================

def home(request):
    """Bosh sahifa - kategoriyalashtirilgan filmlar"""
    categories_obj = Category.objects.filter(is_active=True).order_by("order")

    categories = {}
    for cat in categories_obj:
        movies = Movie.objects.filter(category=cat, is_active=True).order_by("-release_date")
        if len(movies) > 0:
            categories[cat] = movies

    featured_movie = Movie.objects.filter(is_active=True).order_by("-release_date").first()
    
    context = {
        'featured_movie': featured_movie,
        'categories': categories,
    }
    return render(request, 'bosh-sahifa.html', context)


def register(request):
    """Foydalanuvchi ro'yxatdan o'tish"""
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        password_confirm = request.POST.get('password_confirm') or ''

        if not username or not password:
            messages.error(request, 'Foydalanuvchi nomi va parol majburiy')
            return render(request, 'register.html')

        if password != password_confirm:
            messages.error(request, 'Parollar mos kelmadi')
            return render(request, 'register.html')

        if len(password) < 8:
            messages.error(request, 'Parol kamida 8 belgidan iborat bo\'lishi kerak')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Foydalanuvchi allaqachon mavjud')
            return render(request, 'register.html')

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Bu email allaqachon ro\'yxatdan o\'tgan')
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Ro\'yxatdan o\'tish muvaffaqiyatli!')
        return redirect('cinema:home')
    
    return render(request, 'register.html')


def login_view(request):
    """Tizimga kirish"""
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        if not username or not password:
            messages.error(request, 'Login va parolni kiriting')
            return render(request, 'login-page.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Tizimga muvaffaqiyatli kirdingiz!')
            return redirect('cinema:home')
        else:
            messages.error(request, 'Login yoki parol noto\'g\'ri')
            return render(request, 'login-page.html')
    
    return render(request, 'login-page.html')


def logout_view(request):
    """Tizimdan chiqish"""
    logout(request)
    messages.success(request, 'Tizimdan chiqtingiz!')
    return redirect('cinema:home')


@login_required
def profile_view(request):
    """Foydalanuvchi profilini ko'rish va tahrirlash"""
    if request.method == 'POST':
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        new_password = request.POST.get('new_password')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        
        if new_password:
            if len(new_password) < 8:
                messages.error(request, "Yangi parol kamida 8 belgidan iborat bo'lishi kerak.")
                return redirect('cinema:profile')
            user.set_password(new_password)
            
        user.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, "Profil ma'lumotlari muvaffaqiyatli saqlandi!")
        return redirect('cinema:profile')
        
    return render(request, 'profil.html')


def movie_detail(request, movie_id):
    """Film tafsilotlari va seanslar"""
    movie_qs = Movie.objects.all()
    if not getattr(request.user, "is_staff", False):
        movie_qs = movie_qs.filter(is_active=True)
    movie = get_object_or_404(movie_qs, id=movie_id)
    
    # Izoh qoldirish mantiqi
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text', '').strip()
        rating = int(request.POST.get('rating', 5))
        if text:
            Review.objects.create(
                movie=movie,
                user=request.user,
                text=text,
                rating=rating
            )
            
            # Izohlarga qarab filmning o'rtacha reytingini avtomatik yangilash
            all_reviews = Review.objects.filter(movie=movie)
            total_rating = 0
            for r in all_reviews:
                total_rating += r.rating
                
            if len(all_reviews) > 0:
                movie.rating = round(total_rating / len(all_reviews), 1)
            else:
                movie.rating = 0
            movie.save()
                
            messages.success(request, "Izohingiz muvaffaqiyatli qo'shildi!")
            return redirect('cinema:movie_detail', movie_id=movie.id)
    
    today = timezone.now().date()
    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__date__gte=today
    ).order_by('start_time')[:6]
    
    context = {
        'movie': movie,
        'showtimes': showtimes,
        'reviews': movie.reviews.all(),
        'poster_url': movie.get_poster_url(),
    }
    return render(request, 'seanslar.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    """Foydalanuvchining o'z izohini o'chirish"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    movie = review.movie
    review.delete()
    
    # Izoh o'chirilgach, reytingni qayta hisoblab qo'yamiz
    all_reviews = Review.objects.filter(movie=movie)
    total_rating = 0
    for r in all_reviews:
        total_rating += r.rating
        
    if len(all_reviews) > 0:
        movie.rating = round(total_rating / len(all_reviews), 1)
    else:
        movie.rating = 0
    movie.save()
    
    messages.success(request, "Izoh o'chirildi!")
    return redirect('cinema:movie_detail', movie_id=movie.id)


def select_seats(request, showtime_id):
    """O'rindiqlarni tanlash"""
    showtime = get_object_or_404(
        Showtime.objects.select_related("movie", "hall"), id=showtime_id
    )
    if showtime.start_time < timezone.now():
        messages.warning(
            request, "Bu seans allaqachon boshlangan yoki yakunlangan — boshqa seans tanlang."
        )
        return redirect("cinema:movie_detail", movie_id=showtime.movie_id)
    if not showtime.movie.is_active and not getattr(request.user, "is_staff", False):
        raise Http404("Film mavjud emas")
    hall = showtime.hall
    seats = Seat.objects.filter(hall=hall).order_by('row', 'number')
    
    seat_rows = {}
    for seat in seats:
        if seat.row not in seat_rows:
            seat_rows[seat.row] = []
        seat_rows[seat.row].append(seat)
    
    context = {
        'showtime': showtime,
        'hall': hall,
        'seat_rows': sorted(seat_rows.items()),
    }
    return render(request, 'zal.html', context)


@login_required
def checkout(request, showtime_id):
    """To'lov sahifasi"""
    showtime = get_object_or_404(Showtime, id=showtime_id)
    
    selected_seats_ids = request.session.get('selected_seats', [])
    if not selected_seats_ids:
        messages.warning(request, 'Avval o\'rindiqlarni tanlang')
        return redirect('cinema:select_seats', showtime_id=showtime_id)
    
    selected_seats = []
    all_tickets = Ticket.objects.filter(booking__showtime=showtime)
    for seat_id in selected_seats_ids:
        seat = Seat.objects.get(id=seat_id)
        is_booked = False
        for t in all_tickets:
            if str(t.seat.id) == str(seat.id):
                is_booked = True
        if not is_booked:
            selected_seats.append(seat)
    
    if len(selected_seats) == 0:
        messages.error(request, 'Tanlangan o\'rindiqlar mavjud emas')
        return redirect('cinema:select_seats', showtime_id=showtime_id)
    
    total_price = showtime.ticket_price * len(selected_seats)
    final_total = total_price
    
    context = {
        'showtime': showtime,
        'selected_seats': selected_seats,
        'total_price': total_price,
        'final_total': final_total,
    }
    return render(request, 'tolov.html', context)


@login_required
@require_POST
def save_selected_seats(request, showtime_id):
    """Tanlangan o'rindiqlarni saqlash"""
    try:
        seat_ids = request.POST.getlist('seat_ids')
        
        if not seat_ids:
            return JsonResponse({'success': False, 'message': 'O\'rindiqlar tanlanmadi'})
        
        valid_seats = []
        all_tickets = Ticket.objects.filter(booking__showtime_id=showtime_id)
        for seat_id in seat_ids:
            seat = Seat.objects.get(id=seat_id)
            is_booked = False
            for t in all_tickets:
                if str(t.seat.id) == str(seat.id):
                    is_booked = True
            if not is_booked:
                valid_seats.append(seat)
                
        if len(valid_seats) != len(seat_ids):
            return JsonResponse({'success': False, 'message': 'Ayrim o\'rindiqlar band'})
        
        request.session['selected_seats'] = seat_ids
        request.session.save()
        
        return JsonResponse({
            'success': True,
            'redirect_url': f'/checkout/{showtime_id}/',
            'seat_count': len(seat_ids)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def process_payment(request, showtime_id):
    """To'lovni qayta ishlash"""
    showtime = get_object_or_404(Showtime, id=showtime_id)
    selected_seats_ids = request.session.get('selected_seats', [])
    
    if not selected_seats_ids:
        return JsonResponse({'success': False, 'message': 'O\'rindiqlar tanlanmadi'})
    
    try:
        selected_seats = []
        all_tickets = Ticket.objects.filter(booking__showtime=showtime)
        for seat_id in selected_seats_ids:
            seat = Seat.objects.get(id=seat_id)
            is_booked = False
            for t in all_tickets:
                if str(t.seat.id) == str(seat.id):
                    is_booked = True
            if not is_booked:
                selected_seats.append(seat)
                
        if len(selected_seats) == 0:
            return JsonResponse({'success': False, 'message': 'O\'rindiqlar mavjud emas'})
        
        number_of_seats = len(selected_seats)
        total_price = showtime.ticket_price * number_of_seats
        
        if showtime.available_seats < number_of_seats:
            return JsonResponse({'success': False, 'message': 'Bu seansda yetarli bo\'sh o\'rindiq yo\'q'})
            
        booking = Booking.objects.create(
            user=request.user,
            showtime=showtime,
            status='confirmed',
            total_price=total_price,
            number_of_seats=number_of_seats,
        )
        
        for seat in selected_seats:
            ticket_number = "CK-" + str(booking.id) + "-" + str(uuid.uuid4())[:8].upper()
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(ticket_number)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            Ticket.objects.create(
                booking=booking,
                seat=seat,
                ticket_number=ticket_number,
                qr_code=qr_code_base64,
            )
        
        showtime.available_seats = showtime.available_seats - number_of_seats
        showtime.save()
        
        del request.session['selected_seats']
        request.session.save()
        
        return JsonResponse({
            'success': True,
            'redirect_url': '/success/',
            'booking_id': booking.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Xato: {str(e)}'})


def payment_success(request):
    """To'lov muvaffaq sahifasi"""
    return render(request, 'xaridlar.html')


@login_required
def my_tickets(request):
    """Mening chiptalarim"""
    bookings = Booking.objects.filter(
        user=request.user,
        status='confirmed'
    ).prefetch_related('tickets__seat').order_by('-booking_date')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'mening-chiptalarim.html', context)


def search(request):
    """Filmlarni qidiruv (matn va ixtiyoriy kategoriya filtri)"""
    query = (request.GET.get('q') or '').strip()
    category_slug = (request.GET.get('category') or '').strip()
    results = []
    filter_category = None
    
    if category_slug:
        filter_category = Category.objects.filter(
            slug=category_slug, is_active=True
        ).first()
            
    all_movies = Movie.objects.filter(is_active=True).order_by('-release_date')
    
    for m in all_movies:
        if filter_category and m.category != filter_category:
            continue
            
        if query:
            q = query.lower()
            if q in m.title.lower() or q in m.description.lower() or q in m.genre.lower():
                results.append(m)
        else:
            results.append(m)
    
    context = {
        'query': query,
        'results': results,
        'filter_category': filter_category,
    }
    return render(request, 'search.html', context)


# ==================== API ENDPOINTS ====================

def get_movies_api(request):
    """API: Barcha filmlar (poster fayl yoki URL)"""
    out = []
    for m in Movie.objects.filter(is_active=True).iterator():
        if m.poster:
            poster = request.build_absolute_uri(m.poster.url)
        else:
            poster = m.poster_url or ''
        out.append(
            {
                'id': m.id,
                'title': m.title,
                'genre': m.genre,
                'rating': m.rating,
                'poster_url': poster,
            }
        )
    return JsonResponse(out, safe=False)


def get_showtimes_api(request, movie_id):
    """API: Film seansları"""
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__gte=timezone.now()
    ).values(
        'id', 'start_time', 'hall__cinema__name', 'ticket_price', 'available_seats'
    ).order_by('start_time')
    return JsonResponse(list(showtimes), safe=False)