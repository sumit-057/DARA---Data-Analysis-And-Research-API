import pandas as pd
import numpy as np
import os

# Resolve path relative to backend folder -> ../data/netflix_cleaned.csv
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'netflix_cleaned.csv'))
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    # Fallback: try to read from current directory or set empty DataFrame
    try:
        df = pd.read_csv('netflix_cleaned.csv')
    except Exception:
        df = pd.DataFrame()

def movie_by_titleAPI(title):
    title = title.strip().lower()
    
    movie = df[(df['type'].str.lower() == 'movie') &
               (df['title'].str.lower() == title)]
    
    if movie.empty:
        return {
            "message": f"No movie found with title '{title}'."
        }
    row = movie.iloc[0]
    
    row_dict = row.to_dict()
    # convert numpy.int64 to python int
    for key,value in row_dict.items():
        if isinstance(value ,(np.int64,np.float64)):
            row_dict[key] = int(value)
    return {
            "title": row_dict.get("title"),
            "main_director": row_dict.get("Main_director"),
            "cast": row_dict.get("cast"),
            "country": row_dict.get("country"),
            "release_year": row_dict.get("release_year"),
            "rating": row_dict.get("rating"),
            "duration": row_dict.get("duration"),
            "genres": row_dict.get("genres"),
            "description": row_dict.get("description")
        }

def tvshow_by_titleAPI(title):
    title = title.strip().lower()
    
    show = df[(df['type'].str.lower() == 'tv show') &
               (df['title'].str.lower() == title)]
    
    if show.empty:
        return {
            "message": f"No tv show found with title '{title}'."
        }
    row = show.iloc[0]
    
    row_dict = row.to_dict()
    # convert numpy.int64 to python int
    for key,value in row_dict.items():
        if isinstance(value ,(np.int64,np.float64)):
            row_dict[key] = int(value)
    return {
            "title": row_dict.get("title"),
            "main_director": row_dict.get("Main_director"),
            "cast": row_dict.get("cast"),
            "country": row_dict.get("country"),
            "release_year": row_dict.get("release_year"),
            "rating": row_dict.get("rating"),
            "duration": row_dict.get("duration"),
            "genres": row_dict.get("genres"),
            "description": row_dict.get("description")
        }

def movie_tv_distributionAPI():
    # Returns the count and percentage distribution of Movies and TV Shows.

    # Clean and standardize the 'type' column
    df['type'] = df['type'].fillna('Unspecified').astype(str).str.strip()

    # Count number of each type
    type_counts = df['type'].value_counts().reset_index()
    type_counts.columns = ['type', 'count']

    # Calculate percentage
    total = type_counts['count'].sum()
    type_counts['percentage'] = (type_counts['count'] / total * 100).round(2)

    # Convert to list of dicts for JSON output
    return type_counts.to_dict(orient='records')

def top_10_directorsAPI():
    # Ensure consistent naming
    df['Main_director'] = df['Main_director'].astype(str).str.strip()

    # Exclude unspecified directors
    directors = df[df['Main_director'].str.lower() != 'unspecified']

    # Group by director and count number of titles
    top_directors = (
        directors.groupby('Main_director')
        .size()
        .reset_index(name='title_count')
        .sort_values(by='title_count', ascending=False)
        .head(10)
    )
    # Convert to JSON serializable format
    return top_directors.to_dict(orient='records')

def country_statsAPI():
    # Returns top 10 countries where Netflix is mostly used (by number of titles).

    # Clean country data
    df['country'] = df['country'].fillna('Unspecified').astype(str)
    df['country'] = df['country'].apply(lambda x: x.split(',')[0].strip())  # handle multiple country entries

    # Exclude unspecified countries
    country_stats = (
        df[df['country'].str.lower() != 'unspecified']
        .groupby('country')
        .size()
        .reset_index(name='title_count')
        .sort_values(by='title_count', ascending=False)
        .head(10)
    )
    # Convert to list of dictionaries for JSON output
    return country_stats.to_dict(orient='records')

def clean_rating_column():
    """
    Cleans the 'rating' column by removing invalid entries like '74 min', '88 min', etc.
    Keeps only standard rating categories such as TV-MA, TV-14, R, PG, etc.
    """
    df['rating'] = df['rating'].fillna('Unspecified').astype(str).str.strip()

    # Define valid rating types (based on Netflix's standard ratings)
    valid_ratings = [
        'TV-MA', 'TV-14', 'TV-PG', 'TV-Y7', 'TV-Y', 'R', 'PG-13',
        'PG', 'G', 'NC-17', 'NR', 'UR', 'Unspecified'
    ]
    
    # Replace anything that looks like a duration (e.g., '74 min', '120 min', '1 Season')
    df['rating'] = df['rating'].apply(lambda x: x if x in valid_ratings else 'Unspecified')

clean_rating_column()

def rating_distributionAPI():
    """
    Returns the percentage distribution of titles based on their rating type
    (like TV-MA, TV-14, PG-13, etc.)
    """
    # Handle missing values
    df['rating'] = df['rating'].fillna('Unspecified').astype(str)

    # Count how many titles per rating
    rating_counts = df['rating'].value_counts().reset_index()
    rating_counts.columns = ['rating', 'count']

    # Calculate total and percentage
    total = rating_counts['count'].sum()
    rating_counts['percentage'] = (rating_counts['count'] / total * 100).round(2)

    # Convert to JSON serializable format
    return rating_counts.to_dict(orient='records')