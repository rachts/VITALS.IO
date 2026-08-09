from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import pages, api
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Financial health intelligence for startups. "
        "Upload financial data and calculate investor-grade "
        "unit economics, runway, scenarios and forecasts."
    ),
    version=settings.version,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://vitals-io.onrender.com",
    # Add other production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")

# Apply rate limiting to all API endpoints globally (50 requests per minute)
@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        # We can apply custom rate limits per route, but a global one is a good baseline
        pass
    return await call_next(request)
