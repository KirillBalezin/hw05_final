from django.core.paginator import Paginator
from django.conf import settings


def paginate(request, post_list, paginate_page=settings.PAGINATE_PAGE):
    paginator = Paginator(post_list, paginate_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
