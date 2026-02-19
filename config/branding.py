"""
Bristol Myers Squibb branding configuration.
"""

# BMS Brand Colors
BMS_COLORS = {
    'primary': '#BE2BBB',      # BMS Purple - main brand color
    'primary_dark': '#9B2399',  # Darker shade for hover states
    'primary_light': '#D666D4', # Lighter shade for backgrounds
    'secondary': '#003087',     # BMS Blue
    'accent': '#BE2BBB',        # Highlight color
    'success': '#00A758',       # Green for success states
    'warning': '#FF6B35',       # Orange for warnings
    'error': '#DC143C',         # Red for errors
    'info': '#0066CC',          # Blue for info
    'text_primary': '#2C3E50',  # Dark text
    'text_secondary': '#7F8C8D', # Light text
    'background': '#FFFFFF',    # White background
    'background_alt': '#F8F9FA', # Light grey background
    'border': '#E0E0E0',        # Border color
}

# Status badge colors
STATUS_COLORS = {
    'draft': '#6c757d',
    'submitted': '#0066CC',
    'under_review': '#FF6B35',
    'approved': '#00A758',
    'rejected': '#DC143C',
    'published': '#BE2BBB',
    'open': '#00A758'
}

# Typography
FONTS = {
    'regular': 'BMSRegular, Arial, sans-serif',
    'bold': 'BMSBold, Arial, sans-serif',
    'heading': 'BMSBold, Arial, sans-serif',
    'body': 'BMSRegular, Arial, sans-serif',
}

# Logo configuration
LOGO_PATH = 'assets/bms.png'
COMPANY_NAME = 'Bristol Myers Squibb'
APP_TITLE = 'Organizational Spotlight'
