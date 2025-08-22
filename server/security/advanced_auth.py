#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Authentication and User Management System
سیستم پیشرفته احراز هویت و مدیریت کاربران
"""

import asyncio
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import aiosqlite
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

# Import database manager
from ..core.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secure-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v2/auth/token")

# Pydantic models
class UserBase(BaseModel):
    username: str
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase):
    id: int
    created_at: str
    last_login: Optional[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    role: str

class AdvancedAuthSystem:
    """
    سیستم پیشرفته احراز هویت و مدیریت کاربران
    """
    
    def __init__(self):
        self.db = get_database()
        # Create default admin user if not exists
        asyncio.run(self._initialize_default_user())
    
    async def _initialize_default_user(self):
        """Initialize default admin user if no users exist"""
        try:
            user_count = await self.db.fetch_val("SELECT COUNT(*) FROM users")
            if user_count == 0:
                hashed_password = self._hash_password("adminpassword")
                await self.db.create_user({
                    "username": "admin",
                    "password": hashed_password,
                    "role": "admin"
                })
                logger.info("Default admin user created")
        except Exception as e:
            logger.error(f"Error initializing default user: {e}")
    
    def _hash_password(self, password: str) -> bytes:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def _verify_password(self, plain_password: str, hashed_password: bytes) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with credentials"""
        user_data = await self.db.get_user_by_username(username)
        if not user_data:
            return None
        
        if not self._verify_password(password, user_data['password'].encode('utf-8')):
            return None
        
        # Update last login
        await self.db.update_user_last_login(user_data['id'], datetime.utcnow().isoformat())
        
        return User(
            id=user_data['id'],
            username=user_data['username'],
            role=user_data['role'],
            created_at=user_data['created_at'],
            last_login=user_data['last_login']
        )
    
    def create_access_token(self, data: dict) -> str:
        """Create access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            token_type: str = payload.get("type")
            
            if username is None or token_type != "access":
                return None
            
            return TokenData(username=username, role=role)
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[TokenData]:
        """Verify refresh token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            token_type: str = payload.get("type")
            
            if username is None or token_type != "refresh":
                return None
            
            return TokenData(username=username, role=role)
        except Exception as e:
            logger.warning(f"Refresh token verification failed: {e}")
            return None
    
    async def create_user(self, user: UserCreate) -> User:
        """Create new user"""
        hashed_password = self._hash_password(user.password)
        user_id = await self.db.create_user({
            "username": user.username,
            "password": hashed_password.decode('utf-8'),
            "role": user.role
        })
        return User(id=user_id, username=user.username, role=user.role, created_at=datetime.utcnow().isoformat(), last_login=None)
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        updates = {}
        if user_update.username:
            updates['username'] = user_update.username
        if user_update.password:
            updates['password'] = self._hash_password(user_update.password).decode('utf-8')
        if user_update.role:
            updates['role'] = user_update.role
        
        if updates:
            success = await self.db.update_user(user_id, updates)
            if success:
                user_data = await self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
                if user_data:
                    return User(
                        id=user_data['id'],
                        username=user_data['username'],
                        role=user_data['role'],
                        created_at=user_data['created_at'],
                        last_login=user_data['last_login']
                    )
        return None
    
    async def get_users(self) -> List[User]:
        """Get all users"""
        users_data = await self.db.fetch_all("SELECT * FROM users")
        return [User(
            id=user['id'],
            username=user['username'],
            role=user['role'],
            created_at=user['created_at'],
            last_login=user['last_login']
        ) for user in users_data]
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user_data = await self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                role=user_data['role'],
                created_at=user_data['created_at'],
                last_login=user_data['last_login']
            )
        return None

# Global instance
auth_system = AdvancedAuthSystem()

def get_auth_system() -> AdvancedAuthSystem:
    """Get auth system instance"""
    return auth_system

# FastAPI routes for authentication
from fastapi import FastAPI, Response

app = FastAPI()

@app.post("/api/v2/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_system.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_system.create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = auth_system.create_refresh_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/api/v2/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    token_data = auth_system.verify_refresh_token(refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_system.create_access_token(data={"sub": token_data.username, "role": token_data.role})
    new_refresh_token = auth_system.create_refresh_token(data={"sub": token_data.username, "role": token_data.role})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@app.post("/api/v2/users", response_model=User)
async def create_user(user: UserCreate, current_user: TokenData = Depends(oauth2_scheme)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create users")
    return await auth_system.create_user(user)

@app.get("/api/v2/users", response_model=List[User])
async def read_users(current_user: TokenData = Depends(oauth2_scheme)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view users")
    return await auth_system.get_users()

@app.get("/api/v2/users/{user_id}", response_model=User)
async def read_user(user_id: int, current_user: TokenData = Depends(oauth2_scheme)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view user")
    user = await auth_system.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/v2/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate, current_user: TokenData = Depends(oauth2_scheme)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update user")
    updated_user = await auth_system.update_user(user_id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user 