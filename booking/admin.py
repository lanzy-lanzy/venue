from django.contrib import admin
from .models import Venue, Category, TimeSlot, Booking, VenueManager, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity', 'hourly_rate', 'manager', 'status', 'created_at')
    list_filter = ('categories', 'status', 'manager')
    search_fields = ('name', 'address', 'manager__user__username')
    filter_horizontal = ('categories',)
    raw_id_fields = ('manager',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available', 'venue')
    search_fields = ('venue__name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'time_slot', 'num_guests', 'status', 'total_price', 'booking_date')
    list_filter = ('status', 'booking_date', 'venue')
    search_fields = ('user__username', 'venue__name')
    readonly_fields = ('booking_date',)


@admin.register(VenueManager)
class VenueManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone', 'is_approved', 'get_venues_count', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name')
    readonly_fields = ('created_at',)

    def get_venues_count(self, obj):
        return obj.managed_venues.count()

    get_venues_count.short_description = 'Venues'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
