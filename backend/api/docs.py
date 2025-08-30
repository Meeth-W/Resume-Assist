from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
import json

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def custom_docs(request: Request):
    app = request.app
    routes = [route for route in app.routes if isinstance(route, APIRoute)]

    # Group routes by tags
    grouped_routes = {}
    for route in routes:
        tag = route.tags[0] if route.tags else "General"
        if tag not in grouped_routes:
            grouped_routes[tag] = []
        grouped_routes[tag].append(route)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume Assist API Docs</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #e0e0e0;
                margin: 0;
                padding: 70px 0 50px; /* space for fixed header & footer */
            }
            header {
                background: #1f1f1f;
                padding: 15px;
                text-align: center;
                border-bottom: 1px solid #333;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                z-index: 10;
            }
            header h1 {
                margin: 0;
                font-size: 26px;
                color: #00bcd4;
            }
            .container {
                max-width: 900px;
                margin: 20px auto;
                padding: 20px;
                background: #1e1e1e;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }
            h2 {
                color: #00bcd4;
                margin-bottom: 10px;
            }
            .endpoint {
                background: #2a2a2a;
                margin: 10px 0;
                padding: 12px;
                border-radius: 5px;
                transition: 0.3s;
                cursor: pointer;
            }
            .endpoint:hover {
                background: #333333;
            }
            .endpoint-details {
                display: none;
                background: #1e1e1e;
                padding: 10px;
                margin-top: 5px;
                border-radius: 5px;
                font-size: 14px;
                color: #ccc;
            }
            footer {
                text-align: center;
                padding: 15px;
                font-size: 14px;
                color: #888;
                border-top: 1px solid #333;
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background: #1f1f1f;
            }
            footer a {
                color: #00bcd4;
                text-decoration: none;
            }
        </style>
        <script>
            function toggleDetails(id) {
                var section = document.getElementById(id);
                if (section.style.display === "block") {
                    section.style.display = "none";
                } else {
                    section.style.display = "block";
                }
            }
        </script>
    </head>
    <body>
        <header>
            <h1>Resume Assist API Documentation</h1>
        </header>
    """

    # Grouped endpoints
    for tag, tag_routes in grouped_routes.items():
        html += f"<div class='container'><h2>{tag} Endpoints</h2>"
        for idx, route in enumerate(tag_routes):
            methods = ", ".join(route.methods)
            route_id = f"details_{tag}_{idx}"
            details = {
                "description": route.summary or "No description provided",
                "parameters": [p.name for p in route.dependant.query_params],
                "requestBody": route.body_field.name if route.body_field else "None",
                "responses": list(route.response_model.__dict__.keys()) if route.response_model else "Default"
            }
            details_json = json.dumps(details, indent=4)

            html += f"""
            <div class="endpoint" onclick="toggleDetails('{route_id}')">
                <b>{methods}</b> - {route.path}
                <div id="{route_id}" class="endpoint-details"><pre>{details_json}</pre></div>
            </div>
            """
        html += "</div>"

    html += """
        <footer>
            <p>&copy; 2025 Resume Assist API | Built with <a href="https://fastapi.tiangolo.com/">FastAPI</a></p>
        </footer>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
