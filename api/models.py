from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DataSource(models.Model):
    name = models.CharField(max_length=100) # e.g., 'SAP', 'Utility', 'Concur'
    format_type = models.CharField(max_length=50) # e.g., 'CSV'
    
    def __str__(self):
        return self.name

class DataUpload(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)

class NormalizedDataRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged for Issues')
    ]

    SCOPE_CHOICES = [
        ('Scope 1', 'Scope 1'),
        ('Scope 2', 'Scope 2'),
        ('Scope 3', 'Scope 3')
    ]

    upload = models.ForeignKey(DataUpload, on_delete=models.CASCADE, related_name='records')
    scope_category = models.CharField(max_length=50, choices=SCOPE_CHOICES)
    activity_type = models.CharField(max_length=100, db_index=True) # e.g., 'Fuel', 'Electricity', 'Flight'
    activity_date_start = models.DateField(null=True, blank=True, db_index=True)
    activity_date_end = models.DateField(null=True, blank=True)
    original_value = models.FloatField(null=True, blank=True)
    original_unit = models.CharField(max_length=50, null=True, blank=True)
    normalized_value = models.FloatField(null=True, blank=True)
    normalized_unit = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    issues = models.JSONField(default=dict, blank=True)
    raw_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.activity_type} - {self.status}"

class AuditLog(models.Model):
    record = models.ForeignKey(NormalizedDataRecord, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    changes = models.JSONField(default=dict, blank=True)
    user = models.CharField(max_length=100, default='System')

    def __str__(self):
        return f"{self.record.id} - {self.action} at {self.timestamp}"
