from flask import Flask, jsonify, request
from collections import OrderedDict
from flask_cors import CORS
import pandas as pd
import os

import netflix
import happiness
import energy
import ipl

# Import all functions
from olympic_api_functions import (
    get_top_countries_alltime,
    get_country_medals_by_year,
    get_country_ranking,
    get_most_decorated_athletes,
    get_physical_stats_by_sport,
    get_youngest_oldest_medalists,
    get_dominant_countries_per_sport,
    get_sport_evolution,
    get_participation_count_by_sport,
    get_gender_participation_trend,
    get_country_participation_growth,
    get_host_cities_list,
    get_summer_vs_winter_comparison,
    get_physical_changes_over_time,
    get_bmi_analysis_by_sport,
    get_medal_conversion_rate,
    get_underdog_nations,
    get_most_experienced_athletes,
    get_age_defying_athletes,
    get_sport_monopoly,
    get_extinct_sports,
    get_home_advantage_analysis,
    get_boycott_impact
)

from olympic_advanced_insights import (
    get_most_common_names,
    get_name_trends_by_decade,
    get_lucky_names,
    get_surname_analysis,
    get_comeback_athletes,
    get_consistent_countries,
    get_medal_droughts,
    get_gold_rush_moments,
    get_one_hit_wonders,
    get_gender_parity_by_country,
    get_gender_parity_by_sport,
    get_small_country_success,
    get_seasonal_crossover_athletes,
    get_age_sweet_spot_by_sport,
    get_first_time_medal_winners,
    get_dropout_rate_by_sport
)

app = Flask(__name__)
CORS(app)

# Load dataset globally (use a file in the backend folder)
data_path = os.path.join(os.path.dirname(__file__), 'athlete_events.csv')
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
else:
    # Fallback to an empty DataFrame to avoid immediate crashes; endpoints should handle empty df.
    df = pd.DataFrame()

# ==========================================
# ROOT & INFO ENDPOINTS
# ==========================================

@app.route('/')
def home():
    return jsonify({
        'message': '🏅 Olympic Data API - Welcome!',
        'version': '1.0',
        'total_records': len(df),
        'years_covered': f"{df['Year'].min()} - {df['Year'].max()}",
        'total_athletes': df['ID'].nunique(),
        'total_countries': df['NOC'].nunique(),
        'documentation': '/api/docs',
        'health_check': '/health'
    })


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'dataset_loaded': True,
        'records': len(df)
    })


@app.route('/api/docs')
def documentation():
    return jsonify({
        'api_name': 'Olympic Data API',
        'version': '1.0',
        'endpoints': {
            'medals': [
                {'path': '/api/medals/top-countries', 'params': 'top_n (optional, default=10)'},
                {'path': '/api/medals/country/<noc>', 'params': 'year (optional)'},
                {'path': '/api/medals/rankings', 'params': 'year (required), season (optional)'},
            ],
            'athletes': [
                {'path': '/api/athletes/top-decorated', 'params': 'top_n (optional)'},
                {'path': '/api/athletes/youngest-oldest'},
                {'path': '/api/athletes/most-experienced'},
                {'path': '/api/athletes/comebacks'},
                {'path': '/api/athletes/one-hit-wonders'},
                {'path': '/api/athletes/age-defying'},
            ],
            'sports': [
                {'path': '/api/sports/physical-stats', 'params': 'sport (optional)'},
                {'path': '/api/sports/evolution'},
                {'path': '/api/sports/extinct'},
                {'path': '/api/sports/monopoly'},
                {'path': '/api/sports/dominant/<sport>'},
                {'path': '/api/sports/participation'},
                {'path': '/api/sports/dropout-rate'},
            ],
            'countries': [
                {'path': '/api/countries/participation-growth'},
                {'path': '/api/countries/underdog'},
                {'path': '/api/countries/consistent'},
                {'path': '/api/countries/medal-droughts'},
                {'path': '/api/countries/conversion-rate', 'params': 'year, season'},
                {'path': '/api/countries/small-success'},
            ],
            'demographics': [
                {'path': '/api/demographics/gender-trend'},
                {'path': '/api/demographics/gender-parity'},
                {'path': '/api/demographics/gender-by-sport'},
            ],
            'insights': [
                {'path': '/api/insights/bmi-analysis'},
                {'path': '/api/insights/physical-evolution/<sport>'},
                {'path': '/api/insights/age-sweet-spot'},
                {'path': '/api/insights/gold-rush'},
                {'path': '/api/insights/boycott-impact'},
            ],
            'names': [
                {'path': '/api/names/common'},
                {'path': '/api/names/lucky'},
                {'path': '/api/names/family-legacies'},
                {'path': '/api/names/trends'},
            ],
            'search': [
                {'path': '/api/search/athlete', 'params': 'name (required)'},
                {'path': '/api/search/sport', 'params': 'sport (required)'},
            ]
        }
    })


