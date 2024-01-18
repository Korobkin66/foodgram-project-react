from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

    def paginate_queryset(self, queryset, request, view=None):
       if queryset is not None:
           queryset = queryset.order_by('id')
       return super().paginate_queryset(queryset, request, view)