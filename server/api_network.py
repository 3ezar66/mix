from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت داده اسکن شبکه
@app.post("/api/network-scan")
async def receive_network_scan(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("network_scans_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS network_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip TEXT,
                mac TEXT,
                open_ports TEXT,
                device_type TEXT,
                location TEXT
            )
        """)
        for entry in data.get("devices", []):
            c.execute("""
                INSERT INTO network_scans (timestamp, ip, mac, open_ports, device_type, location)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry.get("timestamp"), entry.get("ip"), entry.get("mac"),
                ",".join([str(p) for p in entry.get("open_ports", [])]),
                entry.get("device_type"), entry.get("location", "unknown")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("devices", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
