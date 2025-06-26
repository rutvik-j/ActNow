import streamlit as st
import streamlit.components.v1 as components
import re
import requests
import json
from streamlit.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="ActNow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'video_page' not in st.session_state:
    st.session_state.video_page = False
if 'youtube_url' not in st.session_state:
    st.session_state.youtube_url = ""  # Initialize with an empty string
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {}  # Store analysis results
if 'processing' not in st.session_state:
    st.session_state.processing = False

def get_video_analysis(video_url):
    """
    Analyzes a YouTube video using an external API.

    Args:
        video_url (str): The URL of the YouTube video to analyze.

    Returns:
        tuple: A tuple containing the strategies, summary, and quotes extracted from the video.
               Returns (None, None, None) if an error occurs.
    """
    # API endpoint
    url = st.secrets["url"]
    headers = {'Content-Type': 'application/json'}
    data = {'user_input': f'{video_url}'}

    try:
        # Send POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        data = json.loads(response.text)
        content = data['response']

        logger.info(response.text)

        # Split the content into sections
        sections = content.split('## ')

        # Initialize variables to store each section
        strategies = ""
        summary = ""
        quotes = ""
        
        if "NULL...understanding00" in content:
            st.error("This video does not contain the transcript in English and is unable to be processed. Please try another video :)")
            return None, None, None
        else: 
            # Attempt to extract structured content
            strategies_match = re.search(r'## StrategiesFromVideo:(.*?)(?=## SummaryFromVideo:)', content, re.DOTALL)
            summary_match = re.search(r'## SummaryFromVideo:(.*?)(?=## QuotesFromVideo:)', content, re.DOTALL)
            quotes_match = re.search(r'## QuotesFromVideo:(.*?)$', content, re.DOTALL)

            if strategies_match and summary_match and quotes_match:
                # If all sections are found, process as before
                strategies = strategies_match.group(1).strip()
                summary = summary_match.group(1).strip()
                quotes = quotes_match.group(1).strip()
                return strategies, summary, quotes
            else:
                # If the content doesn't match the expected format, display the raw content
                st.error("This video does not contain the transcript in English and is unable to be processed. Please try another video :)")
                return None, None, None

    except requests.exceptions.RequestException as e:
        st.error(f"Error: An error occurred while connecting to the API: {e}")
        return None, None, None
    except json.JSONDecodeError as e:
        st.error(f"Error: An error occurred while decoding the API response: {e}")
        return None, None, None
    except Exception as e:
        st.error(f"An error occurred while processing the video: {e}")
        return None, None, None

def copy_button_component(content, button_id):


    return f"""
    <div style="position: relative;">
        <h3 style="display: inline-block;">{content}</h3>
        <button onclick="copyToClipboard('{button_id}')" class="custom-copy">📋</button>
    </div>
    """

