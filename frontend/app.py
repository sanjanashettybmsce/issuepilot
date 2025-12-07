"""Streamlit frontend for IssuePilot."""
import streamlit as st
import requests
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from frontend.styles import (
    COLORS,
    get_issue_type_style,
    get_priority_style,
    render_metric_card
)

# Configure Streamlit page
st.set_page_config(
    page_title="IssuePilot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success {
        color: #28A745;
        font-weight: bold;
    }
    .error {
        color: #DC3545;
        font-weight: bold;
    }
    .info {
        color: #0066CC;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def get_backend_url():
    """Return default backend URL (configuration removed)."""
    return "http://localhost:8000"


def display_analysis_result(result: dict):
    """Display analysis result in formatted UI."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Analysis Summary")
        st.write(result.get("summary", "N/A"))
    
    with col2:
        issue_type = result.get("type", "other")
        type_style = get_issue_type_style(issue_type)
        st.metric(
            "Issue Type",
            f"{type_style['label']}"
        )
    
    # Priority Score
    st.subheader("Priority")
    priority = result.get("priority_score", {})
    priority_score = priority.get("score", 3)
    priority_style = get_priority_style(priority_score)
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.metric(
            "Score",
            f"{priority_score}/5"
        )
    with col2:
        st.info(priority.get("justification", "N/A"))
    
    # Potential Impact
    st.subheader("Potential Impact")
    st.warning(result.get("potential_impact", "N/A"))
    
    # Suggested Labels
    st.subheader("Suggested Labels")
    labels = result.get("suggested_labels", [])
    cols = st.columns(len(labels) if labels else 1)
    for col, label in zip(cols, labels):
        with col:
            st.info(f"`{label}`")
    
    # Raw JSON
    with st.expander("Raw JSON Response"):
        st.json(result)


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("IssuePilot")
    st.markdown("""
    **AI-powered GitHub issue analysis with context enrichment**
    
    Analyze GitHub issues with enriched context including linked PRs, files, commits, and stack traces.
    """)
    
    # Get backend URL (sidebar removed)
    backend_url = get_backend_url()

    # Test backend connection and show status in main UI
    try:
        health_response = requests.get(f"{backend_url}/health", timeout=2)
        if health_response.status_code == 200:
            st.info("Backend connected")
        else:
            st.error("Backend error")
    except requests.exceptions.RequestException:
        st.error("Cannot reach backend")
    
    # Main input form
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        repo_url = st.text_input(
            "GitHub Repository",
            placeholder="e.g., torvalds/linux or python/cpython",
            help="Enter repository in format: owner/repo"
        )
    
    with col2:
        issue_number = st.number_input(
            "Issue Number",
            min_value=1,
            value=1,
            step=1
        )
    
    st.divider()
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyze_button = st.button("Analyze Issue", type="primary", use_container_width=True)
    
    with col2:
        st.button("Example Issues", use_container_width=True)
    
    # Process analysis
    if analyze_button:
        if not repo_url or not issue_number:
            st.error("Please enter both repository and issue number")
        else:
            try:
                with st.spinner("Analyzing issue... This may take a minute."):
                    # Make API request
                    response = requests.post(
                        f"{backend_url}/analyze",
                        json={
                            "repo_url": repo_url,
                            "issue_number": int(issue_number)
                        },
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Analysis complete!")
                        st.divider()
                        display_analysis_result(result)
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Analysis failed: {error_detail}")
                        
            except requests.exceptions.Timeout:
                st.error("Request timeout. Please try again or check the backend connection.")
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to backend at {backend_url}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Sidebar removed
    st.divider()
    st.caption("Built by Sanjana Shetty")


if __name__ == "__main__":
    main()
