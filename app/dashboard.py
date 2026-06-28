from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import BASE_DIR
from app.engine import portfolio_summary
from app.utils import get_recent_signals, get_stats

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

@router.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse('dashboard.html', {
        'request': request,
        'portfolio': portfolio_summary(),
        'stats': get_stats(),
        'signals': get_recent_signals(50),
    })
