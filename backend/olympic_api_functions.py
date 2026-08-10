import pandas as pd
import numpy as np
from collections import Counter
import json
import os

# Load the dataset (use backend/athlete_events.csv)
data_path = os.path.join(os.path.dirname(__file__), 'athlete_events.csv')
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    try:
        df = pd.read_csv('athlete_events.csv')
    except Exception:
        df = pd.DataFrame()

# ==========================================
# 1. MEDAL TALLY & COUNTRY PERFORMANCE
# ==========================================

def get_top_countries_alltime(top_n=10):
    """Top performing countries of all time"""
    medals_df = df[df['Medal'].notna()].copy()
    
    country_medals = medals_df.groupby(['NOC', 'Medal']).size().unstack(fill_value=0)
    country_medals['Total'] = country_medals.sum(axis=1)
    country_medals = country_medals.sort_values('Total', ascending=False).head(top_n)
    
    result = []
    for noc in country_medals.index:
        result.append({
            'country': noc,
            'gold': int(country_medals.loc[noc, 'Gold']) if 'Gold' in country_medals.columns else 0,
            'silver': int(country_medals.loc[noc, 'Silver']) if 'Silver' in country_medals.columns else 0,
            'bronze': int(country_medals.loc[noc, 'Bronze']) if 'Bronze' in country_medals.columns else 0,
            'total': int(country_medals.loc[noc, 'Total'])
        })
    
    return {'top_countries': result}


def get_country_medals_by_year(noc, year=None):
    """Country-wise medal count for specific year or all years"""
    medals_df = df[df['Medal'].notna()].copy()
    
    if year:
        medals_df = medals_df[medals_df['Year'] == year]
    
    country_data = medals_df[medals_df['NOC'] == noc]
    
    if country_data.empty:
        return {'error': f'No data found for {noc}'}
    
    medals_by_year = country_data.groupby(['Year', 'Medal']).size().unstack(fill_value=0)
    
    result = []
    for yr in medals_by_year.index:
        result.append({
            'year': int(yr),
            'gold': int(medals_by_year.loc[yr, 'Gold']) if 'Gold' in medals_by_year.columns else 0,
            'silver': int(medals_by_year.loc[yr, 'Silver']) if 'Silver' in medals_by_year.columns else 0,
            'bronze': int(medals_by_year.loc[yr, 'Bronze']) if 'Bronze' in medals_by_year.columns else 0,
        })
    
    return {'country': noc, 'medals_by_year': result}


def get_country_ranking(year, season='Summer'):
    """Country ranking for a specific Olympics"""
    medals_df = df[(df['Medal'].notna()) & (df['Year'] == year) & (df['Season'] == season)].copy()
    
    country_medals = medals_df.groupby(['NOC', 'Medal']).size().unstack(fill_value=0)
    country_medals['Total'] = country_medals.sum(axis=1)
    country_medals['Gold'] = country_medals.get('Gold', 0)
    country_medals = country_medals.sort_values(['Gold', 'Total'], ascending=False)
    
    result = []
    for rank, noc in enumerate(country_medals.index, 1):
        result.append({
            'rank': rank,
            'country': noc,
            'gold': int(country_medals.loc[noc, 'Gold']),
            'silver': int(country_medals.loc[noc, 'Silver']) if 'Silver' in country_medals.columns else 0,
            'bronze': int(country_medals.loc[noc, 'Bronze']) if 'Bronze' in country_medals.columns else 0,
            'total': int(country_medals.loc[noc, 'Total'])
        })
    
    return {'year': year, 'season': season, 'rankings': result}


# ==========================================
# 2. ATHLETE ANALYTICS
# ==========================================

def get_most_decorated_athletes(top_n=10):
    """Athletes with most medals"""
    medals_df = df[df['Medal'].notna()].copy()
    
    athlete_medals = medals_df.groupby(['ID', 'Name', 'Sex', 'Team']).agg({
        'Medal': 'count',
    }).reset_index()
    
    athlete_medals.columns = ['ID', 'Name', 'Sex', 'Team', 'Total_Medals']
    athlete_medals = athlete_medals.sort_values('Total_Medals', ascending=False).head(top_n)
    
    # Get medal breakdown
    result = []
    for _, row in athlete_medals.iterrows():
        athlete_id = row['ID']
        medals = medals_df[medals_df['ID'] == athlete_id]['Medal'].value_counts().to_dict()
        
        result.append({
            'id': int(row['ID']),
            'name': row['Name'],
            'sex': row['Sex'],
            'team': row['Team'],
            'total_medals': int(row['Total_Medals']),
            'gold': medals.get('Gold', 0),
            'silver': medals.get('Silver', 0),
            'bronze': medals.get('Bronze', 0)
        })
    
    return {'most_decorated_athletes': result}


