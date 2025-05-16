from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Venue, TimeSlot, Booking, Category, VenueManager, UserProfile, Payment


class VenueForm(forms.ModelForm):
    """
    Form for creating and updating venues.
    """
    class Meta:
        model = Venue
        fields = ['name', 'description', 'address', 'capacity', 'hourly_rate', 'image', 'categories', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'categories': forms.CheckboxSelectMultiple(),
        }


class TimeSlotForm(forms.ModelForm):
    """
    Form for creating and updating time slots.
    """
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time', 'is_available']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        """
        Custom validation to ensure end_time is after start_time.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data


class BookingForm(forms.ModelForm):
    """
    Form for creating and updating bookings.
    """
    class Meta:
        model = Booking
        fields = ['time_slot', 'num_guests', 'special_requests']
        widgets = {
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }


class VenueManagerForm(forms.ModelForm):
    """
    Form for updating venue manager profile.
    """
    class Meta:
        model = VenueManager
        fields = ['phone', 'company_name']


class VenueSearchForm(forms.Form):
    """
    Form for searching and filtering venues.
    """
    search = forms.CharField(required=False, label='Search')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Category',
        empty_label='All Categories'
    )
    min_capacity = forms.IntegerField(required=False, label='Min Capacity')
    min_price = forms.DecimalField(required=False, label='Min Price')
    max_price = forms.DecimalField(required=False, label='Max Price')


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone', 'address', 'preferred_payment_method', 'booking_preferences']
        widgets = {
            'booking_preferences': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email


class RegistrationForm(UserCreationForm):
    """
    Form for user registration with additional fields.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class PaymentForm(forms.ModelForm):
    """
    Form for submitting payments for bookings.
    """
    class Meta:
        model = Payment
        fields = ['payment_method', 'reference_number', 'payment_proof', 'notes']
        widgets = {
            'payment_method': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent',
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent',
                'placeholder': 'Enter your GCash reference number',
            }),
            'payment_proof': forms.FileInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent',
                'accept': 'image/*',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent',
                'rows': 3,
                'placeholder': 'Any additional information about your payment',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set GCash as the default payment method
        if 'payment_method' in self.fields:
            self.fields['payment_method'].initial = 'gcash'
