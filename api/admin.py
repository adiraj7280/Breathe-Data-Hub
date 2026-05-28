from django.contrib import admin
from .models import Client, DataSource, DataUpload, NormalizedDataRecord, AuditLog

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'format_type')

@admin.register(DataUpload)
class DataUploadAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'client', 'source', 'uploaded_at')

@admin.register(NormalizedDataRecord)
class NormalizedDataRecordAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'scope_category', 'status', 'created_at')
    list_filter = ('status', 'scope_category', 'upload__source')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'timestamp')
    list_filter = ('action', 'user')
