from django.contrib import admin
from .models import Genre, Movie, Session, Ticket, Rating, Newsletter, PasswordResetCode


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


class SessionInline(admin.TabularInline):
    model = Session
    extra = 1
    fields = ('hall', 'starts_at', 'seats_total', 'seats_available')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'director', 'year', 'price', 'is_active', 'created_at', 'updated_at')
    list_filter = ('genre', 'is_active', 'year', 'created_at')
    search_fields = ('title', 'director')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'price')
    inlines = [SessionInline]
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'genre', 'director', 'year', 'duration', 'price', 'is_active')
        }),
        ('Контент', {
            'fields': ('description', 'poster')
        }),
        ('Системне', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'starts_at', 'seats_total', 'seats_available', 'created_at', 'updated_at')
    list_filter = ('hall', 'starts_at', 'movie__genre')
    search_fields = ('movie__title', 'hall')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'quantity', 'total_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'session__movie__title')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    list_editable = ('status',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'created_at', 'updated_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'movie__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_used', 'created_at')
    list_filter = ('is_used',)
    readonly_fields = ('created_at',)
