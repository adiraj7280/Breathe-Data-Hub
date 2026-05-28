# Tradeoffs

Here are three things deliberately omitted from this prototype:

### 1. Complex User Authentication & Role-Based Access Control (RBAC)
**Why**: Implementing OAuth, JWT tokens, and distinguishing between "Analyst" vs "Admin" roles takes significant time. For a prototype evaluating data judgment and UI flow, an unauthenticated "assume user is analyst" approach allows us to focus entirely on the core data ingestion and review dashboard.

### 2. External API Integrations (e.g., IATA Airport Distance Calculator)
**Why**: When corporate travel data provides only `Origin_IATA` and `Dest_IATA`, we ideally call an API to calculate flight distance. I omitted this to avoid external dependencies that could break or rate-limit the prototype. Instead, the system flags the row with an issue ("Distance missing. Need to calculate..."), proving the system can catch the data gap and alert the analyst.

### 3. Dockerization and Complex CI/CD
**Why**: The prompt specified wanting a live Vercel link without Dockerization overhead. Building a robust Docker Compose setup for Django+React+Postgres is great for local dev, but adds unnecessary complexity when deploying serverless on Vercel. We traded containerization for serverless simplicity.

### 4. Bulk Actions in the UI (e.g. "Approve All")
**Why**: Analysts often request a button to "Approve All" pending rows. I intentionally omitted this feature because ESG data audits require high fidelity. Forcing analysts to click approve on each row individually (or at least review them closely) prevents rubber-stamping bad data before it hits the immutable audit trail. This is a deliberate UX friction point to ensure data quality.
