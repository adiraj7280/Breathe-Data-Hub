import csv
import json
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Client, DataSource, DataUpload, NormalizedDataRecord, AuditLog
from .serializers import NormalizedDataRecordSerializer
from datetime import datetime
import io

class NormalizedDataRecordViewSet(viewsets.ModelViewSet):
    queryset = NormalizedDataRecord.objects.all().order_by('-created_at')
    serializer_class = NormalizedDataRecordSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        response = super().update(request, *args, **kwargs)
        
        # Log status change or edits
        new_status = response.data.get('status')
        if old_status != new_status:
            AuditLog.objects.create(
                record=instance,
                action=f"STATUS_CHANGED_TO_{new_status}",
                changes={'old_status': old_status, 'new_status': new_status}
            )
        else:
            AuditLog.objects.create(
                record=instance,
                action="RECORD_EDITED",
                changes={'details': 'Fields updated by analyst'}
            )
        return response


class InitialDataSetupView(APIView):
    def post(self, request):
        client = Client.objects.filter(name="Acme Corp").first()
        if not client:
            client = Client.objects.create(name="Acme Corp")
            
        for source in ["SAP", "Utility", "Travel"]:
            if not DataSource.objects.filter(name=source).exists():
                DataSource.objects.create(name=source, format_type="CSV")
                
        return Response({"message": "Setup complete"})

