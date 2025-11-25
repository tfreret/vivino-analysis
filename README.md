# vivino-analysis

Prof

    Data Exploratory Analysis & Unsupervised Exploration
    Data preprocessing, preparation & train-val-test splits
    Baseline results with basic Linear & Ensemble Models

Notes

1. Exploration des données
2. Entraînement de base (KNN aléatoire, modèle linéaire)
3. Fine-tuning (modèles plus complexes : arbres, etc.)

Autres points :
Les learning curves sont utiles à montrer, mais ne sont pas comparables entre algorithmes.
Positive learning rate → comparer des méthodes de classification.
Cross-validation : utiliser au moins 3 folds.

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Unique identifier |
| `name` | String | Wine name |
| `vintage` | Integer | Vintage year |
| `country` | String | Country of origin |
| `winery` | String | Winery name |
| `grapes` | String | Grape varieties (semicolon separated) |
| `rating` | Float | Average user rating |
| `price` | Float | Price in local currency |
| `acidity` | Float | Acidity feature (normalized) |
| `intensity` | Float | Intensity feature (normalized) |
| `sweetness` | Float | Sweetness feature (normalized) |
| `tannin` | Float | Tannin feature (normalized) |
| `flavor_rank1` | String | Primary flavor category |
| `flavor_rank2` | String | Secondary flavor category |
| `flavor_rank3` | String | Tertiary flavor category |

## Data Exploratory Analysis & Unsupervised Exploration

### Dataset generation and construction

To ensure we worked with a dataset truly relevant for analyzing wine quality and characteristics, we chose to generate our own dataset by scraping the Vivino website through its API. This approach allowed us to selectively extract the specific types of information we wanted to keep: sensory characteristics, user ratings, grape varieties, country of origin, price ranges, and aromatic profiles.

We opted for this solution because existing public wine datasets often contain limited, heterogeneous, or low-impact information that is not particularly meaningful or actionable for winemakers. Many of these datasets lack variables genuinely correlated with perceived wine quality or do not allow the connection between sensory attributes and more objective aspects such as price or geographic origin. By constructing our own dataset, we ensured consistency, granularity, and analytical relevance of the data.

### Subsections for Data Analysis

Before diving into the details of our exploratory work, it is important to note that our dataset contains several distinct categories of information—objective features (price, vintage, country), sensory descriptors (acidity, sweetness, tannins), user-generated ratings, and aromatic classifications. Because these dimensions do not all correlate with each other in the same way, we conducted multiple types of complementary data analyses. Each analysis focuses on a different aspect of the dataset, allowing us to better understand the structure of the data, uncover meaningful patterns, and identify the relationships (or lack thereof) between wine characteristics and perceived quality.

**1. General Descriptive Analysis**

* Distribution of wines by country and wine-producing regions.

* Distribution of vintages, prices, and user ratings.

* Analysis of grape variety diversity and frequency.

**2. Quality and Rating Analysis**

* Relationship between price and rating (correlations, main trends).

* Influence of country, grape variety, or winery on average ratings.

* Rating variability across vintages.

**3. Organoleptic Feature Analysis**

* Distribution of acidity, intensity, sweetness, and tannin levels.

* Visualization of correlations between these sensory variables.

* Identification of typical wine profiles through clustering (K-Means, PCA, etc.).

**4. Aroma Profile Analysis (Flavor Ranks)**

* Frequencies of primary, secondary, and tertiary aroma categories.

* Clustering wines based on their aromatic profiles.

* Identifying sensory patterns linked to rating or price.

**5. Unsupervised Exploration Methods**

* PCA for dimensionality reduction and interpretation of principal axes.

* Clustering (K-Means, DBSCAN, Agglomerative) to detect natural wine groups.

* Cluster interpretation: profile summaries, key distinctions, and insights.

**6. Data Cleaning, Preparation, and Enrichment**

* Handling missing values and feature normalization.

* Encoding categorical variables (grape varieties, countries, flavor categories).

* Considerations for choosing train/validation/test splits.