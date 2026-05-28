from rest_framework import serializers
from .models import Client, DataSource, DataUpload, NormalizedDataRecord, AuditLog

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class NormalizedDataRecordSerializer(serializers.ModelSerializer):
    audit_logs = AuditLogSerializer(many=True, read_only=True)
    source_name = serializers.CharField(source='upload.source.name', read_only=True)
    client_name = serializers.CharField(source='upload.client.name', read_only=True)

    class Meta:
        model = NormalizedDataRecord
        fields = '__all__'

class DataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUpload
        fields = '__all__'
