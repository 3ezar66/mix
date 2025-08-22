#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Central Module - FastAPI/Flask Entrypoint
ماژول مرکزی API - نقطه ورود FastAPI/Flask
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import uvicorn
import logging
from typing import Dict, List, Optional
import asyncio

# Import our modules
from .main import router as main_router
from .routes import router as routes_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APICentral:
    """
    کلاس مرکزی API برای مدیریت تمام endpoint ها
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="SHBH-HBSHY National Mining Detection System",
            description="سیستم ملی تشخیص ماینینگ غیرمجاز",
            version="2.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        self._setup_middleware()
        self._setup_routes()
        self._setup_events()
    
    def _setup_middleware(self):
        """تنظیم middleware ها"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """تنظیم route ها"""
        self.app.include_router(main_router, prefix="/api/v1")
        self.app.include_router(routes_router, prefix="/api/v2")
    
    def _setup_events(self):
        """تنظیم event handlers"""
        @self.app.on_event("startup")
        async def startup_event():
            logger.info("🚀 SHBH-HBSHY API Server Starting...")
            logger.info("📡 National Mining Detection System Active")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            logger.info("🛑 SHBH-HBSHY API Server Shutting Down...")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """اجرای سرور API"""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            log_level="info"
        )

# Global API instance
api_central = APICentral()

def get_api_app() -> FastAPI:
    """دریافت instance سرور API"""
    return api_central.app

if __name__ == "__main__":
    api_central.run(debug=True)
