from django.contrib import admin
from webapp.models import Case, Step, Task

class CaseAdmin(admin.ModelAdmin):
    pass

class TaskAdmin(admin.ModelAdmin):
    pass

class StepAdmin(admin.ModelAdmin):
    pass
    

admin.site.register(Case, CaseAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Step, StepAdmin)