def get_physical_stats_by_sport(sport=None):
    """Average physical stats by sport"""
    stats_df = df[df[['Age', 'Height', 'Weight']].notna().all(axis=1)].copy()
    
    if sport:
        stats_df = stats_df[stats_df['Sport'] == sport]
    
    grouped = stats_df.groupby('Sport').agg({
        'Age': ['mean', 'min', 'max'],
        'Height': ['mean', 'min', 'max'],
        'Weight': ['mean', 'min', 'max'],
        'ID': 'count'
    }).reset_index()
    
    result = []
    for _, row in grouped.iterrows():
        result.append({
            'sport': row['Sport'],
            'avg_age': round(row['Age']['mean'], 2),
            'min_age': int(row['Age']['min']),
            'max_age': int(row['Age']['max']),
            'avg_height': round(row['Height']['mean'], 2),
            'min_height': int(row['Height']['min']),
            'max_height': int(row['Height']['max']),
            'avg_weight': round(row['Weight']['mean'], 2),
            'min_weight': int(row['Weight']['min']),
            'max_weight': int(row['Weight']['max']),
            'total_athletes': int(row['ID']['count'])
        })
    
    return {'physical_stats_by_sport': result}


def get_youngest_oldest_medalists():
    """Youngest and oldest medal winners"""
    medals_df = df[(df['Medal'].notna()) & (df['Age'].notna())].copy()
    
    youngest = medals_df.nsmallest(10, 'Age')[['Name', 'Age', 'Sport', 'Event', 'Year', 'Medal']]
    oldest = medals_df.nlargest(10, 'Age')[['Name', 'Age', 'Sport', 'Event', 'Year', 'Medal']]
    
    result = {
        'youngest_medalists': youngest.to_dict('records'),
        'oldest_medalists': oldest.to_dict('records')
    }
    
    return result


# ==========================================
# 3. SPORT & EVENT ANALYSIS
# ==========================================

def get_dominant_countries_per_sport(sport):
    """Which country dominates which sport"""
    medals_df = df[(df['Medal'].notna()) & (df['Sport'] == sport)].copy()
    
    country_medals = medals_df.groupby('NOC').size().sort_values(ascending=False).head(10)
    
    result = []
    for noc, count in country_medals.items():
        result.append({
            'country': noc,
            'total_medals': int(count)
        })
    
    return {'sport': sport, 'dominant_countries': result}


def get_sport_evolution():
    """Sports added/removed over time"""
    sports_by_year = df.groupby('Year')['Sport'].apply(lambda x: set(x)).to_dict()
    
    years = sorted(sports_by_year.keys())
    result = []
    
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        
        added = list(sports_by_year[curr_year] - sports_by_year[prev_year])
        removed = list(sports_by_year[prev_year] - sports_by_year[curr_year])
        
        if added or removed:
            result.append({
                'year': int(curr_year),
                'added_sports': added,
                'removed_sports': removed
            })
    
    return {'sport_evolution': result}


def get_participation_count_by_sport():
    """Number of athletes per sport"""
    participation = df.groupby('Sport')['ID'].nunique().sort_values(ascending=False)
    
    result = []
    for sport, count in participation.items():
        result.append({
            'sport': sport,
            'unique_athletes': int(count)
        })
    
    return {'participation_by_sport': result}


# ==========================================
# 4. GENDER & DIVERSITY TRENDS
# ==========================================

def get_gender_participation_trend():
    """Male vs Female participation over time"""
    gender_trend = df.groupby(['Year', 'Sex']).size().unstack(fill_value=0)
    
    result = []
    for year in gender_trend.index:
        male = int(gender_trend.loc[year, 'M']) if 'M' in gender_trend.columns else 0
        female = int(gender_trend.loc[year, 'F']) if 'F' in gender_trend.columns else 0
        total = male + female
        
        result.append({
            'year': int(year),
            'male': male,
            'female': female,
            'total': total,
            'female_percentage': round((female / total * 100), 2) if total > 0 else 0
        })
    
    return {'gender_trend': result}


