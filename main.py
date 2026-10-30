from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os

app = FastAPI(title="Damou Farm Backend API", version="1.0")

# تنظیمات CORS برای ارتباط با فایل‌های فرانت‌اند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اتصال به Supabase
SUPABASE_URL = "https://zjxnevkuiyawlkqawcsv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpqeG5ldmt1aXlhd2xrcWF3Y3N2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMDY2NDEsImV4cCI6MjEwMzY4MjY0MX0.6xdeTJuy-D6dFnSj9lhFM0-lPAoVYv72czplKdY6rs4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class LoginRequest(BaseModel):
    phone: str
    password: str

class RegisterRequest(BaseModel):
    manager_name: str
    farm_name: str
    phone: str
    email: str
    password: str

# اطلاعات ادمین ثابت سیستم
ADMIN_PHONE = "09031813270"
ADMIN_PASS = "M09031813270m"

@app.post("/api/login")
def login_user(data: LoginRequest):
    # بررسی دسترسی ادمین کل
    if data.phone == ADMIN_PHONE and data.password == ADMIN_PASS:
        return {
            "status": "success",
            "role": "admin",
            "message": "خوش آمدید، ادمین کل سامانه!",
            "phone": ADMIN_PHONE
        }
    
    # بررسی کاربران عادی در دیتابیس Supabase
    response = supabase.table("farms").select("*").eq("phone", data.phone).eq("password_hash", data.password).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, Хабаровск="شماره موبایل یا رمز عبور اشتباه است.")
    
    user = response.data[0]
    return {
        "status": "success",
        "role": "user",
        "farm_name": user.get("farm_name"),
        "phone": user.get("phone")
    }

@app.post("/api/register")
def register_user(data: RegisterRequest):
    # ثبت‌نام فارم جدید در Supabase
    new_farm = {
        "manager_name": data.manager_name,
        "farm_name": data.farm_name,
        "phone": data.phone,
        "email": data.email,
        "password_hash": data.password,
        "role": "user"
    }
    try:
        response = supabase.table("farms").insert(new_farm).execute()
        return {"status": "success", "message": "حساب کاربری با موفقیت ساخته شد."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)