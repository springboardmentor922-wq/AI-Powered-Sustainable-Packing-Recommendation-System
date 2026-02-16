## EcoPackAI (Flask App)

This app provides:
- **REST APIs** (secured via API key + consistent JSON responses)
- **Web UI** (HTML/CSS/Bootstrap) with a product input form + ranked recommendations table

### 1) Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

If your dataset CSV is not located at `ML/dataset_with_material_references.csv`, set:
- `ECOPACKAI_DATASET_PATH` = full path to the CSV

### 2) Run

```bash
python api_app.py
```

Open UI:
- `http://localhost:5000/`

### 3) Environment variables

- `ECOPACKAI_API_KEY` (default: `change-me`)
- `DATABASE_URL` (default: `sqlite:///ecopackai.db`)
  - For PostgreSQL, set: `postgresql://user:password@localhost:5432/ecopackai`

### 4) REST API endpoints (JSON)

All API endpoints require header:
- `X-API-KEY: <your key>`

#### Create product
- `POST /api/products`

```json
{
  "name": "Milk 1L",
  "category": "DAIRY",
  "packaging_format": "BOTTLE",
  "weight_kg": 1.0,
  "budget_per_kg": 400,
  "max_co2_kg": 2.5,
  "shelf_life_days": 180
}
```

#### Get recommendations
- `POST /api/recommendations`

Option A (stored product):
```json
{ "product_id": 1, "top_n": 5 }
```

Option B (ad-hoc):
```json
{
  "category": "DAIRY",
  "weight_kg": 1.0,
  "budget_per_kg": 400,
  "max_co2_kg": 2.5,
  "shelf_life_days": 180,
  "top_n": 5
}
```

#### Environmental score
- `POST /api/environmental-score`

```json
{ "material_name": "Recycled PET Bottle" }
```

### 5) UI flow

- Go to `/`
- Fill product parameters
- Submit to see:
  - Top pick summary cards
  - Ranking table with comparison metrics (AI score, predicted cost, predicted CO₂, sustainability %, environmental score)

