from django.contrib import admin
from lms_app.models import *


# Register your models here.

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Department)
admin.site.register(Book)
admin.site.register(BookIssueDetail)
