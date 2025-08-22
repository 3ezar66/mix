 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Alert and Notification System
سیستم هشدار و اعلان پیشرفته
"""

import asyncio
import json
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosqlite
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Alert types"""
    NEW_DETECTION = "new_detection"
    HIGH_CONSUMPTION = "high_consumption"
    SYSTEM_ERROR = "system_error"
    SECURITY_BREACH = "security_breach"
    NETWORK_ANOMALY = "network_anomaly"
    RF_SIGNAL_DETECTED = "rf_signal_detected"
    ACOUSTIC_ANOMALY = "acoustic_anomaly"
    THERMAL_ANOMALY = "thermal_anomaly"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    level: AlertLevel
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"
    DASHBOARD = "dashboard"

class AdvancedAlertSystem:
    """
    سیستم هشدار و اعلان پیشرفته
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.alert_rules = self._load_alert_rules()
        self.notification_config = self._load_notification_config()
        self.active_alerts: Dict[str, Alert] = {}
        
    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules from configuration"""
        return {
            "new_detection": {
                "enabled": True,
                "level": AlertLevel.WARNING,
                "threshold": 1,
                "cooldown": 300  # 5 minutes
            },
            "high_consumption": {
                "enabled": True,
                "level": AlertLevel.CRITICAL,
                "threshold": 5000,  # watts
                "cooldown": 600  # 10 minutes
            },
            "system_error": {
                "enabled": True,
                "level": AlertLevel.EMERGENCY,
                "threshold": 1,
                "cooldown": 60  # 1 minute
            },
            "security_breach": {
                "enabled": True,
                "level": AlertLevel.EMERGENCY,
                "threshold": 1,
                "cooldown": 30  # 30 seconds
            },
            "network_anomaly": {
                "enabled": True,
                "level": AlertLevel.WARNING,
                "threshold": 1,
                "cooldown": 300
            },
            "rf_signal_detected": {
                "enabled": True,
                "level": AlertLevel.WARNING,
                "threshold": 1,
                "cooldown": 180
            },
            "acoustic_anomaly": {
                "enabled": True,
                "level": AlertLevel.WARNING,
                "threshold": 1,
                "cooldown": 180
            },
            "thermal_anomaly": {
                "enabled": True,
                "level": AlertLevel.WARNING,
                "threshold": 1,
                "cooldown": 180
            }
        }
    
    def _load_notification_config(self) -> Dict[str, Any]:
        """Load notification configuration"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@ilam-electric.ir",
                "password": "your-email-password",
                "recipients": [
                    "admin@ilam-electric.ir",
                    "security@ilam-electric.ir",
                    "operations@ilam-electric.ir"
                ]
            },
            "sms": {
                "enabled": True,
                "api_url": "https://api.sms.ir/v1/send",
                "api_key": "your-sms-api-key",
                "recipients": [
                    "+989123456789",
                    "+989123456790"
                ]
            },
            "telegram": {
                "enabled": True,
                "bot_token": "your-telegram-bot-token",
                "chat_ids": [
                    "-1001234567890",
                    "-1001234567891"
                ]
            },
            "webhook": {
                "enabled": True,
                "urls": [
                    "https://api.ilam-electric.ir/webhooks/alerts",
                    "https://emergency.ilam-electric.ir/api/alerts"
                ]
            }
        }
    
    async def get_database_connection(self):
        """Get database connection"""
        return await aiosqlite.connect(self.db_path)
    
    async def create_alert(self, alert_type: AlertType, title: str, message: str, 
                          data: Dict[str, Any], level: Optional[AlertLevel] = None) -> Alert:
        """Create a new alert"""
        # Check if alert rule is enabled
        rule = self.alert_rules.get(alert_type.value)
        if not rule or not rule["enabled"]:
            return None
        
        # Use rule level if not specified
        if not level:
            level = rule["level"]
        
        # Check cooldown
        if await self._is_in_cooldown(alert_type, data):
            logger.info(f"Alert {alert_type.value} is in cooldown, skipping")
            return None
        
        # Create alert
        alert_id = f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        alert = Alert(
            id=alert_id,
            type=alert_type,
            level=level,
            title=title,
            message=message,
            data=data,
            timestamp=datetime.now()
        )
        
        # Store alert
        await self._store_alert(alert)
        self.active_alerts[alert_id] = alert
        
        # Send notifications
        await self._send_notifications(alert)
        
        logger.info(f"Alert created: {alert_id} - {title}")
        return alert
    
    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_by = user
        alert.acknowledged_at = datetime.now()
        
        # Update database
        await self._update_alert_acknowledgment(alert)
        
        logger.info(f"Alert {alert_id} acknowledged by {user}")
        return True
    
    async def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active alerts"""
        alerts = list(self.active_alerts.values())
        
        if level:
            alerts = [alert for alert in alerts if alert.level == level]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    async def get_alert_history(self, days: int = 7, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get alert history"""
        async with await self.get_database_connection() as db:
            query = """
            SELECT * FROM system_alerts 
            WHERE timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
            """.format(days)
            
            if level:
                query = query.replace("WHERE", f"WHERE level = '{level.value}' AND")
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            alerts = []
            for row in rows:
                alert = Alert(
                    id=row[0],
                    type=AlertType(row[1]),
                    level=AlertLevel(row[2]),
                    title=row[3],
                    message=row[4],
                    data=json.loads(row[5]),
                    timestamp=datetime.fromisoformat(row[6]),
                    acknowledged=bool(row[7]),
                    acknowledged_by=row[8],
                    acknowledged_at=datetime.fromisoformat(row[9]) if row[9] else None
                )
                alerts.append(alert)
            
            return alerts
    
    async def _is_in_cooldown(self, alert_type: AlertType, data: Dict[str, Any]) -> bool:
        """Check if alert is in cooldown period"""
        rule = self.alert_rules.get(alert_type.value)
        if not rule:
            return False
        
        cooldown_seconds = rule["cooldown"]
        cutoff_time = datetime.now() - timedelta(seconds=cooldown_seconds)
        
        # Check recent alerts of same type
        async with await self.get_database_connection() as db:
            query = """
            SELECT COUNT(*) FROM system_alerts 
            WHERE type = ? AND timestamp > ?
            """
            
            async with db.execute(query, (alert_type.value, cutoff_time.isoformat())) as cursor:
                count = await cursor.fetchone()
                
            return count[0] > 0
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database"""
        async with await self.get_database_connection() as db:
            query = """
            INSERT INTO system_alerts 
            (id, type, level, title, message, data, timestamp, acknowledged, acknowledged_by, acknowledged_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            await db.execute(query, (
                alert.id,
                alert.type.value,
                alert.level.value,
                alert.title,
                alert.message,
                json.dumps(alert.data),
                alert.timestamp.isoformat(),
                alert.acknowledged,
                alert.acknowledged_by,
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
            ))
            
            await db.commit()
    
    async def _update_alert_acknowledgment(self, alert: Alert):
        """Update alert acknowledgment in database"""
        async with await self.get_database_connection() as db:
            query = """
            UPDATE system_alerts 
            SET acknowledged = ?, acknowledged_by = ?, acknowledged_at = ?
            WHERE id = ?
            """
            
            await db.execute(query, (
                alert.acknowledged,
                alert.acknowledged_by,
                alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                alert.id
            ))
            
            await db.commit()
    
    async def _send_notifications(self, alert: Alert):
        """Send notifications through all enabled channels"""
        tasks = []
        
        # Email notifications
        if self.notification_config["email"]["enabled"]:
            tasks.append(self._send_email_notification(alert))
        
        # SMS notifications
        if self.notification_config["sms"]["enabled"]:
            tasks.append(self._send_sms_notification(alert))
        
        # Telegram notifications
        if self.notification_config["telegram"]["enabled"]:
            tasks.append(self._send_telegram_notification(alert))
        
        # Webhook notifications
        if self.notification_config["webhook"]["enabled"]:
            tasks.append(self._send_webhook_notification(alert))
        
        # Execute all notifications concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        try:
            config = self.notification_config["email"]
            
            msg = MIMEMultipart()
            msg['From'] = config["username"]
            msg['To'] = ", ".join(config["recipients"])
            msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
            
            body = f"""
            هشدار سیستم جامع ملی
            
            نوع: {alert.type.value}
            سطح: {alert.level.value}
            عنوان: {alert.title}
            پیام: {alert.message}
            زمان: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            
            جزئیات:
            {json.dumps(alert.data, ensure_ascii=False, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
                server.starttls()
                server.login(config["username"], config["password"])
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_sms_notification(self, alert: Alert):
        """Send SMS notification"""
        try:
            config = self.notification_config["sms"]
            
            message = f"هشدار: {alert.title} - {alert.message}"
            
            for recipient in config["recipients"]:
                payload = {
                    "apiKey": config["api_key"],
                    "mobile": recipient,
                    "message": message
                }
                
                response = requests.post(config["api_url"], json=payload)
                if response.status_code == 200:
                    logger.info(f"SMS notification sent to {recipient}")
                else:
                    logger.error(f"Failed to send SMS to {recipient}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
    
    async def _send_telegram_notification(self, alert: Alert):
        """Send Telegram notification"""
        try:
            config = self.notification_config["telegram"]
            
            message = f"""
🚨 *هشدار سیستم جامع ملی*

*نوع:* {alert.type.value}
*سطح:* {alert.level.value}
*عنوان:* {alert.title}
*پیام:* {alert.message}
*زمان:* {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

*جزئیات:*
```json
{json.dumps(alert.data, ensure_ascii=False, indent=2)}
```
            """
            
            for chat_id in config["chat_ids"]:
                url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    logger.info(f"Telegram notification sent to {chat_id}")
                else:
                    logger.error(f"Failed to send Telegram to {chat_id}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        try:
            config = self.notification_config["webhook"]
            
            payload = {
                "alert_id": alert.id,
                "type": alert.type.value,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "data": alert.data,
                "timestamp": alert.timestamp.isoformat(),
                "source": "ilam_mining_system"
            }
            
            for url in config["urls"]:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code in [200, 201]:
                    logger.info(f"Webhook notification sent to {url}")
                else:
                    logger.error(f"Failed to send webhook to {url}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def cleanup_old_alerts(self, days: int = 30):
        """Clean up old alerts from database"""
        async with await self.get_database_connection() as db:
            query = """
            DELETE FROM system_alerts 
            WHERE timestamp < datetime('now', '-{} days')
            """.format(days)
            
            await db.execute(query)
            await db.commit()
            
            logger.info(f"Cleaned up alerts older than {days} days")

# Global instance
alert_system = AdvancedAlertSystem()

# Convenience functions
async def create_alert(alert_type: AlertType, title: str, message: str, 
                      data: Dict[str, Any], level: Optional[AlertLevel] = None) -> Alert:
    """Create a new alert"""
    return await alert_system.create_alert(alert_type, title, message, data, level)

async def get_active_alerts(level: Optional[AlertLevel] = None) -> List[Alert]:
    """Get active alerts"""
    return await alert_system.get_active_alerts(level)

async def acknowledge_alert(alert_id: str, user: str) -> bool:
    """Acknowledge an alert"""
    return await alert_system.acknowledge_alert(alert_id, user)

if __name__ == "__main__":
    # Test the alert system
    async def test():
        # Create test alert
        alert = await create_alert(
            AlertType.NEW_DETECTION,
            "تشخیص ماینر جدید",
            "یک دستگاه ماینر جدید در شبکه شناسایی شد",
            {
                "ip_address": "192.168.1.100",
                "mac_address": "00:11:22:33:44:55",
                "location": "ایلام، خیابان امام",
                "power_consumption": 2500
            },
            AlertLevel.WARNING
        )
        
        print(f"Alert created: {alert.id}")
        
        # Get active alerts
        active_alerts = await get_active_alerts()
        print(f"Active alerts: {len(active_alerts)}")
        
        # Acknowledge alert
        if alert:
            success = await acknowledge_alert(alert.id, "admin")
            print(f"Alert acknowledged: {success}")
    
    asyncio.run(test())