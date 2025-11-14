import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Lead

app = FastAPI(
    title="Agency Backend",
    description="API for lead capture and service listings",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Agency backend running"}

# Public endpoint to list services for the frontend
class Service(BaseModel):
    slug: str
    title: str
    description: str
    bullets: List[str]
    cta: str

SERVICES: List[Service] = [
    Service(
        slug="paid-marketing",
        title="Paid Marketing (Ads & SEO)",
        description="Drive qualified traffic and revenue through data-driven ad campaigns and full-stack SEO.",
        bullets=[
            "Multi-channel: Google, Meta, LinkedIn, YouTube",
            "SEO sprints: technical, content, authority",
            "CRO and analytics baked in",
        ],
        cta="Book a growth audit",
    ),
    Service(
        slug="linkedin-branding",
        title="LinkedIn Personal Branding",
        description="Executive-grade content and profile systems that turn attention into inbound pipeline.",
        bullets=[
            "Weekly content engine + ghostwriting",
            "DM frameworks and audience building",
            "Performance dashboards",
        ],
        cta="Start your content engine",
    ),
    Service(
        slug="ghostwriting",
        title="Ghostwriting",
        description="Long-form articles, thought leadership, and narratives that move markets.",
        bullets=[
            "Research-backed narratives",
            "Editorial calendars",
            "Multi-channel syndication",
        ],
        cta="Request editorial plan",
    ),
    Service(
        slug="design",
        title="Graphic & Brand Design",
        description="Visual systems that convert: brand identity, landing pages, sales collateral.",
        bullets=[
            "Identity kits and design systems",
            "High-converting landing pages",
            "Presentation and sales design",
        ],
        cta="Explore design sprints",
    ),
    Service(
        slug="ai-automations",
        title="AI Automations",
        description="Automate workflows with AI agents, RPA, and integrations that save hours weekly.",
        bullets=[
            "CRM, ops, and content automations",
            "Custom GPTs and internal tools",
            "Secure, auditable pipelines",
        ],
        cta="Scope an automation",
    ),
]

@app.get("/api/services", response_model=List[Service])
def list_services():
    return SERVICES

# Lead capture endpoint using MongoDB
@app.post("/api/leads")
def create_lead(lead: Lead):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc_id = create_document("lead", lead)
    return {"status": "ok", "id": doc_id}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
