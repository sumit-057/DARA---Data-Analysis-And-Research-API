import pandas as pd
import os

# Load dataset (resolve relative path to project data folder)
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'global_energy_consumption.csv'))
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    try:
        df = pd.read_csv('global_energy_consumption.csv')
    except Exception:
        df = pd.DataFrame()

# CLEANING FUNCTION
def clean_energy_data():
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].mean())

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unspecified").str.strip()

clean_energy_data()

def global_energy_summaryAPI():
    result = {
        "summary": {
            "total_countries": df['Country'].nunique(),
            "highest_energy_country": df.loc[df['Total Energy Consumption (TWh)'].idxmax(), "Country"],
            "lowest_energy_country": df.loc[df['Total Energy Consumption (TWh)'].idxmin(), "Country"],
            "global_avg_energy_consumption_TWh": round(df['Total Energy Consumption (TWh)'].mean(), 3),
            "global_avg_price_usd_per_kwh": round(df['Energy Price Index (USD/kWh)'].mean(), 4),
            "global_avg_co2_million_tons": round(df['Carbon Emissions (Million Tons)'].mean(), 3),
            "global_avg_renewables_percent": round(df['Renewable Energy Share (%)'].mean(), 2)
        }
    }
    return result

def renewable_leadersAPI(limit=7):
    data = (
        df[['Country', 'Year', 'Renewable Energy Share (%)']]
        .sort_values(by='Renewable Energy Share (%)', ascending=False)
        .head(limit)
    )
    return {
        "data": data.to_dict(orient='records')
    }

def cleanest_countriesAPI(limit=8):
    sorted_df = df.sort_values(by='Carbon Emissions (Million Tons)', ascending=True)

    return {
        "units": {"emissions": "Million Tons CO2"},
        "data": sorted_df[['Country', 'Year', 'Carbon Emissions (Million Tons)']]
                .head(limit)
                .to_dict(orient='records'),
        "note": "Lower CO2 emissions usually indicate cleaner and more sustainable energy usage."
    }

def energy_price_comparisonAPI(c1, c2):
    d1 = df[df['Country'].str.lower() == c1.lower()]
    d2 = df[df['Country'].str.lower() == c2.lower()]

    if d1.empty or d2.empty:
        return {"message": "Comparison failed", "error": "One or both countries not found"}

    p1 = round(d1['Energy Price Index (USD/kWh)'].mean(), 4)
    p2 = round(d2['Energy Price Index (USD/kWh)'].mean(), 4)

    return {
        "summary": {
            "higher_price_country": c1 if p1 > p2 else c2,
            "difference_usd_per_kwh": round(abs(p1 - p2), 4)
        },
        "data": [
            {"country": c1, "energy_price_usd_per_kwh": p1},
            {"country": c2, "energy_price_usd_per_kwh": p2}
        ]
    }

def energy_mixAPI(country):
    data = df[df['Country'].str.lower() == country.lower()]

    if data.empty:
        return {
            "message": "Country not found",
            "error": f"No data available for '{country}'."
        }

    row = data.iloc[0]

    # Source-based (should be close to 100%)
    renewable = row['Renewable Energy Share (%)']
    fossil = row['Fossil Fuel Dependency (%)']

    # Usage-based (independent values, not required to add up to 100)
    industrial = row['Industrial Energy Use (%)']
    household = row['Household Energy Use (%)']

    return {
        "message": f"Energy source and usage breakdown for {country}",
        
        "energy_source_breakdown": {
            "renewable_energy_share_percent": renewable,
            "fossil_fuel_dependency_percent": fossil,
            "note": "Source percentages compare renewable vs fossil fuel energy."
        },

        "energy_usage_breakdown": {
            "industrial_energy_use_percent": industrial,
            "household_energy_use_percent": household,
            "note": "Usage percentages represent consumption by sectors and do NOT add up to 100%."
        }
    }

def factor_summaryAPI():
    factors = [
        'Total Energy Consumption (TWh)',
        'Per Capita Energy Use (kWh)',
        'Renewable Energy Share (%)',
        'Fossil Fuel Dependency (%)',
        'Industrial Energy Use (%)',
        'Household Energy Use (%)',
        'Carbon Emissions (Million Tons)',
        'Energy Price Index (USD/kWh)'
    ]

    result = []
    for col in factors:
        result.append({
            "factor": col,
            "average": round(df[col].mean(), 3),
            "maximum": round(df[col].max(), 3),
            "max_country": df.loc[df[col].idxmax(), "Country"],
            "minimum": round(df[col].min(), 3),
            "min_country": df.loc[df[col].idxmin(), "Country"]
        })
    return result
    