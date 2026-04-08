from django.shortcuts import render, redirect, get_object_or_404
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
from django.db.models import Q

from .models import Movie, Category, Cinema, Hall, Seat, Showtime, Booking, Ticket, Todo

# ==================== CINEMA VIEWS ====================

def home(request):
    """Bosh sahifa - kategoriyalashtirilgan filmlar"""
    
    # Aktiv kategoriyalar
    categories_obj = Category.objects.filter(is_active=True).order_by('order')
    
    # Har bir kategoriyaga filmlar
    categories = {}
    for cat in categories_obj:
        movies = Movie.objects.filter(
            is_active=True,
            category=cat
        ).order_by('-release_date')
        if movies.exists():
            categories[cat] = movies
    
    featured_movie = Movie.objects.filter(is_active=True).order_by('-release_date').first()
    
    context = {
        'featured_movie': featured_movie,
        'categories': categories,
    }
    return render(request, 'bosh-sahifa.html', context)


def register(request):
    """Foydalanuvchi ro'yxatdan o'tish"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Parollar mos kelmadi')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Foydalanuvchi allaqachon mavjud')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Ro\'yxatdan o\'tish muvaffaqiyatli!')
        return redirect('cinema:home')
    
    return render(request, 'register.html')


def login_view(request):
    """Tizimga kirish"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
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


def movie_detail(request, movie_id):
    """Film tafsilotlari va seanslar"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    today = timezone.now().date()
    showtimes = Showtime.objects.filter(
        movie=movie,
        start_time__date__gte=today
    ).order_by('start_time')[:6]
    
    context = {
        'movie': movie,
        'showtimes': showtimes,
        'poster_url': movie.get_poster_url(),
    }
    return render(request, 'seanslar.html', context)


def select_seats(request, showtime_id):
    """O'rindiqlarni tanlash"""
    showtime = get_object_or_404(Showtime, id=showtime_id)
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
    
    selected_seats = Seat.objects.filter(id__in=selected_seats_ids, is_available=True)
    
    if not selected_seats.exists():
        messages.error(request, 'Tanlangan o\'rindiqlar mavjud emas')
        return redirect('cinema:select_seats', showtime_id=showtime_id)
    
    total_price = sum(seat.price for seat in selected_seats)
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
        
        seats = Seat.objects.filter(id__in=seat_ids, is_available=True)
        if len(seats) != len(seat_ids):
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
        selected_seats = Seat.objects.filter(
            id__in=selected_seats_ids,
            is_available=True
        )
        
        if not selected_seats.exists():
            return JsonResponse({'success': False, 'message': 'O\'rindiqlar mavjud emas'})
        
        number_of_seats = selected_seats.count()
        total_price = sum(seat.price for seat in selected_seats)
        
        # Broniya yaratish
        booking = Booking.objects.create(
            user=request.user,
            showtime=showtime,
            status='confirmed',
            total_price=total_price,
            number_of_seats=number_of_seats,
        )
        
        # Chiptalar yaratish
        for seat in selected_seats:
            ticket_number = f"CK-{booking.id}-{uuid.uuid4().hex[:8].upper()}"
            
            # QR kod yaratish
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
            
            seat.is_available = False
            seat.save()
        
        showtime.available_seats -= number_of_seats
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
    """Filmlarni qidiruv"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Movie.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search.html', context)


# ==================== TODO VIEWS ====================

@login_required
def todo_list(request):
    """To'do list sahifasi"""
    return render(request, 'todo.html')


@login_required
@require_POST
def sync_todos(request):
    """Server bilan sinxronizlash"""
    try:
        data = json.loads(request.body)
        
        if not isinstance(data, list):
            return JsonResponse({'success': False, 'message': 'Invalid data format'}, status=400)
        
        for todo_data in data:
            if 'id' in todo_data and 'text' in todo_data:
                Todo.objects.update_or_create(
                    id=todo_data.get('id'),
                    user=request.user,
                    defaults={
                        'text': todo_data['text'][:500],
                        'completed': bool(todo_data.get('completed', False)),
                        'priority': todo_data.get('priority', 'normal'),
                    }
                )
        
        return JsonResponse({'success': True, 'message': 'Sinxronizlandi'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# ==================== API ENDPOINTS ====================

def get_movies_api(request):
    """API: Barcha filmlar"""
    movies = Movie.objects.filter(is_active=True).values(
        'id', 'title', 'genre', 'rating', 'poster_url'
    )
    return JsonResponse(list(movies), safe=False)


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