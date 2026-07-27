# Shared HTML export template
# ============================

import html as _html
from ui.app_state import state


def render_html_report(content: str, title: str = "Report", rtl: bool = True) -> str:
    """Render a text report as a styled HTML page."""
    body_bg = '#1E1E2E' if state.theme == 'dark' else '#F5F7FA'
    pre_bg = '#2A2A3C' if state.theme == 'dark' else 'white'
    pre_color = '#E0E0E0' if state.theme == 'dark' else 'inherit'
    shadow = 'none' if state.theme == 'dark' else '0 2px 10px rgba(0,0,0,0.1)'
    dir_attr = "rtl" if rtl else "ltr"
    safe_title = _html.escape(str(title))
    safe_content = _html.escape(str(content))
    return f"""<!DOCTYPE html>
<html dir="{dir_attr}" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>{safe_title}</title>
    <style>
        body {{ font-family: 'Tahoma', sans-serif; background: {body_bg}; padding: 30px; }}
        pre {{ background: {pre_bg}; color: {pre_color}; padding: 30px; border-radius: 10px;
                box-shadow: {shadow}; direction: ltr; text-align: left; }}
    </style>
</head>
<body>
<pre>{safe_content}</pre>
</body>
</html>"""
