from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Endpoint برای دریافت داده‌های هوش مصنوعی و تحلیل پیشرفته شبکه/دستگاه‌ها
@app.post("/api/ai-analysis")
async def receive_ai_analysis(request: Request):
    data = await request.json()
    try:
        conn = sqlite3.connect("ai_analysis_central.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                analysis_type TEXT,
                input_data TEXT,
                result TEXT,
                confidence REAL,
                alert INTEGER,
                location TEXT,
                details TEXT
            )
        """)
        for entry in data.get("results", []):
            c.execute("""
                INSERT INTO ai_analysis (timestamp, analysis_type, input_data, result, confidence, alert, location, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get("timestamp"), entry.get("analysis_type"), entry.get("input_data", ""), entry.get("result", ""),
                entry.get("confidence", 0.0), int(entry.get("alert", False)), entry.get("location", "unknown"), entry.get("details", "")
            ))
        conn.commit()
        conn.close()
        return {"status": "success", "count": len(data.get("results", []))}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# اجرای سرور (در حالت توسعه)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
