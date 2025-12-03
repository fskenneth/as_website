from fasthtml.common import *
from page.components import create_page
from starlette.staticfiles import StaticFiles

app, rt = fast_app(live=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@rt('/')
def home():
    """Home page with only header"""
    content = Div(
        # Body placeholder - content will be added later
        cls="home-content"
    )
    return create_page("Astra Staging", content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
