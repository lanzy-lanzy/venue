"""
Utility functions for generating reports.
"""
import io
import datetime
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from django.db.models import Sum, Count
from django.utils import timezone


def generate_sales_report_pdf(manager, start_date=None, end_date=None, venue_id=None):
    """
    Generate a sales report PDF for a venue manager.

    Args:
        manager: The VenueManager instance
        start_date: Optional start date for filtering (datetime.date)
        end_date: Optional end date for filtering (datetime.date)
        venue_id: Optional venue ID for filtering

    Returns:
        BytesIO object containing the PDF
    """
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center alignment
    subtitle_style = styles['Heading2']
    subtitle_style.alignment = 1  # Center alignment
    normal_style = styles['Normal']

    # Create a custom style for the table header
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=1  # Center alignment
    )

    # Create story (list of flowables)
    story = []

    # Add title
    story.append(Paragraph("Sales Report", title_style))

    # Add date range subtitle
    if start_date and end_date:
        date_range = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    else:
        date_range = "All Time"

    story.append(Paragraph(f"Date Range: {date_range}", subtitle_style))
    story.append(Spacer(1, 0.25*inch))

    # Add manager info
    story.append(Paragraph(f"Manager: {manager.user.get_full_name() or manager.user.username}", normal_style))
    if manager.company_name:
        story.append(Paragraph(f"Company: {manager.company_name}", normal_style))
    story.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y, %I:%M %p')}", normal_style))
    story.append(Spacer(1, 0.25*inch))

    # Get venues managed by the manager
    venues = manager.managed_venues.all()
    if venue_id:
        venues = venues.filter(id=venue_id)

    # Filter bookings by date range if provided
    booking_filter = {'venue__in': venues, 'status': 'confirmed'}
    if start_date:
        booking_filter['time_slot__date__gte'] = start_date
    if end_date:
        booking_filter['time_slot__date__lte'] = end_date

    # Get bookings
    from booking.models import Booking, Payment
    bookings = Booking.objects.filter(**booking_filter).order_by('time_slot__date')

    # Get payments
    payment_filter = {'booking__venue__in': venues, 'status': 'completed'}
    if start_date:
        payment_filter['payment_date__date__gte'] = start_date
    if end_date:
        payment_filter['payment_date__date__lte'] = end_date

    payments = Payment.objects.filter(**payment_filter)

    # Summary statistics
    total_bookings = bookings.count()
    total_revenue = bookings.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Add summary statistics
    summary_data = [
        ["Total Bookings", str(total_bookings)],
        ["Total Revenue", f"₱{total_revenue:.2f}"],
        ["Total Payments Received", f"₱{total_payments:.2f}"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.25*inch))

    # Venue breakdown
    story.append(Paragraph("Revenue by Venue", subtitle_style))
    story.append(Spacer(1, 0.1*inch))

    venue_data = [["Venue", "Bookings", "Revenue"]]

    # Chart data
    chart_data = []
    chart_labels = []

    for venue in venues:
        venue_bookings = bookings.filter(venue=venue)
        booking_count = venue_bookings.count()
        venue_revenue = venue_bookings.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        venue_data.append([
            venue.name,
            str(booking_count),
            f"₱{venue_revenue:.2f}"
        ])

        if booking_count > 0:
            chart_data.append(float(venue_revenue))
            chart_labels.append(venue.name)

    venue_table = Table(venue_data, colWidths=[4*inch, 1.5*inch, 1.5*inch])
    venue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(venue_table)
    story.append(Spacer(1, 0.25*inch))

    # Add bar chart for venue revenue
    if chart_data:
        story.append(Paragraph("Revenue by Venue (Chart)", subtitle_style))
        story.append(Spacer(1, 0.1*inch))

        drawing = Drawing(600, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 500
        bc.data = [chart_data]
        bc.strokeColor = colors.black
        bc.valueAxis.valueMin = 0

        # Handle case when there's data but all values are 0
        if max(chart_data) > 0:
            bc.valueAxis.valueMax = max(chart_data) * 1.1
            bc.valueAxis.valueStep = max(chart_data) / 5
        else:
            bc.valueAxis.valueMax = 100
            bc.valueAxis.valueStep = 20

        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.categoryNames = chart_labels
        bc.bars[0].fillColor = colors.darkblue

        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 0.25*inch))

    # Recent bookings table
    story.append(Paragraph("Recent Confirmed Bookings", subtitle_style))
    story.append(Spacer(1, 0.1*inch))

    # Get the 10 most recent bookings
    recent_bookings = bookings.order_by('-booking_date')[:10]

    if recent_bookings:
        booking_data = [["Booking ID", "Customer", "Venue", "Date", "Time", "Amount"]]

        for booking in recent_bookings:
            booking_data.append([
                f"#{booking.id}",
                booking.user.get_full_name() or booking.user.username,
                booking.venue.name,
                booking.time_slot.date.strftime('%b %d, %Y'),
                f"{booking.time_slot.start_time.strftime('%I:%M %p')} - {booking.time_slot.end_time.strftime('%I:%M %p')}",
                f"₱{booking.total_price:.2f}"
            ])

        booking_table = Table(booking_data, colWidths=[0.75*inch, 2*inch, 2*inch, 1*inch, 2*inch, 1*inch])
        booking_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(booking_table)
    else:
        story.append(Paragraph("No bookings found for the selected criteria.", normal_style))

    # Build the PDF
    doc.build(story)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