# ==========================================
# MEDAL ENDPOINTS
# ==========================================

@app.route('/api/medals/top-countries', methods=['GET'])
def top_countries():
    top_n = request.args.get('top_n', default=10, type=int)
    result = get_top_countries_alltime(top_n)
    return jsonify(result)


@app.route('/api/medals/country/<noc>', methods=['GET'])
def country_medals(noc):
    year = request.args.get('year', type=int)
    result = get_country_medals_by_year(noc.upper(), year)
    return jsonify(result)


@app.route('/api/medals/rankings', methods=['GET'])
def medal_rankings():
    year = request.args.get('year', type=int)
    season = request.args.get('season', default='Summer', type=str)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    result = get_country_ranking(year, season)
    return jsonify(result)


# ==========================================
# ATHLETE ENDPOINTS
# ==========================================

@app.route('/api/athletes/top-decorated', methods=['GET'])
def top_decorated():
    top_n = request.args.get('top_n', default=10, type=int)
    result = get_most_decorated_athletes(top_n)
    return jsonify(result)


@app.route('/api/athletes/youngest-oldest', methods=['GET'])
def youngest_oldest():
    result = get_youngest_oldest_medalists()
    return jsonify(result)


@app.route('/api/athletes/most-experienced', methods=['GET'])
def most_experienced():
    result = get_most_experienced_athletes()
    return jsonify(result)


@app.route('/api/athletes/comebacks', methods=['GET'])
def comebacks():
    result = get_comeback_athletes()
    return jsonify(result)


@app.route('/api/athletes/one-hit-wonders', methods=['GET'])
def one_hit_wonders():
    result = get_one_hit_wonders()
    return jsonify(result)


@app.route('/api/athletes/age-defying', methods=['GET'])
def age_defying():
    result = get_age_defying_athletes()
    return jsonify(result)


@app.route('/api/athletes/crossover', methods=['GET'])
def crossover_athletes():
    result = get_seasonal_crossover_athletes()
    return jsonify(result)


# ==========================================
# SPORT ENDPOINTS
# ==========================================

@app.route('/api/sports/physical-stats', methods=['GET'])
def physical_stats():
    sport = request.args.get('sport', type=str)
    result = get_physical_stats_by_sport(sport)
    return jsonify(result)


@app.route('/api/sports/evolution', methods=['GET'])
def sport_evolution():
    result = get_sport_evolution()
    return jsonify(result)


@app.route('/api/sports/extinct', methods=['GET'])
def extinct_sports():
    result = get_extinct_sports()
    return jsonify(result)


@app.route('/api/sports/monopoly', methods=['GET'])
def sport_monopoly():
    result = get_sport_monopoly()
    return jsonify(result)


@app.route('/api/sports/dominant/<sport>', methods=['GET'])
def dominant_in_sport(sport):
    result = get_dominant_countries_per_sport(sport)
    return jsonify(result)


@app.route('/api/sports/participation', methods=['GET'])
def sport_participation():
    result = get_participation_count_by_sport()
    return jsonify(result)


@app.route('/api/sports/dropout-rate', methods=['GET'])
def dropout_rate():
    result = get_dropout_rate_by_sport()
    return jsonify(result)


# ==========================================
# COUNTRY ENDPOINTS
# ==========================================

@app.route('/api/countries/participation-growth', methods=['GET'])
def participation_growth():
    result = get_country_participation_growth()
    return jsonify(result)


@app.route('/api/countries/underdog', methods=['GET'])
def underdog_nations():
    result = get_underdog_nations()
    return jsonify(result)


@app.route('/api/countries/consistent', methods=['GET'])
def consistent_countries():
    min_olympics = request.args.get('min_olympics', default=10, type=int)
    result = get_consistent_countries(min_olympics)
    return jsonify(result)


