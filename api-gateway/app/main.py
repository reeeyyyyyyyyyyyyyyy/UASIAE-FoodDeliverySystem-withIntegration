import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Food Delivery API Gateway")

# Konfigurasi CORS (Agar frontend bisa akses)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Di production sebaiknya spesifik, tp untuk dev "*" aman
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ambil URL Service dari .env
SERVICES = {
    "user": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "restaurant": os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8002"),
    "order": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
    "payment": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004"),
    "driver": os.getenv("DRIVER_SERVICE_URL", "http://localhost:8005"),
}

# Fungsi Helper untuk Proxy Request
async def forward_request(service_url: str, path: str, request: Request):
    # Buat client HTTP async
    async with httpx.AsyncClient() as client:
        # Tentukan target URL
        url = f"{service_url}/{path}"
        
        # Ambil query params (misal ?id=1)
        params = dict(request.query_params)
        
        # Ambil body (jika ada)
        body = await request.body()

        # Teruskan request ke microservice tujuan
        try:
            rp_req = client.build_request(
                request.method,
                url,
                headers=request.headers.raw, # Forward header (termasuk Auth/Token)
                params=params,
                content=body,
                timeout=30.0 # Timeout biar ga hang
            )
            rp_resp = await client.send(rp_req)
            
            # Kembalikan respon dari microservice ke client asli
            return Response(
                content=rp_resp.content,
                status_code=rp_resp.status_code,
                headers=dict(rp_resp.headers)
            )
        except httpx.RequestError as exc:
            return Response(
                content=f"Error connecting to service: {exc}".encode(),
                status_code=503
            )

# --- ROUTING RULES (Sama seperti Logic Lama + GraphQL) ---

# 1. USER SERVICE ROUTES
# Menangani endpoint REST lama (/auth, /users) dan GraphQL baru (/graphql/user)
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_auth_proxy(path: str, request: Request):
    return await forward_request(SERVICES["user"], f"auth/{path}", request)

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_proxy(path: str, request: Request):
    return await forward_request(SERVICES["user"], f"users/{path}", request)

@app.api_route("/graphql/user", methods=["GET", "POST"])
async def user_graphql_proxy(request: Request):
    # Forward ke endpoint /graphql di user-service
    return await forward_request(SERVICES["user"], "graphql", request)


# 2. RESTAURANT SERVICE ROUTES
# Menangani /restaurants, /menus
@app.api_route("/restaurants/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def restaurant_proxy(path: str, request: Request):
    return await forward_request(SERVICES["restaurant"], f"restaurants/{path}", request)

@app.api_route("/menus/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def menu_proxy(path: str, request: Request):
    return await forward_request(SERVICES["restaurant"], f"menus/{path}", request)

@app.api_route("/graphql/restaurant", methods=["GET", "POST"])
async def restaurant_graphql_proxy(request: Request):
    return await forward_request(SERVICES["restaurant"], "graphql", request)


# 3. ORDER SERVICE ROUTES
# Menangani /orders
@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def order_proxy(path: str, request: Request):
    return await forward_request(SERVICES["order"], f"orders/{path}", request)

@app.api_route("/graphql/order", methods=["GET", "POST"])
async def order_graphql_proxy(request: Request):
    return await forward_request(SERVICES["order"], "graphql", request)


# 4. PAYMENT SERVICE ROUTES
# Menangani /payments
@app.api_route("/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def payment_proxy(path: str, request: Request):
    return await forward_request(SERVICES["payment"], f"payments/{path}", request)

@app.api_route("/graphql/payment", methods=["GET", "POST"])
async def payment_graphql_proxy(request: Request):
    return await forward_request(SERVICES["payment"], "graphql", request)


# 5. DRIVER SERVICE ROUTES
# Menangani /drivers
@app.api_route("/drivers/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def driver_proxy(path: str, request: Request):
    return await forward_request(SERVICES["driver"], f"drivers/{path}", request)

@app.api_route("/graphql/driver", methods=["GET", "POST"])
async def driver_graphql_proxy(request: Request):
    return await forward_request(SERVICES["driver"], "graphql", request)


# Root check
@app.get("/")
async def root():
    return {"message": "API Gateway Food Delivery is Running with GraphQL Support"}