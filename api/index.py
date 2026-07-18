from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="OTP Bomber API",
    description="Send OTP to 100+ websites instantly",
    version="1.0.0"
)

# --- Configuration ---
API_KEY = os.getenv("API_KEY", "your-secret-key-change-me")

# --- Models ---
class OTPRequest(BaseModel):
    phone_number: str  # 10-digit number

class OTPResponse(BaseModel):
    status: str
    message: str
    total_websites: int
    results: List[dict]

# --- Load Websites ---
def load_websites():
    """Load websites from JSON file"""
    try:
        # Try to load from file
        file_path = os.path.join(os.path.dirname(__file__), '..', 'websites.json')
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        # Fallback: Return minimal websites
        logger.warning("Websites.json not found, using fallback")
        return [
            {
                "name": "Test Site",
                "url": "https://example.com",
                "selectors": {"phone": ["input"], "submit": ["button"]},
                "type": "direct"
            }
        ]

WEBSITES = load_websites()

# --- Core Function (Simulated) ---
def send_otp_to_websites(phone: str) -> List[dict]:
    """
    Simulate sending OTP to all websites.
    In production, replace with actual Selenium logic.
    """
    results = []
    
    for website in WEBSITES:
        # Simulate sending OTP (replace with actual logic)
        import random
        success = random.random() > 0.3  # 70% success rate for demo
        
        results.append({
            "website": website['name'],
            "url": website['url'],
            "status": "success" if success else "failed",
            "message": f"OTP sent to {phone}" if success else "Failed to send OTP"
        })
    
    return results

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check - API is live"""
    return {
        "status": "🚀 OTP Bomber API is running on Vercel!",
        "total_websites": len(WEBSITES),
        "version": "1.0.0",
        "endpoints": {
            "/": "Health check",
            "/api/send-otp": "POST - Send OTP to all websites",
            "/api/websites": "GET - List all websites",
            "/docs": "Swagger documentation"
        }
    }

@app.post("/api/send-otp")
async def send_otp(request: OTPRequest, api_key: str = Header(...)):
    """
    Send OTP to all configured websites.
    
    Just enter your phone number and the API will start sending OTPs!
    """
    # Validate API key
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # Validate phone number (Indian format)
    phone = re.sub(r'[\s\-\(\)]', '', request.phone_number)
    if not re.match(r'^[6-9]\d{9}$', phone):
        raise HTTPException(
            status_code=400, 
            detail="Invalid phone number. Must be 10 digits starting with 6,7,8,9"
        )
    
    logger.info(f"Starting OTP send for {phone}")
    
    # Send OTP to all websites
    try:
        results = send_otp_to_websites(phone)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = len(results) - success_count
        
        return OTPResponse(
            status="completed",
            message=f"✅ Processed {len(results)} websites",
            total_websites=len(results),
            results=results
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites")
async def get_websites(api_key: str = Header(...)):
    """Get list of all configured websites"""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    return {
        "total": len(WEBSITES),
        "websites": [{"name": w['name'], "url": w['url']} for w in WEBSITES]
    }

@app.get("/api/status")
async def get_status():
    """Public status endpoint (no auth required)"""
    return {
        "status": "online",
        "total_websites": len(WEBSITES),
        "uptime": "100%",
        "last_deployment": datetime.utcnow().isoformat()
    }

# --- Error Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# --- This is required for Vercel ---
app_handler = app