@app.route('/api/countries/medal-droughts', methods=['GET'])
def medal_droughts():
    result = get_medal_droughts()
    return jsonify(result)


@app.route('/api/countries/conversion-rate', methods=['GET'])
def conversion_rate():
    year = request.args.get('year', type=int)
    season = request.args.get('season', default='Summer', type=str)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    result = get_medal_conversion_rate(year, season)
    return jsonify(result)


@app.route('/api/countries/small-success', methods=['GET'])
def small_country_success():
    result = get_small_country_success()
    return jsonify(result)


# ==========================================
# DEMOGRAPHICS ENDPOINTS
# ==========================================

@app.route('/api/demographics/gender-trend', methods=['GET'])
def gender_trend():
    result = get_gender_participation_trend()
    return jsonify(result)


@app.route('/api/demographics/gender-parity', methods=['GET'])
def gender_parity():
    year = request.args.get('year', type=int)
    result = get_gender_parity_by_country(year)
    return jsonify(result)


@app.route('/api/demographics/gender-by-sport', methods=['GET'])
def gender_by_sport():
    result = get_gender_parity_by_sport()
    return jsonify(result)


# ==========================================
# HOST & GEOGRAPHY ENDPOINTS
# ==========================================

@app.route('/api/host/cities', methods=['GET'])
def host_cities():
    result = get_host_cities_list()
    return jsonify(result)


@app.route('/api/host/home-advantage', methods=['GET'])
def home_advantage():
    result = get_home_advantage_analysis()
    return jsonify(result)


@app.route('/api/host/season-comparison', methods=['GET'])
def season_comparison():
    result = get_summer_vs_winter_comparison()
    return jsonify(result)


# ==========================================
# ADVANCED INSIGHTS ENDPOINTS
# ==========================================

@app.route('/api/insights/bmi-analysis', methods=['GET'])
def bmi_analysis():
    result = get_bmi_analysis_by_sport()
    return jsonify(result)


@app.route('/api/insights/physical-evolution/<sport>', methods=['GET'])
def physical_evolution(sport):
    result = get_physical_changes_over_time(sport)
    return jsonify(result)


@app.route('/api/insights/age-sweet-spot', methods=['GET'])
def age_sweet_spot():
    result = get_age_sweet_spot_by_sport()
    return jsonify(result)


@app.route('/api/insights/gold-rush', methods=['GET'])
def gold_rush():
    threshold = request.args.get('threshold', default=20, type=int)
    result = get_gold_rush_moments(threshold)
    return jsonify(result)


@app.route('/api/insights/boycott-impact', methods=['GET'])
def boycott_impact():
    result = get_boycott_impact()
    return jsonify(result)


# ==========================================
# NAME ANALYSIS ENDPOINTS
# ==========================================

@app.route('/api/names/common', methods=['GET'])
def common_names():
    top_n = request.args.get('top_n', default=20, type=int)
    result = get_most_common_names(top_n)
    return jsonify(result)


@app.route('/api/names/lucky', methods=['GET'])
def lucky_names():
    result = get_lucky_names()
    return jsonify(result)


@app.route('/api/names/family-legacies', methods=['GET'])
def family_legacies():
    result = get_surname_analysis()
    return jsonify(result)


@app.route('/api/names/trends', methods=['GET'])
def name_trends():
    result = get_name_trends_by_decade()
    return jsonify(result)


# ==========================================
# FIRST TIME ACHIEVEMENTS
# ==========================================

@app.route('/api/achievements/first-timers/<int:year>', methods=['GET'])
def first_timers(year):
    result = get_first_time_medal_winners(year)
    return jsonify(result)


# ==========================================
# SEARCH & FILTER ENDPOINTS
# ==========================================

@app.route('/api/search/athlete', methods=['GET'])
def search_athlete():
    name = request.args.get('name', type=str)
    if not name:
        return jsonify({'error': 'Name parameter required'}), 400
    
    results = df[df['Name'].str.contains(name, case=False, na=False)]
    
    if results.empty:
        return jsonify({'message': 'No athletes found', 'query': name})
    
    athletes = results.groupby(['ID', 'Name', 'Team', 'Sex']).agg({
        'Year': lambda x: sorted(x.unique().tolist()),
        'Medal': lambda x: x.notna().sum(),
        'Sport': lambda x: x.unique().tolist()
    }).reset_index()
    
    athletes.columns = ['ID', 'Name', 'Team', 'Sex', 'Years', 'Total_Medals', 'Sports']
    
    return jsonify({
        'query': name,
        'total_results': len(athletes),
        'athletes': athletes.to_dict('records')
    })


