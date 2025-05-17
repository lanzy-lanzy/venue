from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from booking.models import Booking, Payment
from booking.forms import PaymentForm


@login_required
def submit_payment(request, booking_id):
    """
    View for submitting a payment for a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if booking is confirmed
    if booking.status != 'confirmed':
        messages.error(request, 'You can only make payments for confirmed bookings.')
        return redirect('booking_detail', booking_id=booking.id)

    # Check if this is a free venue (no payment required)
    if booking.is_free_venue():
        messages.info(request, 'This is a free venue. No payment is required.')
        return redirect('booking_detail', booking_id=booking.id)

    # Check if payment already exists
    existing_payment = Payment.objects.filter(booking=booking, status='completed').first()
    if existing_payment:
        messages.info(request, 'This booking has already been paid.')
        return redirect('payment_detail', payment_id=existing_payment.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price
            payment.save()

            messages.success(request, 'Payment submitted successfully! We will verify your payment shortly.')
            return redirect('payment_detail', payment_id=payment.id)
    else:
        form = PaymentForm()

    context = {
        'booking': booking,
        'form': form,
    }
    return render(request, 'booking/payment_form.html', context)


@login_required
def payment_detail(request, payment_id):
    """
    View for displaying payment details.
    """
    payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)

    context = {
        'payment': payment,
    }
    return render(request, 'booking/payment_detail.html', context)


@login_required
def payment_history(request):
    """
    View for displaying payment history for the current user.
    """
    payments = Payment.objects.filter(booking__user=request.user).order_by('-payment_date')

    context = {
        'payments': payments,
    }
    return render(request, 'booking/payment_history.html', context)
