import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Food Delivery Hybrid Gateway")

# Config CORS agar frontend bisa akses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping URL Service (Nama Host Docker)
SERVICES = {
    "user": os.getenv("USER_SERVICE_URL", "http://user-service:8000"),
    "restaurant": os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://order-service:8000"),
    "payment": os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000"),
    "driver": os.getenv("DRIVER_SERVICE_URL", "http://driver-service:8000"),
}

async def forward_request(target_url: str, request: Request):
    """
    Fungsi proxy yang AMAN. Membersihkan header agar tidak crash.
    """
    async with httpx.AsyncClient() as client:
        try:
            # 1. Baca Body
            body = await request.body()
            
            # 2. Bersihkan Header (PENTING: Jangan forward Host & Content-Length)
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("content-length", None)
            
            # 3. Kirim Request ke Microservice
            resp = await client.request(
                method=request.method,
                url=target_url,
                params=dict(request.query_params),
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            # 4. Kembalikan Response ke Frontend
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
        except httpx.ConnectError:
            return Response(content=f"Cannot connect to service at {target_url}", status_code=503)
        except Exception as e:
            return Response(content=f"Gateway Error: {str(e)}", status_code=502)

# --- 1. ROUTING UNTUK GRAPHQL (Hybrid Support) ---
@app.api_route("/{service_name}/graphql", methods=["GET", "POST"])
async def graphql_proxy(service_name: str, request: Request):
    if service_name not in SERVICES:
        return Response(content="Service not found", status_code=404)
    target_url = f"{SERVICES[service_name]}/graphql"
    return await forward_request(target_url, request)

# --- 2. ROUTING UNTUK REST API (Frontend Lama) ---
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def rest_proxy(path: str, request: Request):
    """
    Menangani request dari Frontend seperti:
    POST /api/users/auth/login
    GET /api/restaurants
    """
    # Deteksi service berdasarkan kata pertama di URL
    service_key = ""
    if path.startswith("users"): service_key = "user"
    elif path.startswith("restaurants"): service_key = "restaurant"
    elif path.startswith("orders"): service_key = "order"
    elif path.startswith("payments"): service_key = "payment"
    elif path.startswith("drivers"): service_key = "driver"
    
    if not service_key:
        return Response(content=f"No service mapped for path: {path}", status_code=404)

    # --- PATH REWRITING LOGIC ---
    # User Service di backend path-nya adalah /auth/login, BUKAN /users/auth/login
    # Jadi kita harus membuang prefix 'users/' khusus untuk auth
    
    final_path = path
    if service_key == "user":
        # Ubah "users/auth/login" -> "auth/login"
        if path.startswith("users/auth"):
            final_path = path.replace("users/", "", 1)
        # Ubah "users/profile/me" -> "users/profile/me" (Tetap, karena di backend route-nya memang users/profile/me)
        
    # Construct URL Akhir
    target_url = f"{SERVICES[service_key]}/{final_path}"
    
    return await forward_request(target_url, request)

@app.get("/")
def root():
    return {"message": "API Gateway is Running on Port 4000"}