from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import UserProfile, VenueManager


class Command(BaseCommand):
    help = 'Creates missing user profiles for existing users'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Checking for users without profiles...'))
        
        # Get all users
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            # Check if user has a profile
            if not hasattr(user, 'profile'):
                # Create profile for non-staff users
                if not user.is_staff:
                    UserProfile.objects.create(user=user)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
            
            # Check if staff user has a venue manager profile
            if user.is_staff and not hasattr(user, 'venue_manager'):
                VenueManager.objects.create(user=user, is_approved=True)
                self.stdout.write(self.style.SUCCESS(f'Created venue manager profile for staff user: {user.username}'))
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} user profiles'))
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
