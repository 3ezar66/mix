from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت داده GeoIP و مالکیت IP
@app.post("/api/geoip-owner")
async def receive_geoip_owner(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("geoip_owner_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS geoip_owner (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                owner_name TEXT,
                owner_family TEXT,
                phone TEXT,
                national_id TEXT,
                address TEXT,
                contract_type TEXT,
                isp TEXT,
                confidence REAL,
                source TEXT,
                timestamp TEXT,
                location TEXT
            )
        """)
        for entry in data.get("results", []):
            c.execute("""
                INSERT INTO geoip_owner (ip, country, region, city, latitude, longitude, owner_name, owner_family, phone, national_id, address, contract_type, isp, confidence, source, timestamp, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get("ip"), entry.get("country"), entry.get("region"), entry.get("city"),
                entry.get("latitude"), entry.get("longitude"), entry.get("owner_name"), entry.get("owner_family"),
                entry.get("phone"), entry.get("national_id"), entry.get("address"), entry.get("contract_type"),
                entry.get("isp"), entry.get("confidence"), entry.get("source"), entry.get("timestamp"), entry.get("location", "unknown")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("results", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