def display_video_page():
    """Displays the video analysis results, including the video, quotes, summary, and strategies."""
    # Back button
    if st.button("← Back"):
        st.session_state.video_page = False
        st.session_state.processing = False
        st.rerun()  # Important to prevent further execution of this function

    # Check if analysis data exists in session state
    if not st.session_state.analysis_data:
        st.error("No video analysis data available. Please submit a video URL first.")
        return

    strategies_res, summary_res, quotes_res = st.session_state.analysis_data['strategies'], st.session_state.analysis_data['summary'], st.session_state.analysis_data['quotes']

    # Embed YouTube video
    try:
        video_col, quotes_col = st.columns([0.7, 0.3], border=True)
        with video_col:
            st.video(f"{st.session_state.youtube_url}")
            
        # Quotes Section

        with quotes_col:
            
            st.subheader("Quotes")
            st.markdown(quotes_res, unsafe_allow_html=True)
            

        strategies,summary = st.columns([0.6, 0.4], border=True)

        # Strategies Section
        with strategies:
            # st_copy_to_clipboard(strategies_res)
            st.subheader("Strategies")
            # st.markdown(copy_button_component('Strategies','strategies-content'), unsafe_allow_html=True)
            st.markdown(f'<div id="strategies-content" class="custom-column-strategies">\n\n{strategies_res}\n\n</div>', unsafe_allow_html=True)


        with summary:
            st.subheader("Summary")
            st.markdown(f'<div class="custom-column-summary">\n\n{summary_res}\n\n</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Waiting for your input")

def is_valid_youtube_url(url):
    """
    Validates if a given URL is a valid YouTube URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid YouTube URL, False otherwise.
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    match = re.match(youtube_regex, url)
    return bool(match)

# Custom CSS for styling
card_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

    body {
        overflow: hidden; /* Hide scrollbars */
    }

    .custom-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 2.3vh;
        font-weight: 500;
        opacity: 0.35;
        text-align: center;
        line-height: 1.3; 
        padding-bottom:4vh; 
    }

    .custom_column {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s; /* Add transition for smooth hover effect */
    }

    .card:hover, .custom_column:hover {
        transform: translateY(-2px); /* Move card up slightly on hover */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); /* Increase shadow on hover */
    }   
    
    .custom-column-strategies {
        padding: 20px;
        margin-bottom: 10px;
        # height: 40vh;
        # overflow-y: auto;
    }
    .custom-column-summary {
        padding: 20px;
        margin-bottom: 10px;
        # height: 40vh;
        # overflow-y: auto;
    }

    .stVideo {
        border-radius: 10px;
        overflow: hidden;
    }

    .centered-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 20vh;
        width: 100%;
    }

    .centered-logo svg {
        width: 100%;
        height: auto;
        max-width: 300px; /* Adjust this value for desktop view */
    }

    @media (max-width: 768px) {
        .centered-logo svg {
            max-width: 200px; /* Adjust this value for mobile view */
        }
    }

    .stText {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 7vh;
        font-size: 24px;
    }

    br {
        display: none;

    }

    /* Media query for desktop screens */
    @media (min-width: 768px) {
    br {
            display: inline; /* Show <br> on desktop */
        }
    }

    .rotate { transform-origin: 50% 35%; animation: spin 3s linear infinite; }
    
    @keyframes spin { 100% { transform: rotate(360deg); } }

    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        color: rgba(0, 0, 0, 0.14);
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-family: 'Outfit', sans-serif;
    }

    @media screen and (max-width: 768px) {
        .footer {
            display: none;
            # position: fixed;
            # bottom: 0;
            # left: 0;
        }
    }

    </style>

"""



st.markdown(card_style, unsafe_allow_html=True)


def load_svg(file_path):
    """Loads an SVG file and returns its content."""
    with open(file_path, "r") as f:
        return f.read()
    
svg_content = load_svg("Act Now_.svg")

svg_content = re.sub(
    r'(<path[^>]*fill="#1D0BE3"[^>]*)',
    r'\1 class="rotate" style="transform-box: fill-box; transform-origin: center;"',
    svg_content
)

html_content = f"""
<div class="centered-logo">
    {svg_content}
</div>
"""

# Main App Logic
if not st.session_state.video_page:
    st.markdown(html_content, unsafe_allow_html=True)
    st.markdown(f"<div class='custom-subtitle'>Transform your passive watching to </br> active actionable strategies</div>", unsafe_allow_html=True)


    # Input Section
    col1, col2, col3 = st.columns([0.15, 0.4, 0.2])  # Adjust column widths as needed
    with col2:
        st.session_state.youtube_url = st.text_input("Copy & Paste YouTube Video URL", placeholder="https://www.youtube.com/watch?v=", label_visibility="hidden")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # Add space between the input and button
        process_button = st.button("→", disabled=st.session_state.processing, help="Process video for strategies")

    # Title and Subtitle
    if process_button:
        if st.session_state.youtube_url and is_valid_youtube_url(st.session_state.youtube_url):
            # Call the API and store the data in session state
            st.session_state.processing = True
            with col2:
                with st.spinner('Processing video...'):
                    strategies_res, summary_res, quotes_res = get_video_analysis(st.session_state.youtube_url)
                    if strategies_res and summary_res and quotes_res:
                        st.session_state.analysis_data = {'strategies': strategies_res, 'summary': summary_res, 'quotes': quotes_res}
                        st.session_state.video_page = True
                        st.session_state.processing = False
                        st.rerun()
                    else:
                        st.session_state.processing = False
        else:
            st.warning("Please enter a valid YouTube URL.")

else:
    display_video_page()

# Footer
st.markdown('<div class="footer">Made by Someone Somewhere </div>', unsafe_allow_html=True)