def get_country_participation_growth():
    """Number of countries participating over time"""
    countries_by_year = df.groupby('Year')['NOC'].nunique()
    
    result = []
    for year, count in countries_by_year.items():
        result.append({
            'year': int(year),
            'participating_countries': int(count)
        })
    
    return {'country_participation_growth': result}


# ==========================================
# 5. HOST CITY & SEASON DATA
# ==========================================

def get_host_cities_list():
    """List of all host cities"""
    host_data = df.groupby(['Year', 'Season', 'City']).size().reset_index()
    host_data = host_data.drop(columns=0)
    
    result = []
    for _, row in host_data.iterrows():
        result.append({
            'year': int(row['Year']),
            'season': row['Season'],
            'city': row['City']
        })
    
    return {'host_cities': result}


def get_summer_vs_winter_comparison():
    """Summer vs Winter Olympics comparison"""
    season_stats = df.groupby('Season').agg({
        'ID': 'nunique',
        'NOC': 'nunique',
        'Sport': 'nunique',
        'Event': 'nunique'
    }).reset_index()
    
    result = []
    for _, row in season_stats.iterrows():
        result.append({
            'season': row['Season'],
            'unique_athletes': int(row['ID']),
            'countries': int(row['NOC']),
            'sports': int(row['Sport']),
            'events': int(row['Event'])
        })
    
    return {'season_comparison': result}


# ==========================================
# 6. ADVANCED INSIGHTS - ATHLETE EVOLUTION
# ==========================================

