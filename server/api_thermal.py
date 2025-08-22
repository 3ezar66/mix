from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت داده سنسورهای حرارتی و محیطی
@app.post("/api/thermal-sensor")
async def receive_thermal_sensor(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("thermal_sensor_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS thermal_sensor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                temperature REAL,
                detected INTEGER,
                location TEXT,
                details TEXT
            )
        """)
        for entry in data.get("results", []):
            c.execute("""
                INSERT INTO thermal_sensor (timestamp, temperature, detected, location, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry.get("timestamp"), entry.get("temperature"), int(entry.get("detected", False)),
                entry.get("location", "unknown"), entry.get("details", "")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("results", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
