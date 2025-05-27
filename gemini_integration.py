import google.generativeai as genai
from typing import Tuple, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Using Gemini Flash model

def extract_locations(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Use Gemini to extract source and destination locations from natural language query.
    """
    prompt = f"""
    Extract the source and destination locations from the following query about GIKI campus navigation.
    Valid locations are: Hostel 9, Central Block, Cafe, Tuck Shop, Sports Complex, Main Gate, Library, Faculty Block
    
    Query: {query}
    
    Respond in the following format only:
    SOURCE: <location>
    DESTINATION: <location>
    
    If a location is not found or unclear, respond with 'None' for that field.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse the response
        source = None
        destination = None
        
        for line in response_text.split('\n'):
            if line.startswith('SOURCE:'):
                source = line.replace('SOURCE:', '').strip()
                if source.lower() == 'none':
                    source = None
            elif line.startswith('DESTINATION:'):
                destination = line.replace('DESTINATION:', '').strip()
                if destination.lower() == 'none':
                    destination = None
        
        return source, destination
    
    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        return None, None

def generate_navigation_response(path: list, distance: float, query: str) -> str:
    """
    Generate a natural language response using Gemini based on the path and original query.
    """
    path_str = " → ".join(path)
    prompt = f"""
    Generate a helpful and natural response for a navigation query.
    
    Original query: {query}
    Path found: {path_str}
    Total distance: {distance} meters
    
    Generate a friendly response that includes:
    1. A direct answer about the route
    2. The total distance
    3. Any relevant tips about the route (e.g., landmarks to look out for)
    
    Keep the response concise but informative.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback to basic response if Gemini fails
        return f"The shortest path is: {path_str}\nTotal distance: {distance} meters" 