class UploadDataView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        source_name = request.data.get('source') # 'SAP', 'Utility', 'Travel'
        
        if not file or not source_name:
            return Response({"error": "File and source are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.first()
            source = DataSource.objects.get(name__icontains=source_name)
        except DataSource.DoesNotExist:
            return Response({"error": "Invalid source"}, status=status.HTTP_400_BAD_REQUEST)

        file_content = file.read()
        try:
            decoded_file = file_content.decode('utf-8')
        except UnicodeDecodeError:
            decoded_file = file_content.decode('latin-1')
            
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        # Strict Header Validation to prevent uploading the wrong file
        headers = reader.fieldnames if reader.fieldnames else []
        if 'sap' in source_name.lower():
            if not any(h for h in headers if h in ['BUDAT', 'MENGE', 'MEINS']):
                return Response({"error": "Mismatched Data! This doesn't look like an SAP export. Did you forget to change the Data Source dropdown?"}, status=status.HTTP_400_BAD_REQUEST)
        elif 'utility' in source_name.lower():
            if not any(h for h in headers if h in ['Usage', 'Bill_Start_Date', 'Account_Number']):
                return Response({"error": "Mismatched Data! This doesn't look like a Utility export. Did you forget to change the Data Source dropdown?"}, status=status.HTTP_400_BAD_REQUEST)
        elif 'travel' in source_name.lower() or 'concur' in source_name.lower() or 'navan' in source_name.lower():
            if not any(h for h in headers if h in ['Origin_IATA', 'Distance', 'Travel_Date']):
                return Response({"error": "Mismatched Data! This doesn't look like a Travel export. Did you forget to change the Data Source dropdown?"}, status=status.HTTP_400_BAD_REQUEST)

        # Validation passed. Now safe to clear existing data for this source
        DataUpload.objects.filter(client=client, source=source).delete()

        upload = DataUpload.objects.create(client=client, source=source, file_name=file.name)
        
        records_created = 0
        
        for row in reader:
            record_kwargs = {
                'upload': upload,
                'raw_data': row,
                'status': 'PENDING'
            }
            issues = {}
            
            # Normalization logic per source
            if 'sap' in source_name.lower():
                record_kwargs['scope_category'] = 'Scope 1'
                record_kwargs['activity_type'] = 'Fuel'
                try:
                    record_kwargs['activity_date_start'] = datetime.strptime(row.get('BUDAT', ''), '%Y-%m-%d').date()
                    record_kwargs['activity_date_end'] = record_kwargs['activity_date_start']
                except ValueError:
                    issues['date'] = 'Missing/Invalid Posting Date (BUDAT)'

                val = row.get('MENGE', 0)
                try:
                    record_kwargs['original_value'] = float(val)
                except ValueError:
                    issues['value'] = f"Invalid amount MENGE: {val}"
                    record_kwargs['status'] = 'FLAGGED'
                
                unit = row.get('MEINS', '').upper()
                record_kwargs['original_unit'] = unit
                
                # Normalize units to Liters
                if unit == 'GAL':
                    record_kwargs['normalized_value'] = record_kwargs.get('original_value', 0) * 3.78541
                    record_kwargs['normalized_unit'] = 'Liters'
                elif unit == 'L':
                    record_kwargs['normalized_value'] = record_kwargs.get('original_value', 0)
                    record_kwargs['normalized_unit'] = 'Liters'
                else:
                    issues['unit'] = f"Unknown unit {unit}, cannot normalize"
                    record_kwargs['status'] = 'FLAGGED'

            elif 'utility' in source_name.lower():
                record_kwargs['scope_category'] = 'Scope 2'
                record_kwargs['activity_type'] = 'Electricity'
                try:
                    record_kwargs['activity_date_start'] = datetime.strptime(row.get('Bill_Start_Date', ''), '%Y-%m-%d').date()
                    record_kwargs['activity_date_end'] = datetime.strptime(row.get('Bill_End_Date', ''), '%Y-%m-%d').date()
                except ValueError:
                    issues['date'] = 'Missing or invalid billing periods'
                    record_kwargs['status'] = 'FLAGGED'
                
                val = row.get('Usage', 0)
                try:
                    record_kwargs['original_value'] = float(val)
                except ValueError:
                    issues['value'] = f"Invalid usage: {val}"
                    record_kwargs['status'] = 'FLAGGED'
                
                unit = row.get('Unit', '').upper()
                record_kwargs['original_unit'] = unit
                
                if unit == 'KWH':
                    record_kwargs['normalized_value'] = record_kwargs.get('original_value', 0)
                    record_kwargs['normalized_unit'] = 'kWh'
                elif unit == 'MWH':
                    record_kwargs['normalized_value'] = record_kwargs.get('original_value', 0) * 1000
                    record_kwargs['normalized_unit'] = 'kWh'
                else:
                    issues['unit'] = f"Unknown unit {unit}"
                    record_kwargs['status'] = 'FLAGGED'

            elif 'travel' in source_name.lower():
                record_kwargs['scope_category'] = 'Scope 3'
                record_kwargs['activity_type'] = 'Flight'
                try:
                    record_kwargs['activity_date_start'] = datetime.strptime(row.get('Travel_Date', ''), '%Y-%m-%d').date()
                    record_kwargs['activity_date_end'] = record_kwargs['activity_date_start']
                except ValueError:
                    issues['date'] = 'Invalid Travel_Date'
                
                dist = row.get('Distance', '')
                if dist:
                    try:
                        record_kwargs['original_value'] = float(dist)
                        record_kwargs['normalized_value'] = record_kwargs['original_value']
                        record_kwargs['original_unit'] = 'miles'
                        record_kwargs['normalized_unit'] = 'miles'
                    except ValueError:
                        issues['value'] = 'Invalid distance'
                        record_kwargs['status'] = 'FLAGGED'
                else:
                    origin = row.get('Origin_IATA')
                    dest = row.get('Dest_IATA')
                    if origin and dest:
                        issues['distance'] = f"Distance missing. Need to calculate {origin} to {dest}"
                        record_kwargs['status'] = 'FLAGGED'
                        record_kwargs['original_unit'] = 'IATA pair'
                    else:
                        issues['distance'] = "Distance and IATA codes missing"
                        record_kwargs['status'] = 'FLAGGED'

            record_kwargs['issues'] = issues
            record = NormalizedDataRecord.objects.create(**record_kwargs)
            AuditLog.objects.create(record=record, action="CREATED", changes={"source": source_name})
            records_created += 1

        return Response({"message": f"Successfully processed {records_created} rows."}, status=status.HTTP_200_OK)

class ClearDatabaseView(APIView):
    def post(self, request):
        source_name = request.data.get('source')
        if source_name:
            try:
                source = DataSource.objects.get(name__icontains=source_name)
                DataUpload.objects.filter(source=source).delete()
                return Response({"message": f"Cleared data for {source_name}"}, status=status.HTTP_200_OK)
            except DataSource.DoesNotExist:
                return Response({"error": "Invalid source"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            DataUpload.objects.all().delete()
            return Response({"message": "Cleared all data"}, status=status.HTTP_200_OK)
