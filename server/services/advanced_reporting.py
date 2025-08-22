 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Reporting System for National Comprehensive System
سیستم گزارش‌گیری پیشرفته برای سیستم جامع ملی
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import aiosqlite
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedReportingSystem:
    """
    سیستم گزارش‌گیری پیشرفته
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    async def get_database_connection(self):
        """Get database connection"""
        return await aiosqlite.connect(self.db_path)
    
    async def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """Generate daily report"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        async with await self.get_database_connection() as db:
            # Get daily statistics
            stats = await self._get_daily_statistics(db, date)
            
            # Generate charts
            charts = await self._generate_daily_charts(db, date)
            
            # Create report structure
            report = {
                "report_type": "daily",
                "date": date,
                "generated_at": datetime.now().isoformat(),
                "statistics": stats,
                "charts": charts,
                "summary": self._generate_summary(stats)
            }
            
            # Save report
            await self._save_report(report, f"daily_report_{date}.json")
            
            return report
    
    async def generate_weekly_report(self, week_start: str = None) -> Dict[str, Any]:
        """Generate weekly report"""
        if not week_start:
            week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
        async with await self.get_database_connection() as db:
            # Get weekly statistics
            stats = await self._get_weekly_statistics(db, week_start)
            
            # Generate charts
            charts = await self._generate_weekly_charts(db, week_start)
            
            # Create report structure
            report = {
                "report_type": "weekly",
                "week_start": week_start,
                "generated_at": datetime.now().isoformat(),
                "statistics": stats,
                "charts": charts,
                "summary": self._generate_summary(stats)
            }
            
            # Save report
            await self._save_report(report, f"weekly_report_{week_start}.json")
            
            return report
    
    async def generate_monthly_report(self, month: str = None) -> Dict[str, Any]:
        """Generate monthly report"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
            
        async with await self.get_database_connection() as db:
            # Get monthly statistics
            stats = await self._get_monthly_statistics(db, month)
            
            # Generate charts
            charts = await self._generate_monthly_charts(db, month)
            
            # Create report structure
            report = {
                "report_type": "monthly",
                "month": month,
                "generated_at": datetime.now().isoformat(),
                "statistics": stats,
                "charts": charts,
                "summary": self._generate_summary(stats)
            }
            
            # Save report
            await self._save_report(report, f"monthly_report_{month}.json")
            
            return report
    
    async def generate_geographic_report(self) -> Dict[str, Any]:
        """Generate geographic distribution report"""
        async with await self.get_database_connection() as db:
            # Get geographic data
            geo_data = await self._get_geographic_data(db)
            
            # Generate geographic charts
            charts = await self._generate_geographic_charts(geo_data)
            
            # Create report structure
            report = {
                "report_type": "geographic",
                "generated_at": datetime.now().isoformat(),
                "data": geo_data,
                "charts": charts,
                "summary": self._generate_geographic_summary(geo_data)
            }
            
            # Save report
            await self._save_report(report, f"geographic_report_{datetime.now().strftime('%Y%m%d')}.json")
            
            return report
    
    async def generate_energy_consumption_report(self, period: str = "monthly") -> Dict[str, Any]:
        """Generate energy consumption report"""
        async with await self.get_database_connection() as db:
            # Get energy consumption data
            energy_data = await self._get_energy_consumption_data(db, period)
            
            # Generate energy charts
            charts = await self._generate_energy_charts(energy_data)
            
            # Create report structure
            report = {
                "report_type": "energy_consumption",
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "data": energy_data,
                "charts": charts,
                "summary": self._generate_energy_summary(energy_data)
            }
            
            # Save report
            await self._save_report(report, f"energy_report_{period}_{datetime.now().strftime('%Y%m%d')}.json")
            
            return report
    
    async def export_to_excel(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """Export report to Excel format"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
        filepath = self.reports_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([report_data.get("summary", {})])
            summary_df.to_excel(writer, sheet_name='خلاصه', index=False)
            
            # Statistics sheet
            if "statistics" in report_data:
                stats_df = pd.DataFrame([report_data["statistics"]])
                stats_df.to_excel(writer, sheet_name='آمار', index=False)
            
            # Data sheet
            if "data" in report_data:
                data_df = pd.DataFrame(report_data["data"])
                data_df.to_excel(writer, sheet_name='داده‌ها', index=False)
        
        return str(filepath)
    
    async def _get_daily_statistics(self, db, date: str) -> Dict[str, Any]:
        """Get daily statistics from database"""
        query = """
        SELECT 
            COUNT(*) as total_detections,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_miners,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_miners,
            SUM(power_consumption) as total_power_consumption,
            AVG(confidence_score) as avg_confidence_score
        FROM detected_miners 
        WHERE DATE(created_at) = ?
        """
        
        async with db.execute(query, (date,)) as cursor:
            row = await cursor.fetchone()
            
        return {
            "total_detections": row[0] or 0,
            "active_miners": row[1] or 0,
            "confirmed_miners": row[2] or 0,
            "total_power_consumption": row[3] or 0,
            "avg_confidence_score": row[4] or 0
        }
    
    async def _get_weekly_statistics(self, db, week_start: str) -> Dict[str, Any]:
        """Get weekly statistics from database"""
        week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        
        query = """
        SELECT 
            COUNT(*) as total_detections,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_miners,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_miners,
            SUM(power_consumption) as total_power_consumption,
            AVG(confidence_score) as avg_confidence_score
        FROM detected_miners 
        WHERE DATE(created_at) BETWEEN ? AND ?
        """
        
        async with db.execute(query, (week_start, week_end)) as cursor:
            row = await cursor.fetchone()
            
        return {
            "total_detections": row[0] or 0,
            "active_miners": row[1] or 0,
            "confirmed_miners": row[2] or 0,
            "total_power_consumption": row[3] or 0,
            "avg_confidence_score": row[4] or 0
        }
    
    async def _get_monthly_statistics(self, db, month: str) -> Dict[str, Any]:
        """Get monthly statistics from database"""
        query = """
        SELECT 
            COUNT(*) as total_detections,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_miners,
            SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_miners,
            SUM(power_consumption) as total_power_consumption,
            AVG(confidence_score) as avg_confidence_score
        FROM detected_miners 
        WHERE strftime('%Y-%m', created_at) = ?
        """
        
        async with db.execute(query, (month,)) as cursor:
            row = await cursor.fetchone()
            
        return {
            "total_detections": row[0] or 0,
            "active_miners": row[1] or 0,
            "confirmed_miners": row[2] or 0,
            "total_power_consumption": row[3] or 0,
            "avg_confidence_score": row[4] or 0
        }
    
    async def _get_geographic_data(self, db) -> List[Dict[str, Any]]:
        """Get geographic distribution data"""
        query = """
        SELECT 
            city,
            region,
            COUNT(*) as detection_count,
            SUM(power_consumption) as total_power,
            AVG(confidence_score) as avg_confidence
        FROM detected_miners 
        GROUP BY city, region
        ORDER BY detection_count DESC
        """
        
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            
        return [
            {
                "city": row[0],
                "region": row[1],
                "detection_count": row[2],
                "total_power": row[3],
                "avg_confidence": row[4]
            }
            for row in rows
        ]
    
    async def _get_energy_consumption_data(self, db, period: str) -> List[Dict[str, Any]]:
        """Get energy consumption data"""
        if period == "daily":
            group_by = "DATE(created_at)"
        elif period == "weekly":
            group_by = "strftime('%Y-%W', created_at)"
        else:  # monthly
            group_by = "strftime('%Y-%m', created_at)"
            
        query = f"""
        SELECT 
            {group_by} as period,
            SUM(power_consumption) as total_consumption,
            COUNT(*) as device_count,
            AVG(power_consumption) as avg_consumption
        FROM detected_miners 
        GROUP BY {group_by}
        ORDER BY period DESC
        LIMIT 30
        """
        
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            
        return [
            {
                "period": row[0],
                "total_consumption": row[1],
                "device_count": row[2],
                "avg_consumption": row[3]
            }
            for row in rows
        ]
    
    async def _generate_daily_charts(self, db, date: str) -> Dict[str, str]:
        """Generate daily charts"""
        # Implementation for generating charts
        # This would create matplotlib charts and convert to base64
        return {"detection_trend": "base64_chart_data"}
    
    async def _generate_weekly_charts(self, db, week_start: str) -> Dict[str, str]:
        """Generate weekly charts"""
        return {"weekly_trend": "base64_chart_data"}
    
    async def _generate_monthly_charts(self, db, month: str) -> Dict[str, str]:
        """Generate monthly charts"""
        return {"monthly_trend": "base64_chart_data"}
    
    async def _generate_geographic_charts(self, geo_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate geographic charts"""
        return {"geographic_distribution": "base64_chart_data"}
    
    async def _generate_energy_charts(self, energy_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate energy consumption charts"""
        return {"energy_consumption_trend": "base64_chart_data"}
    
    def _generate_summary(self, stats: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary from statistics"""
        return {
            "total_detections": f"{stats.get('total_detections', 0)} تشخیص",
            "active_miners": f"{stats.get('active_miners', 0)} ماینر فعال",
            "power_consumption": f"{stats.get('total_power_consumption', 0):,.0f} وات",
            "confidence_score": f"{stats.get('avg_confidence_score', 0):.1f}%"
        }
    
    def _generate_geographic_summary(self, geo_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate geographic summary"""
        total_detections = sum(item["detection_count"] for item in geo_data)
        total_power = sum(item["total_power"] for item in geo_data)
        
        return {
            "total_cities": f"{len(geo_data)} شهر",
            "total_detections": f"{total_detections} تشخیص",
            "total_power_consumption": f"{total_power:,.0f} وات"
        }
    
    def _generate_energy_summary(self, energy_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate energy consumption summary"""
        total_consumption = sum(item["total_consumption"] for item in energy_data)
        total_devices = sum(item["device_count"] for item in energy_data)
        
        return {
            "total_consumption": f"{total_consumption:,.0f} وات",
            "total_devices": f"{total_devices} دستگاه",
            "avg_consumption": f"{total_consumption/total_devices if total_devices > 0 else 0:,.0f} وات"
        }
    
    async def _save_report(self, report: Dict[str, Any], filename: str):
        """Save report to file"""
        filepath = self.reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report saved: {filepath}")

# Global instance
reporting_system = AdvancedReportingSystem()

async def generate_report(report_type: str, **kwargs) -> Dict[str, Any]:
    """Generate report by type"""
    if report_type == "daily":
        return await reporting_system.generate_daily_report(**kwargs)
    elif report_type == "weekly":
        return await reporting_system.generate_weekly_report(**kwargs)
    elif report_type == "monthly":
        return await reporting_system.generate_monthly_report(**kwargs)
    elif report_type == "geographic":
        return await reporting_system.generate_geographic_report()
    elif report_type == "energy":
        return await reporting_system.generate_energy_consumption_report(**kwargs)
    else:
        raise ValueError(f"Unknown report type: {report_type}")

if __name__ == "__main__":
    # Test the reporting system
    async def test():
        # Generate daily report
        daily_report = await generate_report("daily")
        print("Daily report generated:", daily_report["summary"])
        
        # Generate geographic report
        geo_report = await generate_report("geographic")
        print("Geographic report generated:", geo_report["summary"])
        
        # Export to Excel
        excel_path = await reporting_system.export_to_excel(daily_report)
        print(f"Excel report exported: {excel_path}")
    
    asyncio.run(test())