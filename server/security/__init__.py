#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Module - Advanced Security and Authentication System
ماژول امنیت - سیستم پیشرفته امنیت و احراز هویت
"""

import hashlib
import hmac
import secrets
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import aiosqlite
import json
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """مدل کاربر"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    permissions: List[str]

@dataclass
class SecurityEvent:
    """رویداد امنیتی"""
    id: str
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    ip_address: str
    details: Dict[str, Any]
    severity: str

class SecurityManager:
    """
    مدیر امنیت برای سیستم تشخیص ماینینگ
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.secret_key = "your-super-secret-key-change-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # OAuth2 scheme
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v2/auth/token")
        
        # Security policies
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        self.password_min_length = 8
        self.require_special_chars = True
        self.require_numbers = True
        self.require_uppercase = True
        
        # Rate limiting
        self.rate_limit_requests = 100
        self.rate_limit_window_minutes = 15
        
        # Initialize security tables
        self._initialize_security_tables()
    
    async def _initialize_security_tables(self):
        """راه‌اندازی جداول امنیتی"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Users table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'user',
                        is_active BOOLEAN NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL,
                        last_login TEXT,
                        permissions TEXT,
                        failed_login_attempts INTEGER DEFAULT 0,
                        locked_until TEXT
                    )
                """)
                
                # Security events table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        user_id TEXT,
                        ip_address TEXT NOT NULL,
                        details TEXT,
                        severity TEXT NOT NULL
                    )
                """)
                
                # API keys table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        key_hash TEXT NOT NULL,
                        name TEXT NOT NULL,
                        permissions TEXT,
                        created_at TEXT NOT NULL,
                        expires_at TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Rate limiting table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limits (
                        ip_address TEXT PRIMARY KEY,
                        request_count INTEGER DEFAULT 0,
                        window_start TEXT NOT NULL,
                        last_request TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                
                # Create default admin user if not exists
                await self._create_default_admin()
                
                logger.info("✅ Security tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize security tables: {e}")
            raise
    
    async def _create_default_admin(self):
        """ایجاد کاربر ادمین پیش‌فرض"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if admin user exists
                async with db.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'") as cursor:
                    admin_exists = (await cursor.fetchone())[0] > 0
                
                if not admin_exists:
                    # Create admin user
                    password_hash = self._hash_password("admin123")
                    await db.execute("""
                        INSERT INTO users (username, email, password_hash, role, created_at, permissions)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        "admin",
                        "admin@shbh-hbshy.ir",
                        password_hash,
                        "admin",
                        datetime.now().isoformat(),
                        json.dumps(["all"])
                    ))
                    await db.commit()
                    logger.info("👑 Default admin user created")
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")
    
    def _hash_password(self, password: str) -> str:
        """هش کردن رمز عبور"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """تأیید رمز عبور"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _generate_token(self, data: dict, expires_delta: timedelta) -> str:
        """تولید توکن JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """تأیید توکن JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    async def authenticate_user(self, username: str, password: str, ip_address: str) -> Optional[User]:
        """احراز هویت کاربر"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if user is locked
                async with db.execute("""
                    SELECT locked_until FROM users WHERE username = ?
                """, (username,)) as cursor:
                    locked_until_row = await cursor.fetchone()
                    if locked_until_row and locked_until_row[0]:
                        locked_until = datetime.fromisoformat(locked_until_row[0])
                        if datetime.now() < locked_until:
                            await self._log_security_event(
                                "login_attempt_locked",
                                None,
                                ip_address,
                                {"username": username, "locked_until": locked_until.isoformat()},
                                "medium"
                            )
                            return None
                
                # Get user data
                async with db.execute("""
                    SELECT id, username, email, password_hash, role, is_active, 
                           created_at, last_login, permissions, failed_login_attempts
                    FROM users WHERE username = ?
                """, (username,)) as cursor:
                    user_row = await cursor.fetchone()
                
                if not user_row:
                    await self._log_security_event(
                        "login_attempt_invalid_user",
                        None,
                        ip_address,
                        {"username": username},
                        "low"
                    )
                    return None
                
                user_id, username, email, password_hash, role, is_active, created_at, last_login, permissions, failed_attempts = user_row
                
                if not is_active:
                    await self._log_security_event(
                        "login_attempt_inactive_user",
                        str(user_id),
                        ip_address,
                        {"username": username},
                        "medium"
                    )
                    return None
                
                # Verify password
                if not self._verify_password(password, password_hash):
                    # Increment failed attempts
                    new_failed_attempts = failed_attempts + 1
                    await db.execute("""
                        UPDATE users SET failed_login_attempts = ? WHERE id = ?
                    """, (new_failed_attempts, user_id))
                    
                    # Lock account if too many failed attempts
                    if new_failed_attempts >= self.max_login_attempts:
                        locked_until = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)
                        await db.execute("""
                            UPDATE users SET locked_until = ? WHERE id = ?
                        """, (locked_until.isoformat(), user_id))
                        
                        await self._log_security_event(
                            "account_locked",
                            str(user_id),
                            ip_address,
                            {"username": username, "failed_attempts": new_failed_attempts},
                            "high"
                        )
                    
                    await db.commit()
                    
                    await self._log_security_event(
                        "login_attempt_failed",
                        str(user_id),
                        ip_address,
                        {"username": username, "failed_attempts": new_failed_attempts},
                        "medium"
                    )
                    return None
                
                # Reset failed attempts on successful login
                await db.execute("""
                    UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), user_id))
                await db.commit()
                
                # Log successful login
                await self._log_security_event(
                    "login_successful",
                    str(user_id),
                    ip_address,
                    {"username": username},
                    "low"
                )
                
                return User(
                    id=user_id,
                    username=username,
                    email=email,
                    role=role,
                    is_active=bool(is_active),
                    created_at=datetime.fromisoformat(created_at),
                    last_login=datetime.fromisoformat(last_login) if last_login else None,
                    permissions=json.loads(permissions) if permissions else []
                )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def create_access_token(self, user: User) -> str:
        """ایجاد توکن دسترسی"""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "permissions": user.permissions
        }
        return self._generate_token(data, expires_delta)
    
    async def create_refresh_token(self, user: User) -> str:
        """ایجاد توکن تمدید"""
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        data = {
            "sub": str(user.id),
            "username": user.username,
            "type": "refresh"
        }
        return self._generate_token(data, expires_delta)
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """دریافت کاربر فعلی از توکن"""
        payload = self._verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, username, email, role, is_active, created_at, last_login, permissions
                    FROM users WHERE id = ? AND is_active = 1
                """, (user_id,)) as cursor:
                    user_row = await cursor.fetchone()
                
                if not user_row:
                    return None
                
                user_id, username, email, role, is_active, created_at, last_login, permissions = user_row
                
                return User(
                    id=user_id,
                    username=username,
                    email=email,
                    role=role,
                    is_active=bool(is_active),
                    created_at=datetime.fromisoformat(created_at),
                    last_login=datetime.fromisoformat(last_login) if last_login else None,
                    permissions=json.loads(permissions) if permissions else []
                )
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """بررسی مجوز کاربر"""
        if "all" in user.permissions:
            return True
        return permission in user.permissions
    
    async def _log_security_event(self, event_type: str, user_id: Optional[str], 
                                 ip_address: str, details: Dict[str, Any], severity: str):
        """ثبت رویداد امنیتی"""
        try:
            event_id = secrets.token_hex(16)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO security_events (id, timestamp, event_type, user_id, ip_address, details, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    datetime.now().isoformat(),
                    event_type,
                    user_id,
                    ip_address,
                    json.dumps(details),
                    severity
                ))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def check_rate_limit(self, ip_address: str) -> bool:
        """بررسی محدودیت نرخ درخواست"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get current rate limit data
                async with db.execute("""
                    SELECT request_count, window_start FROM rate_limits WHERE ip_address = ?
                """, (ip_address,)) as cursor:
                    rate_limit_row = await cursor.fetchone()
                
                now = datetime.now()
                window_start = now - timedelta(minutes=self.rate_limit_window_minutes)
                
                if not rate_limit_row:
                    # First request from this IP
                    await db.execute("""
                        INSERT INTO rate_limits (ip_address, request_count, window_start, last_request)
                        VALUES (?, 1, ?, ?)
                    """, (ip_address, window_start.isoformat(), now.isoformat()))
                    await db.commit()
                    return True
                
                current_count, stored_window_start = rate_limit_row
                stored_window = datetime.fromisoformat(stored_window_start)
                
                if now < stored_window:
                    # Still in current window
                    if current_count >= self.rate_limit_requests:
                        return False
                    
                    # Increment count
                    await db.execute("""
                        UPDATE rate_limits SET request_count = ?, last_request = ?
                        WHERE ip_address = ?
                    """, (current_count + 1, now.isoformat(), ip_address))
                    await db.commit()
                    return True
                else:
                    # New window
                    await db.execute("""
                        UPDATE rate_limits SET request_count = 1, window_start = ?, last_request = ?
                        WHERE ip_address = ?
                    """, (window_start.isoformat(), now.isoformat(), ip_address))
                    await db.commit()
                    return True
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow request on error
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """اعتبارسنجی قدرت رمز عبور"""
        errors = []
        warnings = []
        
        if len(password) < self.password_min_length:
            errors.append(f"Password must be at least {self.password_min_length} characters long")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.require_special_chars and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        if len(password) < 12:
            warnings.append("Consider using a longer password for better security")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "strength_score": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """محاسبه امتیاز قدرت رمز عبور"""
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        return min(score, 7)  # Max score of 7

# Global security manager instance
security_manager = SecurityManager()

def get_security_manager() -> SecurityManager:
    """دریافت instance مدیر امنیت"""
    return security_manager

async def initialize_security():
    """راه‌اندازی سیستم امنیت"""
    await security_manager._initialize_security_tables()
    logger.info("🔒 Security system initialized successfully")
