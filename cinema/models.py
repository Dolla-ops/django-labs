from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ─── Таблиця 1: Жанр ────────────────────────────────────────────────────────
class Genre(models.Model):
    name = models.CharField('Назва', max_length=100, unique=True)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Опис', blank=True)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── Таблиця 2: Фільм (пов'язаний з Жанром) ─────────────────────────────────
class Movie(models.Model):
    title = models.CharField('Назва', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE,
        verbose_name='Жанр', related_name='movies'
    )
    description = models.TextField('Опис')
    director = models.CharField('Режисер', max_length=150)
    year = models.PositiveIntegerField('Рік виходу')
    duration = models.PositiveIntegerField('Тривалість (хв)')
    poster = models.ImageField('Постер', upload_to='posters/', blank=True, null=True)
    price = models.DecimalField('Ціна квитка (грн)', max_digits=8, decimal_places=2)
    is_active = models.BooleanField('Активний', default=True)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Фільм'
        verbose_name_plural = 'Фільми'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.year})"

    def avg_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return None
        return round(sum(r.score for r in ratings) / len(ratings), 1)


# ─── Таблиця 3: Сеанс (пов'язаний з Фільмом) ────────────────────────────────
class Session(models.Model):
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE,
        verbose_name='Фільм', related_name='sessions'
    )
    hall = models.CharField('Зала', max_length=50)
    starts_at = models.DateTimeField('Початок сеансу')
    seats_total = models.PositiveIntegerField('Місць всього', default=100)
    seats_available = models.PositiveIntegerField('Доступних місць', default=100)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеанси'
        ordering = ['starts_at']

    def __str__(self):
        return f"{self.movie.title} — {self.starts_at.strftime('%d.%m.%Y %H:%M')}, {self.hall}"


# ─── Таблиця 4: Квиток (кошик / замовлення — Лаба 7, 8) ────────────────────
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('cart', 'В кошику'),
        ('ordered', 'Замовлено'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Скасовано'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Користувач', related_name='tickets'
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE,
        verbose_name='Сеанс', related_name='tickets'
    )
    quantity = models.PositiveIntegerField('Кількість квитків', default=1)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='cart')
    total_price = models.DecimalField('Сума (грн)', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Квиток'
        verbose_name_plural = 'Квитки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.session} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.session.movie.price * self.quantity
        super().save(*args, **kwargs)


# ─── Таблиця 5: Оцінка фільму (Лаба 7) ─────────────────────────────────────
class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Користувач', related_name='ratings'
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE,
        verbose_name='Фільм', related_name='ratings'
    )
    score = models.PositiveSmallIntegerField(
        'Оцінка (1-10)',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField('Коментар', blank=True)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Оцінка'
        verbose_name_plural = 'Оцінки'
        unique_together = ('user', 'movie')  # один юзер — одна оцінка на фільм

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}: {self.score}/10"


# ─── Таблиця 6: Підписка на розсилку (Лаба 7) ──────────────────────────────
class Newsletter(models.Model):
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Ім\'я', max_length=100, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено о', auto_now=True)

    class Meta:
        verbose_name = 'Підписка на розсилку'
        verbose_name_plural = 'Підписки на розсилку'

    def __str__(self):
        return self.email


# ─── Таблиця 7: Код відновлення паролю (Лаба 8) ─────────────────────────────
class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField('Код', max_length=6)
    is_used = models.BooleanField('Використано', default=False)
    created_at = models.DateTimeField('Створено о', auto_now_add=True)

    class Meta:
        verbose_name = 'Код відновлення паролю'
        verbose_name_plural = 'Коди відновлення паролю'

    def __str__(self):
        return f"{self.user.username} — {self.code}"
