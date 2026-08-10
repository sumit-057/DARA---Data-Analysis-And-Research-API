import pandas as pd
import os

# Load dataset (resolve relative path to project data folder)
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'happiness.csv'))
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    try:
        df = pd.read_csv('happiness.csv')
    except Exception:
        df = pd.DataFrame()

# --- Data Cleaning ---
def clean_data():
    # Standardize column names
    df.columns = df.columns.str.strip()

    # Fill missing numeric values with column means
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].mean())

    # Fill missing strings
    df['Region'] = df['Region'].fillna('Unspecified')
    df['Country'] = df['Country'].fillna('Unknown')

clean_data()

def top_countriesAPI(limit=8):
    result = (
        df[['Country', 'Region', 'Happiness Rank', 'Happiness Score']]
        .sort_values(by='Happiness Score', ascending=False)
        .head(limit)
        .reset_index(drop=True)
    )
    return {
        "data": result.to_dict(orient='records')
    }

def factor_impactAPI():
    numeric_df = df.select_dtypes(include='number')
        # Columns to exclude from result
    remove_cols = ['Happiness Rank', 'Standard Error', 'Dystopia Residual']
    numeric_df = numeric_df.drop(columns=[c for c in remove_cols if c in numeric_df.columns])

    corr = numeric_df.corr()['Happiness Score'].sort_values(ascending=False)
    result = [
        {"factor": k, "correlation_with_happiness": round(v, 3)}
        for k, v in corr.items() if k != 'Happiness Score'
    ]
    return result
    

def country_infoAPI(name):
    country = df[df['Country'].str.lower() == name.lower()]
    if country.empty:
        return {"message": "Country data unavailable", "error": f"'{name}' not found in dataset."}
    return {
        "result": country.iloc[0].to_dict()
    }

def compare_countriesAPI(country1, country2):
    c1 = df[df['Country'].str.lower() == country1.lower()]
    c2 = df[df['Country'].str.lower() == country2.lower()]

    if c1.empty or c2.empty:
        return {"message": "Comparison failed", "error": "One or both countries not found in dataset."}

    score1 = float(c1['Happiness Score'].values[0])
    score2 = float(c2['Happiness Score'].values[0])
    diff = round(abs(score1 - score2), 3)
    winner = country1 if score1 > score2 else country2

    return {
        "summary": {
            "more_happy_country": winner,
            "score_difference": diff
        },
        "data": [
            {"country": country1, "happiness_score": score1},
            {"country": country2, "happiness_score": score2}
        ]
    }

def happiness_gapAPI(region):
    region_data = df[df['Region'].str.lower() == region.lower()]
    if region_data.empty:
        return {"message": "Invalid region", "error": f"Region '{region}' not found."}

    happiest = region_data.loc[region_data['Happiness Score'].idxmax()]
    saddest = region_data.loc[region_data['Happiness Score'].idxmin()]
    gap = round(happiest['Happiness Score'] - saddest['Happiness Score'], 3)

    return {
        "summary": {
            "happiest_country": happiest['Country'],
            "saddest_country": saddest['Country'],
            "gap": gap
        }
    }

def country_rank_trendAPI(country):
    data = df[df['Country'].str.lower() == country.lower()]
    if data.empty:
        return {"message": "Country not found", "error": f"'{country}' missing in dataset."}

    rank = int(data['Happiness Rank'].values[0])
    total = df['Happiness Rank'].count()
    percentile = round((1 - (rank / total)) * 100, 2)
    status = "Top 10%" if percentile >= 90 else "Above Average" if percentile >= 50 else "Below Average"

    return {
        "result": {
            "rank": rank,
            "percentile_position": percentile,
            "status": status
        }
    }

def factor_averagesAPI():
    factor_cols = [
        'Economy (GDP per Capita)', 
        'Family', 
        'Health (Life Expectancy)',
        'Freedom', 
        'Trust (Government Corruption)', 
        'Generosity'
    ]

    result = []

    for col in factor_cols:
        avg_val = round(df[col].mean(), 3)
        max_val = round(df[col].max(), 3)
        min_val = round(df[col].min(), 3)

        # Get the country with max/min for this factor
        max_country = df.loc[df[col].idxmax(), 'Country']
        min_country = df.loc[df[col].idxmin(), 'Country']

        result.append({
            "factor": col,
            "global_average": avg_val,
            "max_value": max_val,
            "max_value_country": max_country,
            "min_value": min_val,
            "min_value_country": min_country
        })
    return result
    