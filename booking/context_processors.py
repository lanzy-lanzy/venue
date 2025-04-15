from .models import Category

def common_context(request):
    """
    Context processor to add common data to all templates.
    """
    return {
        'all_categories': Category.objects.all(),
    }
