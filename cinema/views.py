import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .models import Genre, Movie, Session, Ticket, Rating, Newsletter, PasswordResetCode
from .forms import (
    RatingForm, NewsletterForm, RegisterForm, LoginForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)


# ─── ЛАБА 5: Головна сторінка ────────────────────────────────────────────────
def home(request):
    """Головна сторінка: популярні фільми, жанри."""
    movies = Movie.objects.filter(is_active=True).select_related('genre')[:8]
    genres = Genre.objects.all()
    # Форма підписки на розсилку (Лаба 7)
    newsletter_form = NewsletterForm()
    if request.method == 'POST' and 'newsletter_submit' in request.POST:
        newsletter_form = NewsletterForm(request.POST)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data['email']
            if not Newsletter.objects.filter(email=email).exists():
                newsletter_form.save()
                messages.success(request, '✅ Ви успішно підписались на розсилку!')
            else:
                messages.info(request, 'Ця адреса вже підписана.')
            return redirect('home')
    return render(request, 'cinema/home.html', {
        'movies': movies,
        'genres': genres,
        'newsletter_form': newsletter_form,
    })


# ─── ЛАБА 5/6: Сторінка жанру (категорії) ───────────────────────────────────
def genre_detail(request, slug):
    """Сторінка жанру з фільмами лише цього жанру."""
    genre = get_object_or_404(Genre, slug=slug)
    movies = Movie.objects.filter(genre=genre, is_active=True).select_related('genre')
    return render(request, 'cinema/genre.html', {
        'genre': genre,
        'movies': movies,
    })


# ─── ЛАБА 6: Сторінка фільму (товару) ───────────────────────────────────────
def movie_detail(request, slug):
    """Детальна сторінка фільму з сеансами, оцінками, формою оцінки."""
    movie = get_object_or_404(Movie, slug=slug, is_active=True)
    sessions = movie.sessions.filter(starts_at__gte=timezone.now()).order_by('starts_at')
    ratings = movie.ratings.select_related('user').order_by('-created_at')
    avg = movie.avg_rating()

    # Перевірка чи поточний юзер вже оцінив
    user_rating = None
    rating_form = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, movie=movie).first()
        if not user_rating:
            rating_form = RatingForm()

    # POST: додати оцінку
    if request.method == 'POST' and 'rating_submit' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, 'Щоб оцінити фільм, увійдіть в акаунт.')
            return redirect('login')
        if user_rating:
            messages.error(request, 'Ви вже оцінили цей фільм.')
        else:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                r = rating_form.save(commit=False)
                r.user = request.user
                r.movie = movie
                r.save()
                messages.success(request, f'Дякуємо за оцінку: {r.score}/10!')
                return redirect('movie_detail', slug=slug)

    return render(request, 'cinema/movie.html', {
        'movie': movie,
        'sessions': sessions,
        'ratings': ratings,
        'avg': avg,
        'rating_form': rating_form,
        'user_rating': user_rating,
    })


# ─── ЛАБА 7: Кошик ──────────────────────────────────────────────────────────
@login_required
def cart(request):
    """Кошик: перегляд і керування квитками."""
    tickets = Ticket.objects.filter(
        user=request.user, status='cart'
    ).select_related('session__movie')
    total = sum(t.total_price for t in tickets)
    return render(request, 'cinema/cart.html', {
        'tickets': tickets,
        'total': total,
    })


@login_required
def add_to_cart(request, session_id):
    """Додати квиток до кошика."""
    session = get_object_or_404(Session, pk=session_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    if quantity > session.seats_available:
        messages.error(request, 'Недостатньо вільних місць.')
        return redirect('movie_detail', slug=session.movie.slug)

    ticket, created = Ticket.objects.get_or_create(
        user=request.user,
        session=session,
        status='cart',
        defaults={'quantity': quantity}
    )
    if not created:
        ticket.quantity += quantity
        ticket.save()

    messages.success(request, f'✅ {quantity} квиток(ів) додано до кошика!')
    return redirect('cart')


@login_required
def remove_from_cart(request, ticket_id):
    """Видалити квиток з кошика."""
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user, status='cart')
    ticket.delete()
    messages.success(request, 'Квиток видалено з кошика.')
    return redirect('cart')


