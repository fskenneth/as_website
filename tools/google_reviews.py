from .google_places_api import get_google_reviews

def fetch_google_reviews():
    """
    Fetches real-time Google Reviews data for Astra Staging
    Uses Google Places API or cached data
    """
    return get_google_reviews()
