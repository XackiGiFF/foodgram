from rest_framework.pagination import PageNumberPagination

from api.manager.conf import PAGE_SIZE_COUNT


class PageLimitPagination(PageNumberPagination):
    """
    Стандартный пагинатор с определением атрибута
    `page_size_query_param`, для вывода запрошенного количества страниц.
    """
    page_size = PAGE_SIZE_COUNT
    page_size_query_param = 'limit'
