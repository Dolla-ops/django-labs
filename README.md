# 🎬 CinemaUA — Django Project

Сайт кінотеатру. Django-проєкт для лабораторних робіт 3–8.

---

## 🚀 Запуск проєкту

```bash
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Зробити міграції
python manage.py makemigrations
python manage.py migrate

# 3. Створити суперкористувача (для адмін-панелі)
python manage.py createsuperuser

# 4. Зібрати статику
python manage.py collectstatic

# 5. Запустити сервер
python manage.py runserver
```

Після запуску:
- Сайт: http://127.0.0.1:8000/
- Адмін-панель: http://127.0.0.1:8000/admin/

---

## 📦 Структура проєкту

```
cinema_project/
├── manage.py
├── requirements.txt
├── .gitignore
├── cinemasite/             # Основний пакет Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── cinema/                 # Аплікація
    ├── models.py           # Моделі БД
    ├── admin.py            # Адмін-панель
    ├── views.py            # В'юшки
    ├── urls.py             # URL-маршрути
    ├── forms.py            # Форми
    ├── apps.py
    ├── context_processors.py
    ├── static/cinema/
    │   └── style.css       # Весь CSS (не в HTML!)
    └── templates/cinema/
        ├── base.html       # Базовий шаблон (DRY)
        ├── home.html
        ├── genre.html
        ├── movie.html
        ├── cart.html
        └── auth/
            ├── login.html
            ├── register.html
            ├── profile.html
            └── password_reset.html
```

---

## 📚 Лабораторні роботи

### Лаба 3 — Django аплікація + шаблон
- Створено аплікацію `cinema`
- Один базовий шаблон `base.html`
- Головна сторінка → посилання на всі жанри
- Сторінки жанрів → посилання назад на головну
- Рендер через `render()`, контекст через `context_processors`

### Лаба 4 — Моделі + Адмін-панель
**Таблиці (7 моделей):**
- `Genre` — жанри (категорії)
- `Movie` — фільми (ForeignKey → Genre)
- `Session` — сеанси (ForeignKey → Movie)
- `Ticket` — квитки (ForeignKey → User, Session)
- `Rating` — оцінки (ForeignKey → User, Movie)
- `Newsletter` — підписки на розсилку
- `PasswordResetCode` — коди для скидання паролю

**Адмін:** `list_display` включає `created_at`, `updated_at` для кожної моделі

### Лаба 5 — В'юшки + Шаблонізатор
- Головна сторінка через `views.py`
- Хедер з меню (жанри з БД) та футер — у `base.html`
- CSS — лише у `style.css`, не в HTML шаблонах
- `base.html` — всі інші шаблони розширюють його (`{% extends %}`)

### Лаба 6 — Сторінки товару і категорії
- `/genre/<slug>/` — фільми лише цього жанру
- `/movie/<slug>/` — деталі фільму, сеанси, кнопка "Купити"
- Фото фільмів через `ImageField` в БД

### Лаба 7 — Кошик + Форми
- `/cart/` — кошик з квитками
- `add_to_cart`, `remove_from_cart`, `checkout`
- Форма оцінки фільму (1-10 ⭐) + середній бал на сторінці
- Форма підписки на розсилку (на головній)

### Лаба 8 — Авторизація + Email
- `/register/` — реєстрація
- `/login/` — вхід (кнопка лише для неавторизованих)
- `/logout/` — вихід (кнопка лише для авторизованих)
- `/profile/` — замовлення юзера; адмін бачить всі замовлення
- `/password-reset/` — відновлення через email (6-значний код, 15 хв)

**DRY:** весь повторюваний HTML — у `base.html`, інші шаблони — `{% extends 'cinema/base.html' %}`

---

## ⚙️ Налаштування Email (для лаби 8)

В `settings.py`:
```python
# Розробка — виводить в консоль:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Продакшн — реальний SMTP:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🗄 Додати тестові дані через адмін-панель

1. Зайти на http://127.0.0.1:8000/admin/
2. Додати **Жанри**: Бойовик, Комедія, Жахи, Драма, Фантастика
3. Додати **Фільми** (мінімум 3) з постерами
4. Для кожного фільму додати **Сеанси** (інлайн в адмін-панелі фільму)
