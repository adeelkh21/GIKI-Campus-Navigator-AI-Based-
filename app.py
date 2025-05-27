import streamlit as st
from graph_algorithms import CampusGraph
import google.generativeai as genai
from dotenv import load_dotenv
import os
import folium
from streamlit_folium import folium_static
import time

# Load environment variables
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="GIKI Campus Navigator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Google Gemini API
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Google API Key not found. Please check your .env file.")
    genai.configure(api_key=api_key)
    # Initialize the model - using Gemini Flash for faster responses
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ Error configuring Gemini API: {str(e)}")

# Initialize campus graph
@st.cache_resource
def get_campus_graph():
    return CampusGraph()

campus = get_campus_graph()

def get_gemini_response(question):
    """Get response from Gemini API"""
    try:
        if not question.strip():
            return "Please enter a valid question about GIKI campus."
            
        prompt = f"""You are a helpful assistant for GIKI (Ghulam Ishaq Khan Institute) campus. 
        Please provide accurate and helpful information about GIKI. Focus on:
        - Academic buildings and departments
        - Student facilities and services
        - Campus landmarks and important locations
        - Student life and activities
        - Campus history and facts
        
        If the question is about navigation or finding specific locations, suggest using the Path Finder tab.
        If you don't know the answer, be honest and say so.
        
        Question: {question}
        
        Answer:"""
        
        response = model.generate_content(prompt)
        if not response.text:
            return "I couldn't generate a response. Please try rephrasing your question."
        return response.text
    except Exception as e:
        return f"Error getting response: {str(e)}. Please check your internet connection and API key."

