# Data Model

Our data model handles multi-tenancy, source-of-truth tracking, normalization, and an audit trail.

## Core Models

### 1. `Client` (Multi-Tenancy)
Represents the organization whose data is being processed. All data flows up to a Client.
- `name`: Organization name.
- `created_at`: Tenant creation timestamp.

### 2. `DataSource`
Defines the structure/origin of the ingest (e.g., SAP, Utility Portal, Corporate Travel).
- `name`: Identifier for the source.
- `format_type`: Expected format (e.g., CSV).

### 3. `DataUpload` (Source-of-truth tracking)
Groups rows together based on the specific upload event. If a file contained bad data, we can trace it back to the exact upload event and file.
- `client`: FK to Client.
- `source`: FK to DataSource.
- `file_name`: Original name of the uploaded file.
- `uploaded_at`: Timestamp.

### 4. `NormalizedDataRecord` (The Core Ledger)
This is where both the raw data and normalized data live. 
- `upload`: FK to DataUpload, linking the record to its origin.
- `scope_category`: Scope 1, 2, or 3 classification.
- `activity_type`: Specific type (Fuel, Electricity, Flight). Indexed for fast filtering.
- `activity_date_start` / `activity_date_end`: Normalizes timeframes (e.g., for utility bills spanning months).
- `original_value` / `original_unit`: What the source gave us (e.g., `GAL`, `MWH`).
- `normalized_value` / `normalized_unit`: What our system uses (e.g., `Liters`, `kWh`, `miles`).
- `status`: Enum (`PENDING`, `APPROVED`, `REJECTED`, `FLAGGED`). Controls the review flow. Indexed for fast dashboard rendering.
- `issues`: JSON field storing normalization errors (e.g., "Unknown unit KG").
- `raw_data`: JSON field storing the exact row from the CSV. This ensures we never lose the raw context if our normalization logic had a bug.
- **Indexes**: Includes a compound index on `['status', 'created_at']` to optimize the analyst queue query (which typically asks for "Pending/Flagged rows ordered by oldest first").

### 5. `AuditLog`
An append-only log of actions taken on a `NormalizedDataRecord`. This is a strict regulatory requirement for ESG data before audit handoff.
- `record`: FK to NormalizedDataRecord.
- `action`: String describing the event (e.g., `CREATED`, `STATUS_CHANGED_TO_APPROVED`). Indexed.
- `changes`: JSON payload describing what changed (e.g., previous value vs new value).
- `user`: Who made the change.
- `timestamp`: When it happened. Indexed.
