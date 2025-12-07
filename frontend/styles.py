"""UI styling utilities for Streamlit frontend."""

# Color scheme
COLORS = {
    "primary": "#0066CC",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    "light": "#F8F9FA",
    "dark": "#343A40"
}

# Issue type styling
ISSUE_TYPE_STYLES = {
    "bug": {
        "emoji": "🐛",
        "color": "#DC3545",
        "label": "Bug"
    },
    "feature_request": {
        "emoji": "✨",
        "color": "#0066CC",
        "label": "Feature Request"
    },
    "documentation": {
        "emoji": "📚",
        "color": "#6C757D",
        "label": "Documentation"
    },
    "question": {
        "emoji": "❓",
        "color": "#17A2B8",
        "label": "Question"
    },
    "other": {
        "emoji": "📋",
        "color": "#28A745",
        "label": "Other"
    }
}

# Priority styling
PRIORITY_STYLES = {
    1: {"emoji": "🟢", "label": "Low", "color": "#28A745"},
    2: {"emoji": "🟡", "label": "Medium", "color": "#FFC107"},
    3: {"emoji": "🟠", "label": "High", "color": "#FFA500"},
    4: {"emoji": "🔴", "label": "Critical", "color": "#DC3545"},
    5: {"emoji": "⚠️", "label": "Urgent", "color": "#8B0000"}
}


def get_issue_type_style(issue_type: str):
    """Get styling for issue type."""
    return ISSUE_TYPE_STYLES.get(issue_type, ISSUE_TYPE_STYLES["other"])


def get_priority_style(priority_score: int):
    """Get styling for priority score."""
    priority_score = max(1, min(priority_score, 5))
    return PRIORITY_STYLES.get(priority_score, PRIORITY_STYLES[3])


def render_metric_card(label: str, value: str, emoji: str = ""):
    """Render a metric card with label and value."""
    return f"""
    <div style='
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
    '>
        <h4>{emoji} {label}</h4>
        <h2 style='color: #0066CC; margin: 0;'>{value}</h2>
    </div>
    """
