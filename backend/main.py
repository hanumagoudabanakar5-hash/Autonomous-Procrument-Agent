from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from utils import upload_json_to_ipfs

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- AI PREDICTIVE LOOP ---
async def agent_loop():
    print("🧠 AI Agent Started: Running predictive inventory analysis...")
    while True:
        try:
            response = supabase.table("inventory").select("*").execute()
            for item in response.data:
                stock = item['current_stock']
                burn_rate = float(item.get('daily_burn_rate', 1.0))
                
                # AI Logic: How many days until we completely run out?
                days_remaining = stock / burn_rate if burn_rate > 0 else 999
                
                if days_remaining <= 7.0:
                    print(f"⚠️ AI PROCUREMENT ALERT: {item['item_name']} will run out in {days_remaining:.1f} days! Initiating smart contract restock...")
        except Exception as e:
            print(f"Agent Error: {e}")
        
        await asyncio.sleep(20)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(agent_loop())
    yield
    task.cancel()

app = FastAPI(title="PillProof Agentic Backend - V2", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION DEPENDENCY ---
def verify_user(x_user_id: str = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: No User ID provided")
    
    response = supabase.table("authorized_users").select("*").eq("username", x_user_id).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid User")
    
    return response.data[0] # Returns the user record {username, role}

# --- 1. LAB ONLY: REGISTER BATCH ---
@app.post("/register-batch")
async def register_batch(batch_data: dict, user: dict = Depends(verify_user)):
    if user['role'] != 'lab':
        raise HTTPException(status_code=403, detail="Forbidden: Only registered labs can mint batches.")
        
    try:
        ipfs_hash = await upload_json_to_ipfs(batch_data)
        if not ipfs_hash:
            raise HTTPException(status_code=500, detail="IPFS Upload Failed")

        supabase.table("batches").insert({
            "batch_number": batch_data.get("batch_number"),
            "ipfs_hash": ipfs_hash,
            "status": "Manufactured" # Start of Milestone
        }).execute()

        return {"message": f"Batch registered by {user['username']}", "ipfs_hash": ipfs_hash}
    except Exception as e:
        return {"error": str(e)}

# --- 2. SUPPLY CHAIN MILESTONES ---
@app.post("/update-status")
async def update_status(data: dict, user: dict = Depends(verify_user)):
    # Only labs (or delivery drivers in the future) can update shipping status
    if user['role'] != 'lab':
        raise HTTPException(status_code=403, detail="Forbidden")
        
    batch_num = data.get("batch_number")
    new_status = data.get("status") # e.g., "Shipped", "In Transit", "Delivered"
    
    supabase.table("batches").update({"status": new_status}).eq("batch_number", batch_num).execute()
    return {"message": f"Batch {batch_num} updated to {new_status}"}

# --- 3. PHARMACIST ONLY: VERIFY QR ---
@app.post("/verify-qr")
async def verify_qr(qr_data: dict, user: dict = Depends(verify_user)):
    if user['role'] != 'pharmacist':
        raise HTTPException(status_code=403, detail="Forbidden: Only Jan Aushadhi pharmacists can verify.")
        
    batch_num = qr_data.get("batch_number")
    response = supabase.table("batches").select("*").eq("batch_number", batch_num).execute()
    
    if not response.data:
        return {"verified": False, "message": "🚨 ALERT: Batch not found! Potential Counterfeit."}

    batch_record = response.data[0]
    return {
        "verified": True,
        "message": "✅ Genuine Batch Confirmed!",
        "current_status": batch_record["status"],
        "ipfs_hash": batch_record["ipfs_hash"]
    }
