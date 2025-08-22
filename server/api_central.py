from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت داده اسکن RF
@app.post("/api/rf-scan")
async def receive_rf_scan(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("rf_scans_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS rf_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                freq_start REAL,
                freq_end REAL,
                powers TEXT,
                location TEXT,
                center_freq INTEGER,
                bandwidth INTEGER,
                duration INTEGER
            )
        """)
        for entry in data.get("scan_data", []):
            c.execute("""
                INSERT INTO rf_scans (timestamp, freq_start, freq_end, powers, location, center_freq, bandwidth, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["timestamp"], entry["freq_start"], entry["freq_end"],
                ",".join(map(str, entry["powers"])), entry["location"],
                data.get("center_freq"), data.get("bandwidth"), data.get("duration")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("scan_data", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
