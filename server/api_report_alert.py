from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت و ثبت گزارش‌ها و هشدارهای سیستم
@app.post("/api/report-alert")
async def receive_report_alert(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("report_alert_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS report_alert (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                report_type TEXT,
                message TEXT,
                severity TEXT,
                related_id TEXT,
                location TEXT,
                details TEXT
            )
        """)
        for entry in data.get("results", []):
            c.execute("""
                INSERT INTO report_alert (timestamp, report_type, message, severity, related_id, location, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get("timestamp"), entry.get("report_type", ""), entry.get("message", ""), entry.get("severity", "info"),
                entry.get("related_id", ""), entry.get("location", "unknown"), entry.get("details", "")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("results", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
