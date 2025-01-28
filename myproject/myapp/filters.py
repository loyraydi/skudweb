import django_filters
from .models import СustomUser


class UserFilter(django_filters.FilterSet):
    user_name = django_filters.CharFilter(lookup_expr='icontains', label='ФИО')
    access_level = django_filters.CharFilter(lookup_expr='icontains', label='Уровень доступа')

    class Meta:
        model = СustomUser
        fields = ['user_name', 'access_level']
