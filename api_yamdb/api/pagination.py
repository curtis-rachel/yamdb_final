from rest_framework.pagination import PageNumberPagination


class MyPaginator(PageNumberPagination):
    page_size = 5
