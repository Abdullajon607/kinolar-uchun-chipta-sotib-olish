# kinolar-uchun-chipta-sotib-olish (Cyber-Kino)

Django 5 loyihasi: chipta sotib olish, seanslar, broniya.

## Loyiha tuzilishi

| Yo‘l | Vazifa |
|------|--------|
| `kinolar/` | Sozlamalar (`settings.py`), asosiy `urls.py`, `wsgi.py`, `asgi.py` |
| `apps/cinema/` | Filmlar, zallar, seanslar, broniya, veb sahifalar va oddiy JSON API (`/api/movies/` va hokazo) |
| `apps/control/` | `SiteSetting` modeli (admin orqali boshqariladi) |
| `templates/` | HTML shablonlar |
| `media/` | Yuklangan fayllar (posterlar) |

`DJANGO_SETTINGS_MODULE`: **`kinolar.settings`**.

## Ishga tushirish

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Brauzer: `http://127.0.0.1:8000/`

## Muhit o‘zgaruvchilari (xavfsizlik)

Loyiha ildizida `.env` yarating (namuna: `.env.example`).

| O‘zgaruvchi | Tavsif |
|-------------|--------|
| `SECRET_KEY` | Ishlab chiqarishda majburiy, uzun va tasodifiy qiymat |
| `DEBUG` | `False` serverda |
| `ALLOWED_HOSTS` | Vergul bilan ajratilgan domenlar (masalan `mysite.com,www.mysite.com`) |

## Testlar

```bash
python manage.py test apps.cinema
```

## Keyinroq yaxshilash g‘oyalari (hali qilinmagan)

- **To‘lov**: Click / Payme / karta — haqiqiy provayder API va webhook
- **Ma’lumotlar bazasi**: trafik oshsa PostgreSQL + indekslar
- **Kuzatuv**: `LOGGING`, xatoliklar uchun Sentry yoki shunga o‘xshash
- **HTTPS**: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_TRUSTED_ORIGINS`
- **Parol tiklash**: “Unutdingizmi?” havolasi uchun email orqali token

## Eslatma

- **Django REST Framework yo‘q** — JSON uchun `apps/cinema/views.py` dagi `JsonResponse` marshrutlar (`/api/movies/`, `/api/showtimes/<id>/`, …).
- Kod `apps.*` ostida; migratsiyalar `cinema` / `control` **label**lari bilan mos.
