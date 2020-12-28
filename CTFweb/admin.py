from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.User)
admin.site.register(models.Team)
admin.site.register(models.Problem)
admin.site.register(models.Answer_Ship)
admin.site.register(models.Problem_Team_Ship)
admin.site.register(models.problem_solution)
admin.site.register(models.user_application)
admin.site.register(models.captcha)
