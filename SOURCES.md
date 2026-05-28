# Data Sources Research & Realities

## 1. SAP, Fuel and Procurement Data
**Real-World Format Researched**: Flat file (CSV/TXT) exports generated from ALV Grids or custom ABAP reports.
**What I Learned**: SAP systems are heavily customized per organization. While OData and BAPIs are modern, a vast majority of environmental teams receive data as CSV dumps because IT locks down direct API access. Headers are often technical German names (e.g., `BUDAT` = Posting Date, `MENGE` = Quantity, `MEINS` = Base Unit of Measure).
**Sample Data**: My sample data (`sample_sap.csv`) mimics this with `BUDAT`, `MENGE`, and `MEINS`. It includes intentional inconsistencies like using both `L` (Liters) and `GAL` (Gallons) to test our normalization logic.
**What would break in deployment**: Highly customized SAP implementations might use entirely different Z-fields (custom fields) for units, or the export might have inconsistent date formats (DD.MM.YYYY vs YYYY-MM-DD) which would crash simple `strptime` parsing.

## 2. Utility Data, Electricity
**Real-World Format Researched**: Utility Provider Portal CSV Exports.
**What I Learned**: Utilities rarely align perfectly with calendar months. A bill might run from April 15 to May 14. Meters can have varying units (kWh, MWh, CCF for gas). Sometimes there are estimated readings vs actual readings.
**Sample Data**: My sample (`sample_utility.csv`) includes overlapping cross-month dates, different units (`KWH`, `MWH`), and simulates a missing `Bill_End_Date` to test the system's flagging capabilities.
**What would break in deployment**: Tariffs and time-of-use pricing (Peak vs Off-Peak) would break a simple total usage model. Additionally, some providers use PDF bills exclusively, requiring an OCR ingestion pipeline before it ever reaches this CSV format.

## 3. Corporate Travel, Flights (Concur/Navan)
**Real-World Format Researched**: Corporate expense management system CSV exports.
**What I Learned**: Travel platforms often record the financial transaction but not the environmental data. A flight expense might have the date and origin/destination IATA codes (e.g., JFK, LHR), but rarely the actual distance flown.
**Sample Data**: My sample (`sample_travel.csv`) shows a mix. One row has the distance. Another row only has IATA codes, and one row has invalid string data for distance to test error handling.
**What would break in deployment**: Multi-leg flights (e.g., JFK -> LHR -> CDG booked as one expense) would break simple Origin/Dest logic. Also, cabin class (Economy vs First Class) significantly changes emission factors but is often missing or inconsistently labeled in expense data.