@app.route('/api/search/sport', methods=['GET'])
def search_sport():
    sport = request.args.get('sport', type=str)
    if not sport:
        return jsonify({'error': 'Sport parameter required'}), 400
    
    results = df[df['Sport'].str.contains(sport, case=False, na=False)]
    
    if results.empty:
        return jsonify({'message': 'No sports found', 'query': sport})
    
    stats = {
        'query': sport,
        'matching_sports': results['Sport'].unique().tolist(),
        'total_athletes': int(results['ID'].nunique()),
        'total_events': int(results['Event'].nunique()),
        'years_active': sorted(results['Year'].unique().tolist()),
        'top_countries': results['NOC'].value_counts().head(5).to_dict()
    }
    
    return jsonify(stats)

@app.route('/api/allBowlers-record')
def all_bowlers_api():
    return jsonify(ipl.allBowlers())
    

@app.route('/api/allBatsmen-record')
def all_batsman_api():
    return jsonify(ipl.allBatsmen())


@app.route('/api/team-record',methods=['GET'])
def team_api():
    team_name = request.args.get('team')
    result = ipl.teamAPI(team_name)
    return jsonify(result)


@app.route('/api/bowler-record',methods=['GET'])
def bowler_api():
    bowler_name = request.args.get('bowler')
    result = ipl.bowlerAPI(bowler_name)
    return jsonify(result)

@app.route('/api/batsman-record',methods=['GET'])
def batsman_api():
    batsman_name = request.args.get('batsman')
    result = ipl.batsmanAPI(batsman_name)
    return jsonify(result)


#-----------------------------Netflix Dataset APIS-------------------------------------

@app.route('/api/movie-title')
def movie_title():
    title = request.args.get("title")
    return jsonify(netflix.movie_by_titleAPI(title))

@app.route('/api/tv-title')
def tv_title():
    title = request.args.get("title")
    return jsonify(netflix.tvshow_by_titleAPI(title))

@app.route('/api/movie-tv-distribution', methods=['GET'])
def movie_tv_distribution_api():
    result = netflix.movie_tv_distributionAPI()
    return jsonify(result)

@app.route('/api/top-directors', methods=['GET'])
def top_directors_api():
    result = netflix.top_10_directorsAPI()
    return jsonify(result)

@app.route('/api/country-stats', methods=['GET'])
def country_stats_api():
    result = netflix.country_statsAPI()
    
    response = OrderedDict()
    response["data"] = result
    return jsonify(response)

@app.route('/api/rating-distribution', methods=['GET'])
def rating_distribution_api():
    result = netflix.rating_distributionAPI()
    return jsonify(result)

#-----------------------------World Happiness Report Dataset APIs--------------------------------

@app.route('/api/top-countries', methods=['GET'])
def top_happiness_countries():
    limit = int(request.args.get('limit', 10))
    result = happiness.top_countriesAPI(limit)
    return jsonify(result)

@app.route('/api/factor-impact', methods=['GET'])
def factor_impact():
    result = happiness.factor_impactAPI()
    return jsonify(result)

@app.route('/api/country-info', methods=['GET'])
def country_info():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Please provide ?name=country_name parameter."})
    result = happiness.country_infoAPI(name)
    return jsonify(result)

@app.route('/api/compare-countries', methods=['GET'])
def compare_countries():
    c1 = request.args.get('country1')
    c2 = request.args.get('country2')
    if not c1 or not c2:
        return jsonify({"error": "Please provide ?country1= and ?country2= parameters."})
    result = happiness.compare_countriesAPI(c1, c2)
    return jsonify(result)

@app.route('/api/happiness-gap', methods=['GET'])
def happiness_gap():
    region = request.args.get('region')
    result = happiness.happiness_gapAPI(region)
    return jsonify(result)

@app.route('/api/country-rank-trend', methods=['GET'])
def country_rank_trend():
    country = request.args.get('country')
    result = happiness.country_rank_trendAPI(country)
    return jsonify(result)  