def get_physical_changes_over_time(sport):
    """How athlete body types changed over time"""
    stats_df = df[(df['Sport'] == sport) & df[['Age', 'Height', 'Weight']].notna().all(axis=1)].copy()
    
    # Group by decades
    stats_df['Decade'] = (stats_df['Year'] // 10) * 10
    
    decade_stats = stats_df.groupby('Decade').agg({
        'Age': 'mean',
        'Height': 'mean',
        'Weight': 'mean',
        'ID': 'count'
    }).reset_index()
    
    result = []
    for _, row in decade_stats.iterrows():
        result.append({
            'decade': int(row['Decade']),
            'avg_age': round(row['Age'], 2),
            'avg_height': round(row['Height'], 2),
            'avg_weight': round(row['Weight'], 2),
            'sample_size': int(row['ID'])
        })
    
    return {'sport': sport, 'evolution': result}


def get_bmi_analysis_by_sport():
    """BMI analysis for each sport"""
    stats_df = df[df[['Height', 'Weight']].notna().all(axis=1)].copy()
    stats_df['BMI'] = stats_df['Weight'] / ((stats_df['Height'] / 100) ** 2)
    
    bmi_stats = stats_df.groupby('Sport')['BMI'].agg(['mean', 'min', 'max']).reset_index()
    
    result = []
    for _, row in bmi_stats.iterrows():
        result.append({
            'sport': row['Sport'],
            'avg_bmi': round(row['mean'], 2),
            'min_bmi': round(row['min'], 2),
            'max_bmi': round(row['max'], 2)
        })
    
    # Sort by BMI
    result = sorted(result, key=lambda x: x['avg_bmi'], reverse=True)
    
    return {'bmi_by_sport': result}


# ==========================================
# 7. EFFICIENCY & STRIKE RATE
# ==========================================

def get_medal_conversion_rate(year, season='Summer'):
    """Medal conversion rate: Medals per participant"""
    year_df = df[(df['Year'] == year) & (df['Season'] == season)].copy()
    
    total_participants = year_df.groupby('NOC')['ID'].nunique()
    medals_won = year_df[year_df['Medal'].notna()].groupby('NOC').size()
    
    conversion = pd.DataFrame({
        'participants': total_participants,
        'medals': medals_won
    }).fillna(0)
    
    conversion['conversion_rate'] = (conversion['medals'] / conversion['participants'] * 100)
    conversion = conversion.sort_values('conversion_rate', ascending=False).head(20)
    
    result = []
    for noc in conversion.index:
        result.append({
            'country': noc,
            'participants': int(conversion.loc[noc, 'participants']),
            'medals': int(conversion.loc[noc, 'medals']),
            'conversion_rate': round(conversion.loc[noc, 'conversion_rate'], 2)
        })
    
    return {'year': year, 'season': season, 'conversion_rates': result}


def get_underdog_nations():
    """Small countries with high medal efficiency"""
    total_participants = df.groupby('NOC')['ID'].nunique()
    medals_won = df[df['Medal'].notna()].groupby('NOC').size()
    
    efficiency = pd.DataFrame({
        'participants': total_participants,
        'medals': medals_won
    }).fillna(0)
    
    # Filter countries with less than 500 participants
    efficiency = efficiency[efficiency['participants'] < 500]
    efficiency['efficiency'] = efficiency['medals'] / efficiency['participants']
    efficiency = efficiency.sort_values('efficiency', ascending=False).head(20)
    
    result = []
    for noc in efficiency.index:
        result.append({
            'country': noc,
            'total_participants': int(efficiency.loc[noc, 'participants']),
            'total_medals': int(efficiency.loc[noc, 'medals']),
            'efficiency_score': round(efficiency.loc[noc, 'efficiency'], 3)
        })
    
    return {'underdog_nations': result}


# ==========================================
# 8. LONGEVITY & LEGENDS
# ==========================================

def get_most_experienced_athletes():
    """Athletes who participated in most Olympics"""
    olympic_count = df.groupby(['ID', 'Name', 'Team', 'Sex'])['Games'].nunique().reset_index()
    olympic_count = olympic_count.sort_values('Games', ascending=False).head(20)
    
    result = []
    for _, row in olympic_count.iterrows():
        athlete_data = df[df['ID'] == row['ID']]
        years = sorted(athlete_data['Year'].unique())
        
        result.append({
            'id': int(row['ID']),
            'name': row['Name'],
            'team': row['Team'],
            'sex': row['Sex'],
            'olympics_count': int(row['Games']),
            'years_participated': [int(y) for y in years],
            'career_span': int(years[-1] - years[0]) if len(years) > 1 else 0
        })
    
    return {'most_experienced_athletes': result}


def get_age_defying_athletes():
    """Athletes who won medals at advanced age"""
    medals_df = df[(df['Medal'].notna()) & (df['Age'].notna())].copy()
    
    # Athletes over 40 with medals
    old_medalists = medals_df[medals_df['Age'] >= 40].sort_values('Age', ascending=False)
    
    result = []
    for _, row in old_medalists.head(30).iterrows():
        result.append({
            'name': row['Name'],
            'age': int(row['Age']),
            'sport': row['Sport'],
            'event': row['Event'],
            'medal': row['Medal'],
            'year': int(row['Year']),
            'team': row['Team']
        })
    
    return {'age_defying_athletes': result}


# ==========================================
# 9. SPORT-SPECIFIC DOMINATION
# ==========================================

def get_sport_monopoly():
    """Sports dominated by single country"""
    medals_df = df[df['Medal'].notna()].copy()
    
    result = []
    for sport in medals_df['Sport'].unique():
        sport_medals = medals_df[medals_df['Sport'] == sport]
        country_medals = sport_medals['NOC'].value_counts()
        
        if len(country_medals) > 0:
            top_country = country_medals.index[0]
            top_medals = country_medals.iloc[0]
            total_medals = country_medals.sum()
            dominance_percentage = (top_medals / total_medals) * 100
            
            if dominance_percentage > 30:  # At least 30% dominance
                result.append({
                    'sport': sport,
                    'dominant_country': top_country,
                    'medals': int(top_medals),
                    'total_sport_medals': int(total_medals),
                    'dominance_percentage': round(dominance_percentage, 2)
                })
    
    # Sort by dominance
    result = sorted(result, key=lambda x: x['dominance_percentage'], reverse=True)
    
    return {'sport_monopolies': result}


def get_extinct_sports():
    """Sports that are no longer in Olympics"""
    recent_year = df['Year'].max()
    recent_sports = set(df[df['Year'] == recent_year]['Sport'].unique())
    all_sports = set(df['Sport'].unique())
    
    extinct = all_sports - recent_sports
    
    result = []
    for sport in extinct:
        sport_data = df[df['Sport'] == sport]
        last_year = sport_data['Year'].max()
        first_year = sport_data['Year'].min()
        
        result.append({
            'sport': sport,
            'first_year': int(first_year),
            'last_year': int(last_year),
            'years_active': int(last_year - first_year)
        })
    
    return {'extinct_sports': result}


# ==========================================
# 10. GEOPOLITICAL INSIGHTS
# ==========================================

def get_home_advantage_analysis():
    """Do host countries win more medals?"""
    host_info = df.groupby(['Year', 'Season', 'City']).first()['NOC'].reset_index()
    host_info.columns = ['Year', 'Season', 'City', 'Host_NOC']
    
    result = []
    for _, row in host_info.iterrows():
        year = row['Year']
        season = row['Season']
        host_noc = row['Host_NOC']
        
        # Medals won by host
        host_medals = df[(df['Year'] == year) & (df['Season'] == season) & 
                        (df['NOC'] == host_noc) & (df['Medal'].notna())].shape[0]
        
        # Total medals
        total_medals = df[(df['Year'] == year) & (df['Season'] == season) & 
                         (df['Medal'].notna())].shape[0]
        
        result.append({
            'year': int(year),
            'season': season,
            'city': row['City'],
            'host_country': host_noc,
            'medals_won': int(host_medals),
            'total_medals': int(total_medals),
            'percentage': round((host_medals / total_medals * 100), 2) if total_medals > 0 else 0
        })
    
    return {'home_advantage': result}


def get_boycott_impact():
    """Medal distribution during boycott years (1980, 1984)"""
    boycott_years = [1980, 1984]
    
    result = []
    for year in boycott_years:
        year_data = df[(df['Year'] == year) & (df['Medal'].notna())]
        
        top_countries = year_data['NOC'].value_counts().head(10)
        
        countries = []
        for noc, count in top_countries.items():
            countries.append({
                'country': noc,
                'medals': int(count)
            })
        
        result.append({
            'year': year,
            'participating_countries': int(df[df['Year'] == year]['NOC'].nunique()),
            'top_performers': countries
        })
    
    return {'boycott_years': result}


# ==========================================
# UTILITY FUNCTION TO GET ALL INSIGHTS
# ==========================================

def generate_all_insights():
    """Generate all insights at once (for bulk processing)"""
    insights = {
        'medal_tally': {
            'top_countries': get_top_countries_alltime(20),
            'gender_trends': get_gender_participation_trend(),
            'country_growth': get_country_participation_growth()
        },
        'athletes': {
            'most_decorated': get_most_decorated_athletes(20),
            'youngest_oldest': get_youngest_oldest_medalists(),
            'most_experienced': get_most_experienced_athletes(),
            'age_defying': get_age_defying_athletes()
        },
        'sports': {
            'sport_evolution': get_sport_evolution(),
            'extinct_sports': get_extinct_sports(),
            'sport_monopoly': get_sport_monopoly(),
            'participation': get_participation_count_by_sport()
        },
        'physical_analytics': {
            'bmi_analysis': get_bmi_analysis_by_sport(),
            'physical_stats': get_physical_stats_by_sport()
        },
        'efficiency': {
            'underdog_nations': get_underdog_nations()
        },
        'geopolitics': {
            'home_advantage': get_home_advantage_analysis(),
            'boycott_impact': get_boycott_impact()
        },
        'host_data': {
            'host_cities': get_host_cities_list(),
            'season_comparison': get_summer_vs_winter_comparison()
        }
    }
    
    return insights


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    # Example calls (uncomment to test)
    
    # print(json.dumps(get_top_countries_alltime(10), indent=2))
    # print(json.dumps(get_most_decorated_athletes(10), indent=2))
    # print(json.dumps(get_physical_stats_by_sport(), indent=2))
    # print(json.dumps(get_medal_conversion_rate(2016), indent=2))
    # print(json.dumps(get_home_advantage_analysis(), indent=2))
    
    # Generate all insights
    # all_data = generate_all_insights()
    # with open('olympic_insights.json', 'w') as f:
    #     json.dumps(all_data, f, indent=2)
    
    pass
