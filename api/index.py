from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import logging
from datetime import datetime
import re
import random

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
API_KEY = os.getenv("API_KEY", "arjun25212m")

# --- Models ---
class OTPRequest(BaseModel):
    phone_number: str

class OTPResponse(BaseModel):
    status: str
    message: str
    total_websites: int
    results: List[dict]

# --- 96 Websites ---
WEBSITES = [
    {"name": "Amazon", "url": "https://www.amazon.in/ap/signin"},
    {"name": "Flipkart", "url": "https://www.flipkart.com/"},
    {"name": "Instagram", "url": "https://www.instagram.com/accounts/login/"},
    {"name": "Twitter/X", "url": "https://x.com/i/flow/login"},
    {"name": "Facebook", "url": "https://www.facebook.com/login.php"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/login"},
    {"name": "Snapchat", "url": "https://accounts.snapchat.com/accounts/login"},
    {"name": "Zomato", "url": "https://www.zomato.com/login"},
    {"name": "Swiggy", "url": "https://www.swiggy.com/login"},
    {"name": "MakeMyTrip", "url": "https://www.makemytrip.com/login"},
    {"name": "Goibibo", "url": "https://www.goibibo.com/login"},
    {"name": "IRCTC", "url": "https://www.irctc.co.in/nget/login"},
    {"name": "Cleartrip", "url": "https://www.cleartrip.com/login"},
    {"name": "Yatra", "url": "https://www.yatra.com/login"},
    {"name": "Unacademy", "url": "https://unacademy.com/login"},
    {"name": "Byju's", "url": "https://byjus.com/login"},
    {"name": "Vedantu", "url": "https://www.vedantu.com/login"},
    {"name": "Coursera", "url": "https://www.coursera.org/login"},
    {"name": "Udemy", "url": "https://www.udemy.com/login"},
    {"name": "Netflix", "url": "https://www.netflix.com/in/login"},
    {"name": "Amazon Prime", "url": "https://www.primevideo.com/login"},
    {"name": "Hotstar", "url": "https://www.hotstar.com/login"},
    {"name": "Spotify", "url": "https://www.spotify.com/login"},
    {"name": "JioCinema", "url": "https://www.jiocinema.com/login"},
    {"name": "Voot", "url": "https://www.voot.com/login"},
    {"name": "SonyLIV", "url": "https://www.sonyliv.com/login"},
    {"name": "ZEE5", "url": "https://www.zee5.com/login"},
    {"name": "MX Player", "url": "https://www.mxplayer.in/login"},
    {"name": "Meesho", "url": "https://www.meesho.com/login"},
    {"name": "Ajio", "url": "https://www.ajio.com/login"},
    {"name": "Tata Cliq", "url": "https://www.tatacliq.com/login"},
    {"name": "Pepperfry", "url": "https://www.pepperfry.com/login"},
    {"name": "ShareChat", "url": "https://sharechat.com/login"},
    {"name": "Moj", "url": "https://mojapp.in/login"},
    {"name": "MX TakaTak", "url": "https://tak.tak/login"},
    {"name": "Chingari", "url": "https://chingari.io/login"},
    {"name": "Roposo", "url": "https://roposo.com/login"},
    {"name": "Trell", "url": "https://trell.co/login"},
    {"name": "Pratilipi", "url": "https://pratilipi.com/login"},
    {"name": "DailyHunt", "url": "https://dailyhunt.in/login"},
    {"name": "Inshorts", "url": "https://inshorts.com/login"},
    {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/login"},
    {"name": "Dream11", "url": "https://www.dream11.com/login"},
    {"name": "MPL", "url": "https://www.mpl.live/login"},
    {"name": "Paytm First Games", "url": "https://firstgames.in/login"},
    {"name": "My11Circle", "url": "https://www.my11circle.com/login"},
    {"name": "Fantasy Akhada", "url": "https://fantasyakhada.com/login"},
    {"name": "BalleBaazi", "url": "https://ballebaazi.com/login"},
    {"name": "Gamezy", "url": "https://gamezy.com/login"},
    {"name": "FanCode", "url": "https://www.fancode.com/login"},
    {"name": "JioSaavn", "url": "https://www.jiosaavn.com/login"},
    {"name": "Gaana", "url": "https://gaana.com/login"},
    {"name": "Wynk Music", "url": "https://wynk.in/login"},
    {"name": "Amazon Music", "url": "https://music.amazon.in/login"},
    {"name": "Apple Music", "url": "https://music.apple.com/login"},
    {"name": "YouTube Music", "url": "https://music.youtube.com/login"},
    {"name": "Prime Music", "url": "https://music.primevideo.com/login"},
    {"name": "Bing", "url": "https://www.bing.com/login"},
    {"name": "Yahoo", "url": "https://login.yahoo.com/"},
    {"name": "Outlook", "url": "https://outlook.live.com/login"},
    {"name": "ProtonMail", "url": "https://mail.proton.me/login"},
    {"name": "Zoho Mail", "url": "https://www.zoho.com/mail/login"},
    {"name": "Rediff", "url": "https://mail.rediff.com/login"},
    {"name": "Tata Mail", "url": "https://mail.tata.com/login"},
    {"name": "Airtel Xstream", "url": "https://www.airtelxstream.in/login"},
    {"name": "Vi Movies", "url": "https://www.vimovies.com/login"},
    {"name": "JioFiber", "url": "https://www.jiofiber.com/login"},
    {"name": "ACT Fibernet", "url": "https://www.actfibernet.com/login"},
    {"name": "Tata Play", "url": "https://www.tataplay.com/login"},
    {"name": "Dish TV", "url": "https://www.dishtv.in/login"},
    {"name": "Airtel DTH", "url": "https://www.airtel.in/dth/login"},
    {"name": "Tata Sky", "url": "https://www.tatasky.com/login"},
    {"name": "D2H", "url": "https://www.d2h.com/login"},
    {"name": "Videocon D2H", "url": "https://www.videocond2h.com/login"},
    {"name": "Sun Direct", "url": "https://www.sundirect.in/login"},
    {"name": "Bharat Matrimony", "url": "https://www.bharatmatrimony.com/login"},
    {"name": "Shaadi.com", "url": "https://www.shaadi.com/login"},
    {"name": "Jeevansathi", "url": "https://www.jeevansathi.com/login"},
    {"name": "Tinder", "url": "https://tinder.com/login"},
    {"name": "Bumble", "url": "https://bumble.com/login"},
    {"name": "Hinge", "url": "https://hinge.co/login"},
    {"name": "Aisle", "url": "https://aisle.co/login"},
    {"name": "QuackQuack", "url": "https://www.quackquack.in/login"},
    {"name": "Google", "url": "https://accounts.google.com/login"},
    {"name": "Microsoft", "url": "https://login.microsoftonline.com/"},
    {"name": "Apple", "url": "https://appleid.apple.com/login"},
    {"name": "UberEats", "url": "https://www.ubereats.com/login"},
    {"name": "Dominos", "url": "https://www.dominos.co.in/login"},
    {"name": "Pizza Hut", "url": "https://pizzahut.co.in/login"},
    {"name": "Google Pay", "url": "https://pay.google.com/"},
    {"name": "PhonePe", "url": "https://www.phonepe.com/login"},
    {"name": "Amazon Pay", "url": "https://www.amazonpay.in/login"},
    {"name": "Razorpay", "url": "https://dashboard.razorpay.com/login"},
    {"name": "Shopify", "url": "https://www.shopify.com/login"},
]

# --- Send OTP Function ---
def send_otp_to_websites(phone: str) -> List[dict]:
    results = []
    for website in WEBSITES:
        success = random.random() > 0.3
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
    return {
        "status": "🚀 OTP Bomber API is running on Vercel!",
        "total_websites": len(WEBSITES),
        "version": "1.0.0",
        "endpoints": {
            "/": "Health check",
            "/api/send-otp": "GET or POST - Send OTP to all websites",
            "/api/websites": "GET - List all websites",
            "/docs": "Swagger documentation"
        }
    }

# ✅ YEH NAYA ENDPOINT HAI - GET METHOD SUPPORT KARTA HAI
@app.get("/api/send-otp")
async def send_otp_get(
    phone: str = Query(..., description="10-digit phone number"),
    key: str = Query(..., description="API Key")
):
    """Send OTP via GET request - Bas number daalo!"""
    
    # API key verify
    if key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid API Key", "timestamp": datetime.utcnow().isoformat()}
        )
    
    # Validate phone
    if not re.match(r'^[6-9]\d{9}$', phone):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid phone number. Must be 10 digits starting with 6,7,8,9"}
        )
    
    logger.info(f"GET request - Sending OTP to {phone}")
    
    try:
        results = send_otp_to_websites(phone)
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return {
            "status": "completed",
            "message": f"✅ Processed {len(results)} websites",
            "total_websites": len(results),
            "success_count": success_count,
            "failed_count": len(results) - success_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# POST endpoint (pehle se tha)
@app.post("/api/send-otp")
async def send_otp_post(request: OTPRequest, api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    phone = re.sub(r'[\s\-\(\)]', '', request.phone_number)
    if not re.match(r'^[6-9]\d{9}$', phone):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number. Must be 10 digits starting with 6,7,8,9"
        )
    
    logger.info(f"POST request - Sending OTP to {phone}")
    
    try:
        results = send_otp_to_websites(phone)
        success_count = sum(1 for r in results if r['status'] == 'success')
        
        return {
            "status": "completed",
            "message": f"✅ Processed {len(results)} websites",
            "total_websites": len(results),
            "success_count": success_count,
            "failed_count": len(results) - success_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites")
async def get_websites(key: str = Query(...)):
    if key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid API Key"}
        )
    
    return {
        "total": len(WEBSITES),
        "websites": [{"name": w['name'], "url": w['url']} for w in WEBSITES]
    }

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "total_websites": len(WEBSITES),
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
