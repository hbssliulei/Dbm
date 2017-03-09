from django.db import models
import ast

class ListField(models.TextField):
    description = "store a list"

    def __init__(self, *args, **kwargs):
        self.value = None
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if not value:
            value = []

        if isinstance(value, list):
            print sorted(value)
            return sorted(value)

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if not value:
            return value
        return unicode(value)
