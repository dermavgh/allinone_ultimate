from django.db import models
import ast
from login_app.models import *

class ListField(models.TextField):

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

def delete_everything():
    Saved_str.objects.all().delete()
    Saved_list.objects.all().delete()
    Saved_boo.objects.all().delete()

def made_context():
    context = {}
    for i in range(Saved_list.objects.all().count()):
        context[Saved_list.objects.all()[i].name] = Saved_list.objects.all()[i].content
    for i in range(Saved_str.objects.all().count()):
        context[Saved_str.objects.all()[i].name] = Saved_str.objects.all()[i].content
    for i in range(Saved_boo.objects.all().count()):
        context[Saved_boo.objects.all()[i].name] = Saved_boo.objects.all()[i].content
    return context


def savetolist(name, content):
    save = Saved_list.objects.get_or_create(name = name)[0]
    save.content = content
    save.save()

def savetostring(name, content):
    save = Saved_str.objects.get_or_create(name = name)[0]
    save.content = content
    save.save()

def savetoboo(name, content):
    save = Saved_boo.objects.get_or_create(name = name)[0]
    save.content = content
    save.save()


# Create your models here.
class Saved_list(models.Model):
    name = models.CharField(max_length=25, primary_key=True)
    content = ListField(default = [], null= True)

class Saved_str(models.Model):
    name = models.CharField(max_length=25,  primary_key=True)
    content = models.CharField(max_length=25, default = "", null=True)


class Saved_boo(models.Model):
    name = models.CharField(max_length=25,  primary_key=True)
    content = models.BooleanField(null=True)


