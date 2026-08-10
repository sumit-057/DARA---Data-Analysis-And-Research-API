import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json
import re
import os

# Load dataset (use backend/athlete_events.csv)
data_path = os.path.join(os.path.dirname(__file__), 'athlete_events.csv')
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    try:
        df = pd.read_csv('athlete_events.csv')
    except Exception:
        df = pd.DataFrame()

# ==========================================
# 11. NAME ANALYSIS
# ==========================================

def get_most_common_names(top_n=20):
    """Most common athlete names"""
    # Extract first names
    first_names = df['Name'].str.split().str[0].value_counts().head(top_n)
    
    result = []
    for name, count in first_names.items():
        result.append({
            'name': name,
            'count': int(count)
        })
    
    return {'most_common_names': result}


def get_name_trends_by_decade():
    """Name popularity by decade"""
    df_copy = df.copy()
    df_copy['Decade'] = (df_copy['Year'] // 10) * 10
    df_copy['FirstName'] = df_copy['Name'].str.split().str[0]
    
    result = []
    for decade in sorted(df_copy['Decade'].unique()):
        decade_data = df_copy[df_copy['Decade'] == decade]
        top_names = decade_data['FirstName'].value_counts().head(5)
        
        names_list = []
        for name, count in top_names.items():
            names_list.append({
                'name': name,
                'count': int(count)
            })
        
        result.append({
            'decade': int(decade),
            'top_names': names_list
        })
    
    return {'name_trends_by_decade': result}


def get_lucky_names():
    """Names with highest medal conversion rate"""
    df_copy = df.copy()
    df_copy['FirstName'] = df_copy['Name'].str.split().str[0]
    
    name_stats = df_copy.groupby('FirstName').agg({
        'ID': 'nunique',
        'Medal': lambda x: x.notna().sum()
    }).reset_index()
    
    name_stats.columns = ['Name', 'Athletes', 'Medals']
    name_stats['Success_Rate'] = (name_stats['Medals'] / name_stats['Athletes']) * 100
    
    # Filter names with at least 50 athletes
    name_stats = name_stats[name_stats['Athletes'] >= 50]
    name_stats = name_stats.sort_values('Success_Rate', ascending=False).head(20)
    
    result = []
    for _, row in name_stats.iterrows():
        result.append({
            'name': row['Name'],
            'athletes': int(row['Athletes']),
            'medals': int(row['Medals']),
            'success_rate': round(row['Success_Rate'], 2)
        })
    
    return {'lucky_names': result}


def get_surname_analysis():
    """Common surnames (potential family legacies)"""
    # Extract last names
    df_copy = df.copy()
    df_copy['LastName'] = df_copy['Name'].str.split().str[-1]
    
    surname_counts = df_copy.groupby('LastName').agg({
        'ID': 'nunique',
        'Medal': lambda x: x.notna().sum()
    }).reset_index()
    
    surname_counts.columns = ['Surname', 'Athletes', 'Medals']
    surname_counts = surname_counts[surname_counts['Athletes'] >= 5]  # At least 5 athletes
    surname_counts = surname_counts.sort_values('Athletes', ascending=False).head(30)
    
    result = []
    for _, row in surname_counts.iterrows():
        result.append({
            'surname': row['Surname'],
            'athletes': int(row['Athletes']),
            'medals': int(row['Medals']),
            'avg_medals_per_athlete': round(row['Medals'] / row['Athletes'], 2)
        })
    
    return {'family_legacies': result}


# ==========================================
# 12. COMEBACK STORIES
# ==========================================

def get_comeback_athletes():
    """Athletes who took breaks and returned"""
    athlete_years = df.groupby(['ID', 'Name', 'Team'])['Year'].apply(list).reset_index()
    
    comebacks = []
    for _, row in athlete_years.iterrows():
        years = sorted(row['Year'])
        if len(years) >= 3:
            # Check for gaps >= 8 years
            for i in range(len(years) - 1):
                gap = years[i + 1] - years[i]
                if gap >= 8:
                    athlete_data = df[df['ID'] == row['ID']]
                    medals_before = athlete_data[(athlete_data['Year'] <= years[i]) & 
                                                (athlete_data['Medal'].notna())].shape[0]
                    medals_after = athlete_data[(athlete_data['Year'] >= years[i + 1]) & 
                                               (athlete_data['Medal'].notna())].shape[0]
                    
                    comebacks.append({
                        'id': int(row['ID']),
                        'name': row['Name'],
                        'team': row['Team'],
                        'gap_years': int(gap),
                        'years_before_break': [int(y) for y in years if y <= years[i]],
                        'years_after_break': [int(y) for y in years if y >= years[i + 1]],
                        'medals_before': int(medals_before),
                        'medals_after': int(medals_after)
                    })
                    break
    
    # Sort by gap
    comebacks = sorted(comebacks, key=lambda x: x['gap_years'], reverse=True)[:20]
    
    return {'comeback_athletes': comebacks}


# ==========================================
# 13. CONSISTENCY INDEX
# ==========================================

def get_consistent_countries(min_olympics=10):
    """Countries that consistently win medals"""
    medals_df = df[df['Medal'].notna()].copy()
    
    country_years = medals_df.groupby(['NOC', 'Year']).size().reset_index()
    country_olympics = country_years.groupby('NOC')['Year'].nunique().reset_index()
    country_olympics.columns = ['NOC', 'Olympics_Count']
    
    # Filter countries with minimum olympics
    consistent = country_olympics[country_olympics['Olympics_Count'] >= min_olympics]
    
    result = []
    for _, row in consistent.iterrows():
        noc = row['NOC']
        country_data = medals_df[medals_df['NOC'] == noc]
        
        total_medals = country_data.shape[0]
        olympics_count = int(row['Olympics_Count'])
        
        result.append({
            'country': noc,
            'olympics_participated': olympics_count,
            'total_medals': int(total_medals),
            'avg_medals_per_olympics': round(total_medals / olympics_count, 2)
        })
    
    # Sort by consistency
    result = sorted(result, key=lambda x: x['olympics_participated'], reverse=True)
    
    return {'consistent_countries': result}


# ==========================================
# 14. MEDAL DROUGHT ANALYSIS
# ==========================================

def get_medal_droughts():
    """Countries with long gaps between medals"""
    medals_df = df[df['Medal'].notna()].copy()
    
    country_years = medals_df.groupby('NOC')['Year'].apply(sorted).reset_index()
    
    droughts = []
    for _, row in country_years.iterrows():
        years = row['Year']
        if len(years) >= 2:
            max_gap = 0
            gap_period = None
            
            for i in range(len(years) - 1):
                gap = years[i + 1] - years[i]
                if gap > max_gap:
                    max_gap = gap
                    gap_period = (years[i], years[i + 1])
            
            if max_gap >= 12:  # At least 12 years gap
                droughts.append({
                    'country': row['NOC'],
                    'drought_years': int(max_gap),
                    'from_year': int(gap_period[0]),
                    'to_year': int(gap_period[1]),
                    'total_medals_all_time': len(years)
                })
    
    # Sort by drought length
    droughts = sorted(droughts, key=lambda x: x['drought_years'], reverse=True)[:30]
    
    return {'medal_droughts': droughts}


# ==========================================
# 15. GOLD RUSH MOMENTS
# ==========================================

def get_gold_rush_moments(threshold=20):
    """Sudden spike in medals for a country"""
    medals_df = df[df['Medal'].notna()].copy()
    
    country_year_medals = medals_df.groupby(['NOC', 'Year']).size().reset_index()
    country_year_medals.columns = ['NOC', 'Year', 'Medals']
    
    # Calculate average for each country
    country_avg = country_year_medals.groupby('NOC')['Medals'].mean().reset_index()
    country_avg.columns = ['NOC', 'Avg_Medals']
    
    # Merge and find spikes
    merged = country_year_medals.merge(country_avg, on='NOC')
    merged['Spike'] = merged['Medals'] - merged['Avg_Medals']
    
    # Filter significant spikes
    spikes = merged[merged['Spike'] >= threshold].sort_values('Spike', ascending=False)
    
    result = []
    for _, row in spikes.head(30).iterrows():
        result.append({
            'country': row['NOC'],
            'year': int(row['Year']),
            'medals_won': int(row['Medals']),
            'average_medals': round(row['Avg_Medals'], 2),
            'spike': round(row['Spike'], 2)
        })
    
    return {'gold_rush_moments': result}


# ==========================================
# 16. ONE-HIT WONDERS
# ==========================================

def get_one_hit_wonders():
    """Athletes who participated once and won medal"""
    athlete_olympics = df.groupby('ID')['Games'].nunique().reset_index()
    athlete_olympics.columns = ['ID', 'Olympics_Count']
    
    one_timers = athlete_olympics[athlete_olympics['Olympics_Count'] == 1]['ID'].tolist()
    
    medalists = df[(df['ID'].isin(one_timers)) & (df['Medal'].notna())]
    
    result = []
    for athlete_id in medalists['ID'].unique():
        athlete_data = medalists[medalists['ID'] == athlete_id]
        medals = athlete_data['Medal'].value_counts().to_dict()
        
        result.append({
            'id': int(athlete_id),
            'name': athlete_data.iloc[0]['Name'],
            'team': athlete_data.iloc[0]['Team'],
            'year': int(athlete_data.iloc[0]['Year']),
            'sport': athlete_data.iloc[0]['Sport'],
            'gold': medals.get('Gold', 0),
            'silver': medals.get('Silver', 0),
            'bronze': medals.get('Bronze', 0),
            'total_medals': len(athlete_data)
        })
    
    # Sort by total medals
    result = sorted(result, key=lambda x: x['total_medals'], reverse=True)[:50]
    
    return {'one_hit_wonders': result}


# ==========================================
# 17. GENDER PARITY SCORE
# ==========================================

def get_gender_parity_by_country(year=None):
    """Gender balance in each country"""
    df_filtered = df.copy()
    if year:
        df_filtered = df_filtered[df_filtered['Year'] == year]
    
    gender_counts = df_filtered.groupby(['NOC', 'Sex']).size().unstack(fill_value=0)
    gender_counts['Total'] = gender_counts.sum(axis=1)
    gender_counts['Female_Percentage'] = (gender_counts.get('F', 0) / gender_counts['Total']) * 100
    gender_counts['Parity_Score'] = 100 - abs(50 - gender_counts['Female_Percentage'])
    
    gender_counts = gender_counts.sort_values('Parity_Score', ascending=False)
    
    result = []
    for noc in gender_counts.index:
        result.append({
            'country': noc,
            'male': int(gender_counts.loc[noc, 'M']) if 'M' in gender_counts.columns else 0,
            'female': int(gender_counts.loc[noc, 'F']) if 'F' in gender_counts.columns else 0,
            'total': int(gender_counts.loc[noc, 'Total']),
            'female_percentage': round(gender_counts.loc[noc, 'Female_Percentage'], 2),
            'parity_score': round(gender_counts.loc[noc, 'Parity_Score'], 2)
        })
    
    return {'gender_parity': result[:30]}


def get_gender_parity_by_sport():
    """Gender balance in each sport"""
    gender_counts = df.groupby(['Sport', 'Sex']).size().unstack(fill_value=0)
    gender_counts['Total'] = gender_counts.sum(axis=1)
    gender_counts['Female_Percentage'] = (gender_counts.get('F', 0) / gender_counts['Total']) * 100
    
    result = []
    for sport in gender_counts.index:
        result.append({
            'sport': sport,
            'male': int(gender_counts.loc[sport, 'M']) if 'M' in gender_counts.columns else 0,
            'female': int(gender_counts.loc[sport, 'F']) if 'F' in gender_counts.columns else 0,
            'total': int(gender_counts.loc[sport, 'Total']),
            'female_percentage': round(gender_counts.loc[sport, 'Female_Percentage'], 2)
        })
    
    # Sort by female percentage
    result = sorted(result, key=lambda x: x['female_percentage'])
    
    return {'gender_parity_by_sport': result}


# ==========================================
# 18. SMALL COUNTRIES BIG WINS
# ==========================================

def get_small_country_success():
    """Countries with less athletes but good medals"""
    total_athletes = df.groupby('NOC')['ID'].nunique().reset_index()
    total_medals = df[df['Medal'].notna()].groupby('NOC').size().reset_index()
    
    total_athletes.columns = ['NOC', 'Athletes']
    total_medals.columns = ['NOC', 'Medals']
    
    merged = total_athletes.merge(total_medals, on='NOC')
    merged = merged[merged['Athletes'] < 1000]  # Small countries
    merged['Medal_Per_Athlete'] = merged['Medals'] / merged['Athletes']
    merged = merged.sort_values('Medal_Per_Athlete', ascending=False)
    
    result = []
    for _, row in merged.head(30).iterrows():
        result.append({
            'country': row['NOC'],
            'total_athletes': int(row['Athletes']),
            'total_medals': int(row['Medals']),
            'medal_per_athlete': round(row['Medal_Per_Athlete'], 3)
        })
    
    return {'small_country_success': result}


# ==========================================
# 19. SEASONAL SPORTS CROSSOVER
# ==========================================

def get_seasonal_crossover_athletes():
    """Athletes who competed in both Summer and Winter"""
    athlete_seasons = df.groupby('ID')['Season'].unique().reset_index()
    
    crossover = athlete_seasons[athlete_seasons['Season'].apply(lambda x: len(x) > 1)]
    
    result = []
    for _, row in crossover.iterrows():
        athlete_id = row['ID']
        athlete_data = df[df['ID'] == athlete_id]
        
        summer_sports = athlete_data[athlete_data['Season'] == 'Summer']['Sport'].unique().tolist()
        winter_sports = athlete_data[athlete_data['Season'] == 'Winter']['Sport'].unique().tolist()
        
        medals = athlete_data[athlete_data['Medal'].notna()]
        
        result.append({
            'id': int(athlete_id),
            'name': athlete_data.iloc[0]['Name'],
            'team': athlete_data.iloc[0]['Team'],
            'summer_sports': summer_sports,
            'winter_sports': winter_sports,
            'total_medals': len(medals),
            'years_active': athlete_data['Year'].min() + ' - ' + str(athlete_data['Year'].max())
        })
    
    return {'crossover_athletes': result}


# ==========================================
# 20. AGE SWEET SPOT BY SPORT
# ==========================================

def get_age_sweet_spot_by_sport():
    """Optimal age for winning medals in each sport"""
    medals_df = df[(df['Medal'].notna()) & (df['Age'].notna())].copy()
    
    sport_age = medals_df.groupby('Sport')['Age'].agg(['mean', 'median', 'std']).reset_index()
    
    result = []
    for _, row in sport_age.iterrows():
        result.append({
            'sport': row['Sport'],
            'mean_age': round(row['mean'], 2),
            'median_age': round(row['median'], 2),
            'std_deviation': round(row['std'], 2),
            'age_range': f"{round(row['mean'] - row['std'], 1)} - {round(row['mean'] + row['std'], 1)}"
        })
    
    return {'age_sweet_spot': result}


# ==========================================
# 21. FIRST TIME MEDALISTS
# ==========================================

def get_first_time_medal_winners(year):
    """Countries winning their first medal in a specific year"""
    medals_df = df[df['Medal'].notna()].copy()
    
    # Get all countries' first medal year
    first_medal_year = medals_df.groupby('NOC')['Year'].min().reset_index()
    first_medal_year.columns = ['NOC', 'First_Medal_Year']
    
    # Filter for specific year
    first_timers = first_medal_year[first_medal_year['First_Medal_Year'] == year]
    
    result = []
    for _, row in first_timers.iterrows():
        noc = row['NOC']
        country_data = medals_df[(medals_df['NOC'] == noc) & (medals_df['Year'] == year)]
        
        result.append({
            'country': noc,
            'year': int(year),
            'first_medal_sport': country_data.iloc[0]['Sport'],
            'first_medal_type': country_data.iloc[0]['Medal'],
            'total_medals_that_year': len(country_data)
        })
    
    return {'first_time_medalists': result}


# ==========================================
# 22. PARTICIPATION DROP-OUT RATE
# ==========================================

def get_dropout_rate_by_sport():
    """Athletes who participated but didn't win medals (high failure rate sports)"""
    total_participants = df.groupby('Sport')['ID'].nunique().reset_index()
    medalists = df[df['Medal'].notna()].groupby('Sport')['ID'].nunique().reset_index()
    
    total_participants.columns = ['Sport', 'Total_Athletes']
    medalists.columns = ['Sport', 'Medalists']
    
    merged = total_participants.merge(medalists, on='Sport')
    merged['Non_Medalists'] = merged['Total_Athletes'] - merged['Medalists']
    merged['Failure_Rate'] = (merged['Non_Medalists'] / merged['Total_Athletes']) * 100
    merged = merged.sort_values('Failure_Rate', ascending=False)
    
    result = []
    for _, row in merged.iterrows():
        result.append({
            'sport': row['Sport'],
            'total_athletes': int(row['Total_Athletes']),
            'medalists': int(row['Medalists']),
            'non_medalists': int(row['Non_Medalists']),
            'failure_rate': round(row['Failure_Rate'], 2)
        })
    
    return {'dropout_rate_by_sport': result}


# ==========================================
# 23. GENERATE FULL REPORT
# ==========================================

def generate_advanced_insights():
    """Generate all advanced insights"""
    insights = {
        'name_analysis': {
            'common_names': get_most_common_names(30),
            'lucky_names': get_lucky_names(),
            'family_legacies': get_surname_analysis(),
            'name_trends': get_name_trends_by_decade()
        },
        'career_patterns': {
            'comebacks': get_comeback_athletes(),
            'one_hit_wonders': get_one_hit_wonders(),
            'crossover_athletes': get_seasonal_crossover_athletes()
        },
        'consistency': {
            'consistent_countries': get_consistent_countries(10),
            'medal_droughts': get_medal_droughts(),
            'gold_rush': get_gold_rush_moments(15)
        },
        'demographics': {
            'gender_parity_countries': get_gender_parity_by_country(),
            'gender_parity_sports': get_gender_parity_by_sport(),
            'small_country_wins': get_small_country_success()
        },
        'performance': {
            'age_sweet_spot': get_age_sweet_spot_by_sport(),
            'dropout_rates': get_dropout_rate_by_sport()
        }
    }
    
    return insights


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    # Test functions
    # print(json.dumps(get_lucky_names(), indent=2))
    # print(json.dumps(get_comeback_athletes(), indent=2))
    # print(json.dumps(get_gold_rush_moments(20), indent=2))
    
    pass
