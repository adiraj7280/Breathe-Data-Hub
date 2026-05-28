# Decisions & Assumptions

### 1. Vercel for Deployment
You mentioned wanting to use Vercel. We decided to structure the project such that both the Django API and React frontend can be deployed via a single `vercel.json`. Django is served as serverless functions, and React is built statically.

### 2. SQLite for Database
Since this is a prototype to be built in 4 days (and executed in hours), SQLite is used for simplicity and zero-configuration. It easily swaps to PostgreSQL by changing `DATABASES` in `settings.py`.

### 3. CSV as the Ingestion Mechanism
Real-world systems often have APIs, but analysts frequently fall back to CSV exports from portals like SAP or Utility providers due to IT red tape. Handling CSVs accurately represents the most common "messy" data ingestion path.

### 4. Analyst UX & Visual Triage
The React frontend uses a color-coded "Triage" approach. Non-engineers (analysts) do not want to read raw JSON to figure out why an ingestion failed. The dashboard abstracts this by:
- Normalizing values visibly side-by-side with original values.
- Highlighting specific `issues` in Amber warning tags (e.g. "Unknown unit L").
- Using simple "Approve" (Check) and "Reject" (Cross) actions that lock the row's state.

### 5. Normalization Strategy
- **SAP**: We assume German headers (`BUDAT` for date, `MENGE` for amount, `MEINS` for unit). We convert `GAL` to `Liters` for standardization. Unrecognized units flag the row.
- **Utility**: We handle `KWH` and `MWH` (converting MWH to KWH). Missing end dates flag the row.
- **Travel**: If distance is provided, we use it. If only IATA codes are provided, we flag the row indicating distance calculation is needed (since we omitted an external API lookup for IATA distances to keep the prototype fast).

### 5. Scope Categorization
Hardcoded based on the source for prototype purposes:
- SAP (Fuel) -> Scope 1
- Utility (Electricity) -> Scope 2
- Travel (Flights) -> Scope 3

### Questions for the PM
- For travel distances, should we integrate a paid IATA routing API, or rely on users inputting distance?
- How should we handle overlapping utility billing periods?
- Do we need an automated fallback if the SAP unit is completely foreign, or is manual analyst intervention acceptable?
