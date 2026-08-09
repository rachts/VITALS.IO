from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/solutions", response_class=HTMLResponse)
async def solutions(request: Request):
    return templates.TemplateResponse(request=request, name="solutions.html")

@router.get("/product", response_class=HTMLResponse)
async def product(request: Request):
    return templates.TemplateResponse(request=request, name="product.html")

@router.get("/economics", response_class=HTMLResponse)
async def economics(request: Request):
    # Notice we REMOVED MISTRAL_API_KEY from the context here!
    return templates.TemplateResponse(
        request=request,
        name="economics.html",
        context={
            "SUPABASE_URL": settings.next_public_supabase_url or settings.supabase_url or "",
            "SUPABASE_ANON_KEY": settings.supabase_anon_key or "",
        },
    )

@router.get("/api", response_class=HTMLResponse)
async def api_docs(request: Request):
    return templates.TemplateResponse(request=request, name="api.html")

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "SUPABASE_URL": settings.next_public_supabase_url or settings.supabase_url or "",
            "SUPABASE_ANON_KEY": settings.supabase_anon_key or "",
        },
    )

@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={
            "SUPABASE_URL": settings.next_public_supabase_url or settings.supabase_url or "",
            "SUPABASE_ANON_KEY": settings.supabase_anon_key or "",
        },
    )

@router.get("/robots.txt", response_class=FileResponse)
async def robots():
    return FileResponse("static/robots.txt")

@router.get("/sitemap.xml", response_class=FileResponse)
async def sitemap():
    return FileResponse("static/sitemap.xml")
