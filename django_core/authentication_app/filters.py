import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(field_name="email", lookup_expr="istartswith")
    full_name = django_filters.CharFilter(method="full_name_search")

    def full_name_search(self, qs: QuerySet, field_name: str, value: str) -> QuerySet:
        for name in value.split():
            qs = qs.filter(
                Q(first_name__icontains=name)
                | Q(last_name__icontains=name)
            )
        return qs

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
