import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from booking.models import Category, VenueManager, Venue, TimeSlot, Booking


class Command(BaseCommand):
    help = 'Creates sample data for the venue booking system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create categories
        self.create_categories()
        
        # Create users and managers
        self.create_users_and_managers()
        
        # Create venues
        self.create_venues()
        
        # Create time slots
        self.create_time_slots()
        
        # Create bookings
        self.create_bookings()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
    
    def create_categories(self):
        categories = [
            'Conference Room',
            'Wedding Venue',
            'Party Hall',
            'Meeting Room',
            'Workshop Space',
            'Outdoor Venue',
            'Studio',
            'Auditorium',
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Venues suitable for {category_name.lower()}'}
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
    
    def create_users_and_managers(self):
        # Create admin user if it doesn't exist
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin)'))
        
        # Create regular users
        regular_users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': f'User {i}',
                    'last_name': 'Test',
                }
            )
            
            if created:
                user.set_password('password')
                user.save()
                regular_users.append(user)
        
        if regular_users:
            self.stdout.write(self.style.SUCCESS(f'Created {len(regular_users)} regular users (password: password)'))
        
        # Create venue managers
        manager_users = []
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'manager{i}',
                defaults={
                    'email': f'manager{i}@example.com',
                    'first_name': f'Manager {i}',
                    'last_name': 'Test',
                    'is_staff': True,
                }
            )
            
            if created:
                user.set_password('password')
                user.save()
                manager_users.append(user)
                
                # Create venue manager profile
                VenueManager.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': f'555-555-{1000+i}',
                        'company_name': f'Venue Company {i}',
                        'is_approved': True,
                    }
                )
        
        if manager_users:
            self.stdout.write(self.style.SUCCESS(f'Created {len(manager_users)} venue managers (password: password)'))
    
    def create_venues(self):
        managers = VenueManager.objects.all()
        categories = Category.objects.all()
        
        if not managers:
            self.stdout.write(self.style.WARNING('No venue managers found. Skipping venue creation.'))
            return
        
        venue_data = [
            {
                'name': 'Grand Conference Center',
                'description': 'A spacious conference center with state-of-the-art facilities.',
                'address': '123 Main St, New York, NY 10001',
                'capacity': 500,
                'hourly_rate': 200.00,
            },
            {
                'name': 'Elegant Wedding Hall',
                'description': 'A beautiful venue perfect for weddings and receptions.',
                'address': '456 Park Ave, New York, NY 10002',
                'capacity': 300,
                'hourly_rate': 250.00,
            },
            {
                'name': 'Downtown Meeting Rooms',
                'description': 'Professional meeting rooms in the heart of downtown.',
                'address': '789 Broadway, New York, NY 10003',
                'capacity': 50,
                'hourly_rate': 75.00,
            },
            {
                'name': 'Creative Studio Space',
                'description': 'A versatile studio space for workshops, photoshoots, and small events.',
                'address': '101 Creative Blvd, Brooklyn, NY 11201',
                'capacity': 30,
                'hourly_rate': 60.00,
            },
            {
                'name': 'Rooftop Event Space',
                'description': 'A stunning rooftop venue with panoramic city views.',
                'address': '202 Skyline Dr, New York, NY 10004',
                'capacity': 150,
                'hourly_rate': 180.00,
            },
            {
                'name': 'Garden Party Venue',
                'description': 'A charming outdoor venue with beautiful gardens.',
                'address': '303 Garden Rd, Queens, NY 11101',
                'capacity': 200,
                'hourly_rate': 150.00,
            },
        ]
        
        venues_created = 0
        for data in venue_data:
            venue, created = Venue.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'address': data['address'],
                    'capacity': data['capacity'],
                    'hourly_rate': data['hourly_rate'],
                    'manager': random.choice(managers),
                    'status': random.choice(['active', 'active', 'active', 'maintenance', 'inactive']),
                }
            )
            
            if created:
                venues_created += 1
                # Add random categories
                venue.categories.add(*random.sample(list(categories), k=random.randint(1, 3)))
        
        self.stdout.write(self.style.SUCCESS(f'Created {venues_created} venues'))
    
    def create_time_slots(self):
        venues = Venue.objects.filter(status='active')
        
        if not venues:
            self.stdout.write(self.style.WARNING('No active venues found. Skipping time slot creation.'))
            return
        
        # Create time slots for the next 14 days
        today = timezone.now().date()
        time_slots_created = 0
        
        for venue in venues:
            for day_offset in range(14):
                slot_date = today + timedelta(days=day_offset)
                
                # Create 2-4 time slots per day
                for _ in range(random.randint(2, 4)):
                    # Random start hour between 8 AM and 6 PM
                    start_hour = random.randint(8, 18)
                    # Duration between 1-3 hours
                    duration = random.randint(1, 3)
                    
                    start_time = datetime.strptime(f"{start_hour}:00", "%H:%M").time()
                    end_time = datetime.strptime(f"{start_hour + duration}:00", "%H:%M").time()
                    
                    # 80% chance of being available
                    is_available = random.random() < 0.8
                    
                    time_slot, created = TimeSlot.objects.get_or_create(
                        venue=venue,
                        date=slot_date,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'is_available': is_available,
                        }
                    )
                    
                    if created:
                        time_slots_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {time_slots_created} time slots'))
    
    def create_bookings(self):
        users = User.objects.filter(is_staff=False)
        time_slots = TimeSlot.objects.filter(is_available=True)
        
        if not users:
            self.stdout.write(self.style.WARNING('No regular users found. Skipping booking creation.'))
            return
        
        if not time_slots:
            self.stdout.write(self.style.WARNING('No available time slots found. Skipping booking creation.'))
            return
        
        # Create 10-20 random bookings
        num_bookings = random.randint(10, 20)
        bookings_created = 0
        
        for _ in range(num_bookings):
            # Get a random time slot and mark it as unavailable
            time_slot = random.choice(time_slots)
            time_slot.is_available = False
            time_slot.save()
            
            # Calculate total price
            hours = (time_slot.end_time.hour - time_slot.start_time.hour)
            total_price = time_slot.venue.hourly_rate * hours
            
            # Create booking
            booking, created = Booking.objects.get_or_create(
                user=random.choice(users),
                time_slot=time_slot,
                defaults={
                    'venue': time_slot.venue,
                    'num_guests': random.randint(5, time_slot.venue.capacity),
                    'status': random.choice(['pending', 'confirmed', 'confirmed', 'cancelled']),
                    'special_requests': random.choice([
                        'Please provide a projector.',
                        'We need extra chairs.',
                        'Please arrange for catering.',
                        '',
                        '',
                    ]),
                    'total_price': total_price,
                }
            )
            
            if created:
                bookings_created += 1
                # Update time slot availability based on booking status
                if booking.status == 'cancelled':
                    time_slot.is_available = True
                    time_slot.save()
        
        self.stdout.write(self.style.SUCCESS(f'Created {bookings_created} bookings'))
