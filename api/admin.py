from django.contrib import admin
from main.models import CustomUser, Project

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'date_created',)
    # Add other configurations or customizations if needed

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date_created',)
    # Add other configurations or customizations if needed

# Register your models with the custom admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project, ProjectAdmin)
