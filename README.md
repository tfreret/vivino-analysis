# Vivino Wine Analysis

## Prelude
We set out to analyze wine quality through the lens of Vivino, the leading consumer platform for wine ratings. Existing public datasets (like the UCI Wine Quality corpus) emphasize physicochemical characteristics and miss the market-driven dimensions we care about—price, origin, grape blends, and aromatic descriptors. To bridge that gap, we scraped data from Vivino's API so we could craft a dataset that directly reflects consumer perception, sensory narratives, and the pricing context of wines.

## Project Recap
1. **Dataset generation and construction** – Selecting Vivino as the source (scrapping) gave us the freedom to collect only the fields we needed: country, winery, price, ratings, grape varieties, and flavor ranks. We prioritized variables that link consumer perceptions to both organoleptic descriptors and commercial attributes.
2. **Analytical focus** – With a consistent dataset in hand, we explore descriptive statistics, sensory correlations, and latent patterns (clusters/PCA) before moving into predictive modeling.

## Getting Started
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Main Steps
1. **Data Exploratory Analysis & Unsupervised Exploration**
    - Understand distributions of ratings, prices, grape varieties, and organoleptic descriptors (acidity, intensity, sweetness, tannin).
    - Visualize relationships among features and run unsupervised methods (PCA, clustering) to surface natural groupings of wines.
2. **Data Preprocessing**
    - Clean the dataset by de-duplicating, handling missing ratings, and harmonizing text fields.
    - Engineer features such as `age`, encode categorical variables (winery, country, flavor ranks, grape blends), and normalize numeric attributes.
    - Build transformers/pipelines and split data into training and test sets.
3. **Baseline Modeling**
    - Train Linear Regression and ensemble models (Random Forest, Gradient Boosting) on preprocessed data.
    - Evaluate with regression metrics (RMSE, MAE, R²) and visualize predictions to compare how well each baseline captures wine quality scores.
4. ...

## Data Schema
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Unique identifier |
| `name` | String | Wine name |
| `vintage` | Integer | Vintage year |
| `country` | String | Country of origin |
| `winery` | String | Winery name |
| `grapes` | String | Semicolon-separated grape varieties |
| `rating` | Float | Vivino average rating |
| `price` | Float | Price in local currency |
| `acidity` | Float | Normalized acidity score |
| `intensity` | Float | Normalized intensity score |
| `sweetness` | Float | Normalized sweetness score |
| `tannin` | Float | Normalized tannin score |
| `flavor_rank1` | String | Primary flavor category |
| `flavor_rank2` | String | Secondary flavor category |
| `flavor_rank3` | String | Tertiary flavor category |