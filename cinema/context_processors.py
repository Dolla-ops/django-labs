from .models import Genre, Ticket


def cart_count(request):
    """Кількість квитків у кошику — доступна на всіх сторінках."""
    count = 0
    if request.user.is_authenticated:
        count = Ticket.objects.filter(user=request.user, status='cart').count()
    return {'cart_count': count}


def genres_list(request):
    """Список жанрів для меню навігації — доступний на всіх сторінках."""
    return {'genres': Genre.objects.all()}
