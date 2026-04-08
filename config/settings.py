# Add cinema app to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'cinema',
]

# Configure Templates Directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... existing context processors
            ],
        },
    },
]

# Add STATIC_ROOT setting
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add MEDIA settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
