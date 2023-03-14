from django.db import models
import ast
import autofillout.models, changeservice.models


def delete_everything():
    autofillout.models.Saved_str.objects.all().delete()
    autofillout.models.Saved_list.objects.all().delete()
    autofillout.models.Saved_boo.objects.all().delete()
    changeservice.models.Saved_str.objects.all().delete()
    changeservice.models.Saved_list.objects.all().delete()
    changeservice.models.Saved_boo.objects.all().delete()

def made_context():
    context = {}
    for i in range(do_not_delete.objects.all().count()):
        context[do_not_delete.objects.all()[i].name] = do_not_delete.objects.all()[i].content
    return context



def savetodonotdelete(name, content):
    save = do_not_delete.objects.get_or_create(name = name)[0]
    save.content = content
    save.save()

# Create your models here.
class do_not_delete(models.Model):
    name = models.CharField(max_length=25,  primary_key=True)
    content = models.CharField(max_length=25, default = "", null=True)