@app.route('/api/factor-averages', methods=['GET'])
def factor_averages():
    result = happiness.factor_averagesAPI()
    return jsonify(result)

#-----------------------Global Energy Consumption dataset APIs----------------------------

@app.route("/api/global-summary")
def global_summary():
    return jsonify(energy.global_energy_summaryAPI())

@app.route("/api/renewable-leaders")
def renewable_leaders():
    limit = int(request.args.get("limit", 10))
    return jsonify(energy.renewable_leadersAPI(limit))

@app.route("/api/cleanest-country")
def cleanest():
    limit = int(request.args.get("limit", 10))
    return jsonify(energy.cleanest_countriesAPI(limit))

@app.route("/api/compare-price")
def compare_price():
    c1 = request.args.get("country1")
    c2 = request.args.get("country2")
    return jsonify(energy.energy_price_comparisonAPI(c1, c2))

@app.route("/api/energy-mix")
def energy_mix():
    country = request.args.get("country")
    return jsonify(energy.energy_mixAPI(country))

@app.route("/api/factor-summary")
def factor_summary():
    return jsonify(energy.factor_summaryAPI())


# ==========================================
# DETAILED API DOCUMENTATION ENDPOINT
# ==========================================

@app.route('/api/docs/detailed', methods=['GET'])
def detailed_docs():
    """Comprehensive API documentation for all datasets"""
    docs = {
        "api_version": "1.0",
        "title": "DARA - Data Analysis & Research API",
        "description": "Multi-dataset API providing insights on Olympics, Netflix, World Happiness, Global Energy, and IPL",
        "datasets": {
            "olympics": {
                "name": "Olympic Games Dataset",
                "description": "Historical data from 1896-2016 Olympic Games with 271,116 records covering 135,571 athletes from 230 countries",
                "endpoints": [
                    {
                        "path": "/api/medals/top-countries",
                        "method": "GET",
                        "description": "Get top performing countries of all time by medal count",
                        "parameters": [{"name": "top_n", "type": "integer", "required": False, "default": 10, "description": "Number of top countries to return"}],
                        "example_url": "/api/medals/top-countries?top_n=5",
                        "sample_response": {"top_countries": [{"country": "USA", "gold": 1000, "silver": 750, "bronze": 650, "total": 2400}]}
                    },
                    {
                        "path": "/api/medals/country/<noc>",
                        "method": "GET",
                        "description": "Get medal count for a specific country by year",
                        "parameters": [{"name": "noc", "type": "string", "required": True, "description": "Country NOC code (e.g., USA, IND, CHN)"}, {"name": "year", "type": "integer", "required": False, "description": "Specific Olympic year"}],
                        "example_url": "/api/medals/country/IND?year=2016",
                        "sample_response": {"country": "IND", "medals_by_year": [{"year": 2016, "gold": 2, "silver": 4, "bronze": 8}]}
                    },
                    {
                        "path": "/api/medals/rankings",
                        "method": "GET",
                        "description": "Get country rankings for a specific Olympics",
                        "parameters": [{"name": "year", "type": "integer", "required": True, "description": "Olympic year"}, {"name": "season", "type": "string", "required": False, "default": "Summer", "description": "Summer or Winter"}],
                        "example_url": "/api/medals/rankings?year=2016&season=Summer",
                        "sample_response": {"year": 2016, "season": "Summer", "rankings": [{"rank": 1, "country": "USA", "gold": 46, "silver": 37, "bronze": 38, "total": 121}]}
                    },
                    {
                        "path": "/api/athletes/top-decorated",
                        "method": "GET",
                        "description": "Get athletes with the most medals",
                        "parameters": [{"name": "top_n", "type": "integer", "required": False, "default": 10, "description": "Number of athletes to return"}],
                        "example_url": "/api/athletes/top-decorated?top_n=5",
                        "sample_response": {"most_decorated_athletes": [{"id": 1, "name": "Michael Phelps", "team": "USA", "sex": "M", "total_medals": 28, "gold": 23, "silver": 3, "bronze": 2}]}
                    },
                    {
                        "path": "/api/athletes/youngest-oldest",
                        "method": "GET",
                        "description": "Get youngest and oldest medalists in Olympic history",
                        "parameters": [],
                        "example_url": "/api/athletes/youngest-oldest",
                        "sample_response": {"youngest": {"name": "Dimitrios Loundras", "age": 10}, "oldest": {"name": "Oscar Swahn", "age": 72}}
                    },
                    {
                        "path": "/api/sports/physical-stats",
                        "method": "GET",
                        "description": "Get average physical stats (height, weight, age) by sport",
                        "parameters": [{"name": "sport", "type": "string", "required": False, "description": "Specific sport name"}],
                        "example_url": "/api/sports/physical-stats?sport=Basketball",
                        "sample_response": {"sports": [{"sport": "Basketball", "avg_height": 198, "avg_weight": 100, "avg_age": 28}]}
                    },
                    {
                        "path": "/api/sports/evolution",
                        "method": "GET",
                        "description": "Track how sports evolved over time (new/removed sports)",
                        "parameters": [],
                        "example_url": "/api/sports/evolution",
                        "sample_response": {"sports_history": [{"decade": 1896, "new_sports": ["Athletics", "Swimming"], "removed_sports": []}]}
                    },
                    {
                        "path": "/api/countries/participation-growth",
                        "method": "GET",
                        "description": "Track country participation growth across Olympics",
                        "parameters": [],
                        "example_url": "/api/countries/participation-growth",
                        "sample_response": {"countries_growth": [{"country": "India", "first_olympics": 1900, "total_olympics": 27, "growth_trend": "increasing"}]}
                    },
                    {
                        "path": "/api/demographics/gender-trend",
                        "method": "GET",
                        "description": "Get gender participation trends over time",
                        "parameters": [],
                        "example_url": "/api/demographics/gender-trend",
                        "sample_response": {"gender_trend": [{"year": 2016, "male_athletes": 6500, "female_athletes": 4900}]}
                    },
                    {
                        "path": "/api/host/cities",
                        "method": "GET",
                        "description": "Get list of Olympic host cities and years",
                        "parameters": [],
                        "example_url": "/api/host/cities",
                        "sample_response": {"host_cities": [{"city": "Tokyo", "year": 2016, "season": "Summer", "country": "Japan"}]}
                    },
                    {
                        "path": "/api/search/athlete",
                        "method": "GET",
                        "description": "Search for athletes by name",
                        "parameters": [{"name": "name", "type": "string", "required": True, "description": "Athlete name or partial name"}],
                        "example_url": "/api/search/athlete?name=Phelps",
                        "sample_response": {"query": "Phelps", "total_results": 1, "athletes": [{"name": "Michael Phelps", "team": "USA", "total_medals": 28}]}
                    }
                ]
            },
            "netflix": {
                "name": "Netflix Dataset",
                "description": "Netflix content library with movies and TV shows, including ratings, genres, and directors",
                "endpoints": [
                    {
                        "path": "/api/movie-title",
                        "method": "GET",
                        "description": "Get movie details by title",
                        "parameters": [{"name": "title", "type": "string", "required": True, "description": "Exact movie title"}],
                        "example_url": "/api/movie-title?title=Inception",
                        "sample_response": {"title": "Inception", "main_director": "Christopher Nolan", "cast": "Leonardo DiCaprio, Marion Cotillard", "release_year": 2010, "rating": "PG-13"}
                    },
                    {
                        "path": "/api/tv-title",
                        "method": "GET",
                        "description": "Get TV show details by title",
                        "parameters": [{"name": "title", "type": "string", "required": True, "description": "Exact TV show title"}],
                        "example_url": "/api/tv-title?title=Breaking%20Bad",
                        "sample_response": {"title": "Breaking Bad", "main_director": "Vince Gilligan", "cast": "Bryan Cranston, Aaron Paul"}
                    },
                    {
                        "path": "/api/movie-tv-distribution",
                        "method": "GET",
                        "description": "Get distribution of movies vs TV shows",
                        "parameters": [],
                        "example_url": "/api/movie-tv-distribution",
                        "sample_response": {"data": [{"type": "Movie", "count": 6000, "percentage": 60.5}, {"type": "TV Show", "count": 3900, "percentage": 39.5}]}
                    },
                    {
                        "path": "/api/top-directors",
                        "method": "GET",
                        "description": "Get top directors by number of titles",
                        "parameters": [],
                        "example_url": "/api/top-directors",
                        "sample_response": {"data": [{"Main_director": "Rajiv Chilaka", "title_count": 14}, {"Main_director": "Steven Spielberg", "title_count": 9}]}
                    },
                    {
                        "path": "/api/country-stats",
                        "method": "GET",
                        "description": "Get content distribution by country",
                        "parameters": [],
                        "example_url": "/api/country-stats",
                        "sample_response": {"data": [{"country": "United States", "title_count": 3000}, {"country": "India", "title_count": 1200}]}
                    },
                    {
                        "path": "/api/rating-distribution",
                        "method": "GET",
                        "description": "Get distribution of content ratings (TV-MA, PG-13, etc.)",
                        "parameters": [],
                        "example_url": "/api/rating-distribution",
                        "sample_response": {"data": [{"rating": "TV-MA", "count": 2500, "percentage": 25.0}]}
                    }
                ]
            },
            "happiness": {
                "name": "World Happiness Report Dataset",
                "description": "World Happiness scores and contributing factors for countries across multiple years",
                "endpoints": [
                    {
                        "path": "/api/top-countries",
                        "method": "GET",
                        "description": "Get top countries by happiness score",
                        "parameters": [{"name": "limit", "type": "integer", "required": False, "default": 10, "description": "Number of countries to return"}],
                        "example_url": "/api/top-countries?limit=5",
                        "sample_response": {"data": [{"Country": "Finland", "Region": "Western Europe", "Happiness_Score": 7.769, "Happiness_Rank": 1}]}
                    },
                    {
                        "path": "/api/factor-impact",
                        "method": "GET",
                        "description": "Get correlation of factors with happiness score",
                        "parameters": [],
                        "example_url": "/api/factor-impact",
                        "sample_response": [{"factor": "Economy (GDP per Capita)", "correlation_with_happiness": 0.787}, {"factor": "Health (Life Expectancy)", "correlation_with_happiness": 0.743}]
                    },
                    {
                        "path": "/api/country-info",
                        "method": "GET",
                        "description": "Get detailed happiness info for a specific country",
                        "parameters": [{"name": "name", "type": "string", "required": True, "description": "Country name"}],
                        "example_url": "/api/country-info?name=India",
                        "sample_response": {"result": {"Country": "India", "Happiness_Score": 5.577, "Economy": 1.233, "Family": 1.081}}
                    },
                    {
                        "path": "/api/compare-countries",
                        "method": "GET",
                        "description": "Compare happiness scores between two countries",
                        "parameters": [{"name": "country1", "type": "string", "required": True}, {"name": "country2", "type": "string", "required": True}],
                        "example_url": "/api/compare-countries?country1=India&country2=Finland",
                        "sample_response": {"summary": {"more_happy_country": "Finland", "score_difference": 2.2}}
                    },
                    {
                        "path": "/api/factor-averages",
                        "method": "GET",
                        "description": "Get global averages and extremes for happiness factors",
                        "parameters": [],
                        "example_url": "/api/factor-averages",
                        "sample_response": [{"factor": "Economy (GDP per Capita)", "global_average": 0.95, "max_value": 1.85, "max_value_country": "Luxembourg"}]
                    }
                ]
            },
            "energy": {
                "name": "Global Energy Consumption Dataset",
                "description": "Energy consumption, renewable energy share, and carbon emissions data by country",
                "endpoints": [
                    {
                        "path": "/api/global-summary",
                        "method": "GET",
                        "description": "Get global energy consumption summary",
                        "parameters": [],
                        "example_url": "/api/global-summary",
                        "sample_response": {"summary": {"total_countries": 195, "highest_energy_country": "China", "global_avg_energy_consumption_TWh": 3.45, "global_avg_renewables_percent": 12.5}}
                    },
                    {
                        "path": "/api/renewable-leaders",
                        "method": "GET",
                        "description": "Get countries leading in renewable energy",
                        "parameters": [{"name": "limit", "type": "integer", "required": False, "default": 10, "description": "Number of countries to return"}],
                        "example_url": "/api/renewable-leaders?limit=5",
                        "sample_response": {"data": [{"Country": "Iceland", "Year": 2020, "Renewable Energy Share (%)": 98.5}]}
                    },
                    {
                        "path": "/api/cleanest-country",
                        "method": "GET",
                        "description": "Get countries with lowest carbon emissions",
                        "parameters": [{"name": "limit", "type": "integer", "required": False, "default": 10, "description": "Number of countries to return"}],
                        "example_url": "/api/cleanest-country?limit=5",
                        "sample_response": {"units": {"emissions": "Million Tons CO2"}, "data": [{"Country": "Bahrain", "Year": 2019, "Carbon Emissions (Million Tons)": 0.1}]}
                    },
                    {
                        "path": "/api/compare-price",
                        "method": "GET",
                        "description": "Compare energy prices between two countries",
                        "parameters": [{"name": "country1", "type": "string", "required": True}, {"name": "country2", "type": "string", "required": True}],
                        "example_url": "/api/compare-price?country1=USA&country2=India",
                        "sample_response": {"summary": {"higher_price_country": "USA", "difference_usd_per_kwh": 0.05}}
                    },
                    {
                        "path": "/api/energy-mix",
                        "method": "GET",
                        "description": "Get energy source and usage breakdown for a country",
                        "parameters": [{"name": "country", "type": "string", "required": True, "description": "Country name"}],
                        "example_url": "/api/energy-mix?country=Norway",
                        "sample_response": {"energy_source_breakdown": {"renewable_energy_share_percent": 95.5, "fossil_fuel_dependency_percent": 4.5}}
                    },
                    {
                        "path": "/api/factor-summary",
                        "method": "GET",
                        "description": "Get summary stats for all energy factors",
                        "parameters": [],
                        "example_url": "/api/factor-summary",
                        "sample_response": [{"factor": "Total Energy Consumption (TWh)", "average": 3.45, "maximum": 156.2, "max_country": "China"}]
                    }
                ]
            },
            "ipl": {
                "name": "IPL (Indian Premier League) Dataset",
                "description": "Cricket statistics from Indian Premier League (2008-2022)",
                "endpoints": [
                    {
                        "path": "/api/allBatsmen-record",
                        "method": "GET",
                        "description": "Get all batsmen records and statistics",
                        "parameters": [],
                        "example_url": "/api/allBatsmen-record",
                        "sample_response": {"batsmen": [{"name": "Virat Kohli", "runs": 6000, "matches": 150, "average": 45.5}]}
                    },
                    {
                        "path": "/api/allBowlers-record",
                        "method": "GET",
                        "description": "Get all bowlers records and statistics",
                        "parameters": [],
                        "example_url": "/api/allBowlers-record",
                        "sample_response": {"bowlers": [{"name": "Jasprit Bumrah", "wickets": 120, "matches": 100, "average": 25.3}]}
                    },
                    {
                        "path": "/api/team-record",
                        "method": "GET",
                        "description": "Get team statistics",
                        "parameters": [{"name": "team", "type": "string", "required": True, "description": "Team name"}],
                        "example_url": "/api/team-record?team=Mumbai%20Indians",
                        "sample_response": {"team": "Mumbai Indians", "wins": 80, "losses": 45, "win_percentage": 64.0}
                    },
                    {
                        "path": "/api/batsman-record",
                        "method": "GET",
                        "description": "Get specific batsman statistics",
                        "parameters": [{"name": "batsman", "type": "string", "required": True, "description": "Batsman name"}],
                        "example_url": "/api/batsman-record?batsman=Virat%20Kohli",
                        "sample_response": {"name": "Virat Kohli", "runs": 6000, "matches": 150, "centuries": 46, "average": 45.5}
                    },
                    {
                        "path": "/api/bowler-record",
                        "method": "GET",
                        "description": "Get specific bowler statistics",
                        "parameters": [{"name": "bowler", "type": "string", "required": True, "description": "Bowler name"}],
                        "example_url": "/api/bowler-record?bowler=Jasprit%20Bumrah",
                        "sample_response": {"name": "Jasprit Bumrah", "wickets": 120, "matches": 100, "economy": 7.2, "average": 25.3}
                    }
                ]
            }
        }
    }
    return jsonify(docs)


# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check /api/docs for available endpoints'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Olympic Data API Server Starting...")
    print("="*50)
    print(f"Dataset loaded: {len(df)} records")
    print(f"Total athletes: {df['ID'].nunique()}")
    print(f"Total countries: {df['NOC'].nunique()}")
    print(f"Years covered: {df['Year'].min()} - {df['Year'].max()}")
    print("\nServer running at: http://localhost:5000")
    print("Documentation: http://localhost:5000/api/docs")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)



