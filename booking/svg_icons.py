"""
SVG icons for the venue booking system.
This module contains SVG icons as functions that return SVG markup.
"""

def venue_placeholder():
    """SVG placeholder for venues without images."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-gray-400">
        <rect width="18" height="14" x="3" y="5" rx="2" />
        <circle cx="12" cy="12" r="3" />
        <path d="M3 12h.01M21 12h.01M12 3v.01M12 21v.01M7.5 3h9M7.5 21h9" />
    </svg>
    '''

def conference_room():
    """SVG icon for conference room venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-indigo-600">
        <rect width="18" height="12" x="3" y="6" rx="2" />
        <path d="M7 12h10M7 9h2M7 15h2M15 9h2M15 15h2" />
    </svg>
    '''

def wedding_venue():
    """SVG icon for wedding venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-pink-600">
        <path d="M12 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
        <path d="M8 14a6 6 0 0 0 8 0M18 18l-2-2M6 18l2-2" />
        <path d="M12 2v2M12 20v2M4 12H2M22 12h-2" />
    </svg>
    '''

def party_hall():
    """SVG icon for party hall venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-purple-600">
        <path d="M5.8 11.3 2 22l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1-3.8-10.7" />
        <path d="M12 2a6 6 0 0 0-6 6c0 1.5 1 3 3 4l3 2 3-2c2-1 3-2.5 3-4a6 6 0 0 0-6-6z" />
    </svg>
    '''

def meeting_room():
    """SVG icon for meeting room venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-blue-600">
        <rect width="16" height="16" x="4" y="4" rx="2" />
        <path d="M9 15v-6h6v6" />
        <path d="M9 9h6" />
    </svg>
    '''

def workshop_space():
    """SVG icon for workshop space venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-yellow-600">
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
    </svg>
    '''

def outdoor_venue():
    """SVG icon for outdoor venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-green-600">
        <path d="M2 22h20M12 2v8M2 12h20M12 18v4M7 12v4M17 12v4M7 2v4M17 2v4" />
    </svg>
    '''

def studio():
    """SVG icon for studio venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-red-600">
        <circle cx="12" cy="12" r="7" />
        <circle cx="12" cy="12" r="3" />
        <path d="M12 5v-2M12 21v-2M5 12h-2M21 12h-2M5 19l-1.5 1.5M5 5l-1.5-1.5M19 19l1.5 1.5M19 5l1.5-1.5" />
    </svg>
    '''

def auditorium():
    """SVG icon for auditorium venues."""
    return '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" 
         class="w-full h-full text-teal-600">
        <path d="M3 12h18M3 6h18M3 18h18" />
        <path d="M7 6v12M17 6v12" />
    </svg>
    '''

# Dictionary mapping category names to SVG functions
CATEGORY_ICONS = {
    'Conference Room': conference_room,
    'Wedding Venue': wedding_venue,
    'Party Hall': party_hall,
    'Meeting Room': meeting_room,
    'Workshop Space': workshop_space,
    'Outdoor Venue': outdoor_venue,
    'Studio': studio,
    'Auditorium': auditorium,
}

def get_icon_for_category(category_name):
    """Get the SVG icon function for a category name."""
    return CATEGORY_ICONS.get(category_name, venue_placeholder)