def main():
    # Custom CSS
    st.markdown("""
    <style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    /* Headers */
    .stMarkdown h1 {
        color: #00ff88;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .stMarkdown h2 {
        color: #00ff88;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        border-bottom: 2px solid #00ff88;
        padding-bottom: 0.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
        color: #1a1a2e;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    
    /* Select boxes */
    .stSelectbox>div>div>select {
        background-color: #2a2a3a;
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid #00ff88;
        padding: 8px;
    }
    
    /* Text input */
    .stTextInput>div>div>input {
        background-color: #2a2a3a;
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid #00ff88;
        padding: 8px;
    }
    
    /* Project info box */
    .project-info {
        background: linear-gradient(135deg, #2a2a3a 0%, #1a1a2e 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border: 1px solid #00ff88;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Algorithm info box */
    .algorithm-info {
        background: linear-gradient(135deg, #2a2a3a 0%, #1a1a2e 100%);
        color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00ff88;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .stSuccess {
        background-color: rgba(0,255,136,0.1);
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Error message */
    .stError {
        background-color: rgba(255,0,0,0.1);
        border: 1px solid #ff0000;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Warning message */
    .stWarning {
        background-color: rgba(255,165,0,0.1);
        border: 1px solid #ffa500;
        border-radius: 10px;
        padding: 10px;
    }

    /* Loading animation */
    .stSpinner > div {
        border-color: #00ff88 !important;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ff88;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00cc6a;
    }

    /* Performance bar */
    .performance-bar {
        background: #2a2a3a;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    .performance-bar-fill {
        background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%);
        height: 20px;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #00ff88; font-size: 2rem; margin-bottom: 0;">GIKI Campus Navigator</h1>
            <p style="color: #ffffff; font-size: 0.9rem;">Your Smart Campus Guide</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio("Navigation", ["🗺️ Path Finder", "📊 Algorithm Analysis", "❓ Campus Information"])
        st.markdown("---")
        
        st.markdown("### About")
        st.markdown("""
        <div style="color: #ffffff;">
        This app helps you navigate the GIKI campus and get information about various locations.
        
        - Use **Path Finder** to find the shortest route between locations
        - Use **Algorithm Analysis** to compare pathfinding algorithms
        - Use **Campus Information** to ask questions about GIKI
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Project Info")
        st.markdown("""
        <div class="project-info">
        <p style="color: #00ff88; font-weight: bold;">Developed by Nauman A. Murad, Hassan Rais, M. Adeel & Hamza Zaidi</p>
        <p>As part of semester project for Design and Analysis of Algorithms course</p>
        <p>Ghulam Ishaq Khan Institute of Engineering Sciences and Technology</p>
        </div>
        """, unsafe_allow_html=True)

    if page == "🗺️ Path Finder":
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #00ff88; font-size: 2.5rem; margin-bottom: 0;">AI Powered Campus Path Finder for GIKI</h1>
            <p style="color: #ffffff; font-size: 1.1rem;">Find the shortest route between any two locations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get available locations
        locations = list(campus.graph.nodes())
        
        # Create columns for inputs
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            start = st.selectbox("📍 Starting Point", locations, index=0)
        with col2:
            end = st.selectbox("🏁 Destination", locations, index=1)
        with col3:
            algorithm = st.selectbox("🔍 Algorithm", ["Dijkstra", "A*"], 
                                   help="Dijkstra: Guaranteed shortest path\nA*: Faster with heuristic")
        
        if st.button("Find Path 🚀"):
            try:
                with st.spinner("🔍 Finding the best path..."):
                    start_time = time.time()
                    path, distance = campus.find_path(start, end, 
                                                    algorithm="astar" if algorithm == "A*" else "dijkstra")
                    execution_time = time.time() - start_time
                
                # Display results in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Path found! Total distance: {distance:.2f} meters")
                    st.markdown("### Route:")
                    for i, location in enumerate(path, 1):
                        st.markdown(f"<div style='color: #ffffff;'>{i}. {location}</div>", unsafe_allow_html=True)
                    
                    # Display algorithm info
                    st.markdown("### Algorithm Info:")
                    if algorithm == "A*":
                        st.markdown("""
                        <div class="algorithm-info">
                        
                        - A* Algorithm: Uses heuristic (straight-line distance) to find path faster
                        
                        - Heuristic: Haversine distance between points
                        
                        - Guarantee: Still finds the shortest path
                        
                        - Time Complexity: O(E) in best case, O(E + V log V) in worst case
                        
                        - Space Complexity: O(V)
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="algorithm-info">
                        
                        - Dijkstra's Algorithm: Explores all possible paths
                        
                        - Guarantee: Always finds the shortest path
                        
                        - Time Complexity: O(E + V log V)
                        
                        - Space Complexity: O(V)
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"### Performance Metrics")
                    st.markdown(f"""
                    <div class="algorithm-info">
                    - Execution Time: {execution_time:.4f} seconds
                    - Path Length: {len(path)} nodes
                    - Total Distance: {distance:.2f} meters
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### Map View")
                    m = campus.visualize_path(path)
                    folium_static(m)
                
            except Exception as e:
                st.error(f"❌ Error finding path: {str(e)}")
    
    elif page == "📊 Algorithm Analysis":
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #00ff88; font-size: 2.5rem; margin-bottom: 0;">📊 Algorithm Analysis</h1>
            <p style="color: #ffffff; font-size: 1.1rem;">Compare the performance of pathfinding algorithms</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get available locations
        locations = list(campus.graph.nodes())
        
        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox("📍 Starting Point", locations, index=0)
        with col2:
            end = st.selectbox("🏁 Destination", locations, index=1)
        
        if st.button("Compare Algorithms 🚀"):
            try:
                with st.spinner("🔍 Analyzing algorithms..."):
                    # Run Dijkstra's algorithm
                    dijkstra_start = time.time()
                    dijkstra_path, dijkstra_distance = campus.find_path(start, end, algorithm="dijkstra")
                    dijkstra_time = time.time() - dijkstra_start
                    
                    # Run A* algorithm
                    astar_start = time.time()
                    astar_path, astar_distance = campus.find_path(start, end, algorithm="astar")
                    astar_time = time.time() - astar_start
                
                # Display comparison results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Dijkstra's Algorithm")
                    st.markdown(f"""
                    <div class="algorithm-info">
                    <div style="margin-bottom: 10px;">~ Execution Time: {dijkstra_time:.4f} seconds</div>
                    <div style="margin-bottom: 10px;">~ Path Length: {len(dijkstra_path)} nodes</div>
                    <div style="margin-bottom: 10px;">~ Total Distance: {dijkstra_distance:.2f} meters</div>
                    <div style="margin-bottom: 10px;">~ Time Complexity: O(E + V log V)</div>
                    <div style="margin-bottom: 10px;">~ Space Complexity: O(V)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Performance bar for Dijkstra
                    st.markdown("### Performance")
                    max_time = max(dijkstra_time, astar_time) if dijkstra_time > 0 and astar_time > 0 else 1
                    st.markdown(f"""
                    <div class="performance-bar">
                        <div style="color: #ffffff; margin-bottom: 5px;">Execution Time: {dijkstra_time:.4f}s</div>
                        <div class="performance-bar-fill" style="width: {min(100, (dijkstra_time/max_time)*100)}%;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### A* Algorithm")
                    st.markdown(f"""
                    <div class="algorithm-info">
                    <div style="margin-bottom: 10px;">~ Execution Time: {astar_time:.4f} seconds</div>
                    <div style="margin-bottom: 10px;">~ Path Length: {len(astar_path)} nodes</div>
                    <div style="margin-bottom: 10px;">~ Total Distance: {astar_distance:.2f} meters</div>
                    <div style="margin-bottom: 10px;">~ Time Complexity: O(E) in best case, O(E + V log V) in worst case</div>
                    <div style="margin-bottom: 10px;">~ Space Complexity: O(V)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Performance bar for A*
                    st.markdown("### Performance")
                    st.markdown(f"""
                    <div class="performance-bar">
                        <div style="color: #ffffff; margin-bottom: 5px;">Execution Time: {astar_time:.4f}s</div>
                        <div class="performance-bar-fill" style="width: {min(100, (astar_time/max_time)*100)}%;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display paths
                st.markdown("### Path Comparison")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Dijkstra's Path")
                    m_dijkstra = campus.visualize_path(dijkstra_path)
                    folium_static(m_dijkstra)
                
                with col2:
                    st.markdown("#### A* Path")
                    m_astar = campus.visualize_path(astar_path)
                    folium_static(m_astar)
                
            except Exception as e:
                st.error(f"❌ Error comparing algorithms: {str(e)}")
    
    elif page == "❓ Campus Information":
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #00ff88; font-size: 2.5rem; margin-bottom: 0;">❓ Ask About GIKI</h1>
            <p style="color: #ffffff; font-size: 1.1rem;">Get AI-powered answers about the campus</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Text input for questions
        question = st.text_input("Ask any question about GIKI:", 
                               placeholder="Example: What are the main academic buildings?")
        
        if st.button("Get Answer 💡"):
            if question:
                with st.spinner("🤔 Getting answer..."):
                    response = get_gemini_response(question)
                    st.markdown("### Answer:")
                    st.markdown(f"<div style='color: #ffffff;'>{response}</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter a question.")

if __name__ == "__main__":
    main() 