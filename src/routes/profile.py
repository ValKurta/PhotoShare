from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# Initialize router
router = APIRouter()

# Initialize Jinja2 templates (assuming templates directory is in the project root)
templates = Jinja2Templates(directory="templates")

@router.get("/profile-ui")
def profile_page(request: Request):
    """
    Serve the user profile and photos page.

    Arguments:
    - **request**: The incoming HTTP request.

    Returns:
    - The rendered profile.html template.
    """
    return templates.TemplateResponse("profile.html", {"request": request})