@login_required
def checkout(request):
    """Оформити замовлення — переводимо кошик у статус 'ordered'."""
    tickets = Ticket.objects.filter(user=request.user, status='cart')
    if not tickets.exists():
        messages.error(request, 'Кошик порожній.')
        return redirect('cart')
    for ticket in tickets:
        if ticket.quantity <= ticket.session.seats_available:
            ticket.session.seats_available -= ticket.quantity
            ticket.session.save()
            ticket.status = 'ordered'
            ticket.save()
        else:
            messages.error(request, f'Недостатньо місць для "{ticket.session.movie.title}".')
            return redirect('cart')
    messages.success(request, '🎉 Замовлення оформлено! Чекайте на підтвердження.')
    return redirect('profile')


# ─── ЛАБА 8: Авторизація ─────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.username}!')
            return redirect('home')
    return render(request, 'cinema/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вітаємо, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    return render(request, 'cinema/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Ви вийшли з акаунту.')
    return redirect('home')


@login_required
def profile(request):
    """Особистий кабінет: замовлення юзера (адмін бачить всі)."""
    if request.user.is_staff:
        orders = Ticket.objects.filter(status='ordered').select_related(
            'user', 'session__movie'
        ).order_by('-created_at')
    else:
        orders = Ticket.objects.filter(
            user=request.user, status='ordered'
        ).select_related('session__movie').order_by('-created_at')
    total_spent = sum(o.total_price for o in orders)
    return render(request, 'cinema/auth/profile.html', {
        'orders': orders,
        'total_spent': total_spent,
    })


# ─── Лаба 8: Зміна пароля через email ───────────────────────────────────────
def password_reset_request(request):
    """Крок 1: ввести email, отримати код."""
    form = PasswordResetRequestForm()
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Акаунт з таким email не знайдено.')
                return render(request, 'cinema/auth/password_reset.html', {'form': form, 'step': 1})

            # Генеруємо 6-значний код
            code = ''.join(random.choices(string.digits, k=6))
            PasswordResetCode.objects.create(user=user, code=code)

            # Надсилаємо email (в DEBUG виводить у консоль)
            send_mail(
                subject='CinemaUA — код відновлення паролю',
                message=f'Ваш код для відновлення паролю: {code}\nКод дійсний 15 хвилин.',
                from_email='noreply@cinemaUA.com',
                recipient_list=[email],
            )
            messages.success(request, f'Код надіслано на {email}.')
            request.session['reset_email'] = email
            return redirect('password_reset_confirm')
    return render(request, 'cinema/auth/password_reset.html', {'form': form, 'step': 1})


def password_reset_confirm(request):
    """Крок 2: ввести код і новий пароль."""
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')

    form = PasswordResetConfirmForm()
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            code = form.cleaned_data['code']
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(email=email)
                reset_obj = PasswordResetCode.objects.filter(
                    user=user, code=code, is_used=False,
                    created_at__gte=timezone.now() - timedelta(minutes=15)
                ).last()
                if not reset_obj:
                    messages.error(request, 'Невірний або застарілий код.')
                    return render(request, 'cinema/auth/password_reset.html', {'form': form, 'step': 2})
                user.set_password(new_password)
                user.save()
                reset_obj.is_used = True
                reset_obj.save()
                del request.session['reset_email']
                messages.success(request, '✅ Пароль успішно змінено! Увійдіть з новим паролем.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Помилка. Спробуйте ще раз.')
    return render(request, 'cinema/auth/password_reset.html', {'form': form, 'step': 2})
