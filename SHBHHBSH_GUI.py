#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHBHHBSH GUI - Advanced Graphical User Interface for Mining Device Detection System
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import numpy as np
import threading
import queue
import time
from datetime import datetime
import json
import folium
import webbrowser
import os
from SHBHHBSH_MAIN import MiningDeviceDetector
from typing import Dict, Any

class ModernMiningDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 SHBHHBSH - سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize detector
        self.detector = MiningDeviceDetector()
        self.scan_queue = queue.Queue()
        self.is_scanning = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_gui, daemon=True)
        self.update_thread.start()
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='white', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Header.TLabel', 
                       background='#34495e', 
                       foreground='white', 
                       font=('Arial', 12, 'bold'))
        
        style.configure('Scan.TButton', 
                       background='#3498db', 
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Stop.TButton', 
                       background='#e74c3c', 
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Success.TLabel', 
                       background='#27ae60', 
                       foreground='white',
                       font=('Arial', 10))
        
        style.configure('Warning.TLabel', 
                       background='#f39c12', 
                       foreground='white',
                       font=('Arial', 10))
        
        style.configure('Danger.TLabel', 
                       background='#e74c3c', 
                       foreground='white',
                       font=('Arial', 10))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main title
        self.title_label = tk.Label(
            self.root,
            text="🔍 SHBHHBSH - سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='white',
            pady=20
        )
        
        # Control panel
        self.create_control_panel()
        
        # Scan options
        self.create_scan_options()
        
        # Results display
        self.create_results_display()
        
        # Real-time monitoring
        self.create_monitoring_panel()
        
        # Map integration
        self.create_map_panel()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#34495e',
            fg='white'
        )
        
    def create_control_panel(self):
        """Create main control panel"""
        self.control_frame = tk.LabelFrame(
            self.root,
            text="🎛️ Control Panel",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=10
        )
        
        # Location input
        tk.Label(self.control_frame, text="📍 Location:", bg='#2c3e50', fg='white').grid(row=0, column=0, sticky='w', pady=5)
        
        self.lat_var = tk.StringVar(value="35.6892")
        self.lon_var = tk.StringVar(value="51.3890")
        
        tk.Label(self.control_frame, text="Latitude:", bg='#2c3e50', fg='white').grid(row=1, column=0, sticky='w')
        tk.Entry(self.control_frame, textvariable=self.lat_var, width=15).grid(row=1, column=1, padx=5)
        
        tk.Label(self.control_frame, text="Longitude:", bg='#2c3e50', fg='white').grid(row=2, column=0, sticky='w')
        tk.Entry(self.control_frame, textvariable=self.lon_var, width=15).grid(row=2, column=1, padx=5)
        
        # Scan control buttons
        self.scan_button = tk.Button(
            self.control_frame,
            text="🚀 Start Comprehensive Scan",
            command=self.start_comprehensive_scan,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            pady=10,
            padx=20
        )
        self.scan_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.stop_button = tk.Button(
            self.control_frame,
            text="⏹️ Stop Scan",
            command=self.stop_scan,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold'),
            pady=10,
            padx=20,
            state='disabled'
        )
        self.stop_button.grid(row=4, column=0, columnspan=2, pady=5)
        
    def create_scan_options(self):
        """Create scan type selection"""
        self.options_frame = tk.LabelFrame(
            self.root,
            text="⚙️ Scan Options",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=10
        )
        
        # Scan types
        self.scan_vars = {
            'acoustic': tk.BooleanVar(value=True),
            'rf': tk.BooleanVar(value=True),
            'thermal': tk.BooleanVar(value=True),
            'power': tk.BooleanVar(value=True),
            'network': tk.BooleanVar(value=True)
        }
        
        row = 0
        for scan_type, var in self.scan_vars.items():
            tk.Checkbutton(
                self.options_frame,
                text=f"🔊 {scan_type.title()} Scan",
                variable=var,
                bg='#2c3e50',
                fg='white',
                selectcolor='#34495e',
                activebackground='#2c3e50',
                activeforeground='white'
            ).grid(row=row, column=0, sticky='w', pady=2)
            row += 1
        
        # Network scan options
        self.network_frame = tk.Frame(self.options_frame, bg='#2c3e50')
        self.network_frame.grid(row=0, column=1, rowspan=5, padx=20)
        
        tk.Label(self.network_frame, text="🌐 Network Options:", bg='#2c3e50', fg='white').grid(row=0, column=0, sticky='w', pady=5)
        
        self.ip_range_var = tk.StringVar(value="192.168.1.0/24")
        tk.Label(self.network_frame, text="IP Range:", bg='#2c3e50', fg='white').grid(row=1, column=0, sticky='w')
        tk.Entry(self.network_frame, textvariable=self.ip_range_var, width=20).grid(row=1, column=1, padx=5)
        
        self.scan_type_var = tk.StringVar(value="fast")
        tk.Label(self.network_frame, text="Scan Type:", bg='#2c3e50', fg='white').grid(row=2, column=0, sticky='w')
        scan_type_combo = ttk.Combobox(
            self.network_frame,
            textvariable=self.scan_type_var,
            values=["fast", "comprehensive", "stealth"],
            state="readonly",
            width=15
        )
        scan_type_combo.grid(row=2, column=1, padx=5)
        
    def create_results_display(self):
        """Create results display area"""
        self.results_frame = tk.LabelFrame(
            self.root,
            text="📊 Scan Results",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=10
        )
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            width=60,
            height=15,
            bg='#34495e',
            fg='white',
            font=('Consolas', 9)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.results_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Export button
        self.export_button = tk.Button(
            self.results_frame,
            text="💾 Export Results",
            command=self.export_results,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            pady=5
        )
        self.export_button.pack(pady=5)
        
    def create_monitoring_panel(self):
        """Create real-time monitoring panel"""
        self.monitor_frame = tk.LabelFrame(
            self.root,
            text="📡 Real-Time Monitoring",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=10
        )
        
        # Create matplotlib figure for real-time plots
        self.fig = Figure(figsize=(6, 4), facecolor='#34495e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#34495e')
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.monitor_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Monitoring controls
        monitor_controls = tk.Frame(self.monitor_frame, bg='#2c3e50')
        monitor_controls.pack(fill=tk.X, pady=5)
        
        self.monitor_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            monitor_controls,
            text="Enable Real-Time Monitoring",
            variable=self.monitor_var,
            command=self.toggle_monitoring,
            bg='#2c3e50',
            fg='white',
            selectcolor='#34495e',
            activebackground='#2c3e50',
            activeforeground='white'
        ).pack(side=tk.LEFT)
        
    def create_map_panel(self):
        """Create map integration panel"""
        self.map_frame = tk.LabelFrame(
            self.root,
            text="🗺️ Geographic Visualization",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white',
            padx=10,
            pady=10
        )
        
        # Map controls
        map_controls = tk.Frame(self.map_frame, bg='#2c3e50')
        map_controls.pack(fill=tk.X, pady=5)
        
        tk.Button(
            map_controls,
            text="🗺️ Open Interactive Map",
            command=self.open_interactive_map,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10, 'bold'),
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            map_controls,
            text="📍 Add Current Location",
            command=self.add_location_to_map,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10, 'bold'),
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Map info
        self.map_info = tk.Text(
            self.map_frame,
            height=8,
            bg='#34495e',
            fg='white',
            font=('Arial', 9)
        )
        self.map_info.pack(fill=tk.BOTH, expand=True)
        
    def setup_layout(self):
        """Setup widget layout"""
        # Main title
        self.title_label.pack(fill=tk.X)
        
        # Main content area
        main_content = tk.Frame(self.root, bg='#1e1e1e')
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (controls and options)
        left_panel = tk.Frame(main_content, bg='#1e1e1e')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.options_frame.pack(fill=tk.X)
        
        # Right panel (results and monitoring)
        right_panel = tk.Frame(main_content, bg='#1e1e1e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Top right (results)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bottom right (monitoring and map)
        bottom_right = tk.Frame(right_panel, bg='#1e1e1e')
        bottom_right.pack(fill=tk.BOTH, expand=True)
        
        self.monitor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Status bar
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def start_comprehensive_scan(self):
        """Start comprehensive scanning"""
        if self.is_scanning:
            messagebox.showwarning("Warning", "Scan already in progress!")
            return
            
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            
            # Get selected scan types
            selected_scans = [scan_type for scan_type, var in self.scan_vars.items() if var.get()]
            
            if not selected_scans:
                messagebox.showwarning("Warning", "Please select at least one scan type!")
                return
            
            self.is_scanning = True
            self.scan_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress_var.set(0)
            self.status_var.set("Scanning...")
            
            # Start scan in separate thread
            scan_thread = threading.Thread(
                target=self.run_comprehensive_scan,
                args=(lat, lon, selected_scans),
                daemon=True
            )
            scan_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates!")
            
    def run_comprehensive_scan(self, lat, lon, scan_types):
        """Run comprehensive scan in background"""
        try:
            location = (lat, lon)
            
            # Update progress
            total_scans = len(scan_types)
            for i, scan_type in enumerate(scan_types):
                if not self.is_scanning:
                    break
                    
                # Update progress
                progress = (i / total_scans) * 100
                self.scan_queue.put(('progress', progress))
                
                # Log scan start
                self.scan_queue.put(('log', f"Starting {scan_type} scan..."))
                
                # Perform scan
                if scan_type == 'acoustic':
                    result = self.detector.acoustic_scan(duration=15, location=location)
                elif scan_type == 'rf':
                    result = self.detector.rf_scan(duration=15, location=location)
                elif scan_type == 'thermal':
                    result = self.detector.thermal_scan(location=location)
                elif scan_type == 'power':
                    result = self.detector.power_scan(location=location)
                elif scan_type == 'network':
                    result = self.detector.network_scan(self.ip_range_var.get(), self.scan_type_var.get())
                
                # Log result
                if 'error' not in result:
                    self.scan_queue.put(('log', f"{scan_type.title()} scan completed successfully"))
                    if 'mining_probability' in result:
                        self.scan_queue.put(('log', f"Mining probability: {result['mining_probability']:.2f}"))
                else:
                    self.scan_queue.put(('log', f"{scan_type.title()} scan failed: {result['error']}"))
                
                # Wait for REAL scan completion
                time.sleep(1)  # Wait for scan to complete
            
            # Final progress
            self.scan_queue.put(('progress', 100))
            self.scan_queue.put(('log', "Comprehensive scan completed!"))
            self.scan_queue.put(('scan_complete', None))
            
        except Exception as e:
            self.scan_queue.put(('log', f"Scan error: {str(e)}"))
            self.scan_queue.put(('scan_complete', None))
            
    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False
        self.scan_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Scan stopped")
        
    def update_gui(self):
        """Update GUI from scan queue"""
        try:
            while True:
                try:
                    msg_type, data = self.scan_queue.get_nowait()
                    
                    if msg_type == 'progress':
                        self.progress_var.set(data)
                    elif msg_type == 'log':
                        self.results_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {data}\n")
                        self.results_text.see(tk.END)
                    elif msg_type == 'scan_complete':
                        self.is_scanning = False
                        self.scan_button.config(state='normal')
                        self.stop_button.config(state='disabled')
                        self.status_var.set("Scan completed")
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"GUI update error: {e}")
            
        # Schedule next update
        self.root.after(100, self.update_gui)
        
    def toggle_monitoring(self):
        """Toggle real-time monitoring"""
        if self.monitor_var.get():
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start REAL monitoring with actual data"""
        try:
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitor_button.config(text="توقف نظارت", bg="#ff4444")
                
                # Start REAL monitoring thread
                self.monitor_thread = threading.Thread(target=self.run_real_monitoring, daemon=True)
                self.monitor_thread.start()
                
                self.log_message("نظارت واقعی شروع شد")
        except Exception as e:
            self.log_message(f"خطا در شروع نظارت: {e}")
    
    def run_real_monitoring(self):
        """Run REAL monitoring with actual system data"""
        try:
            while self.monitoring_active:
                try:
                    # Get REAL system data
                    real_data = self.get_real_system_data()
                    
                    # Update GUI with REAL data
                    self.update_monitoring_display(real_data)
                    
                    # Wait before next update
                    time.sleep(2)
                    
                except Exception as e:
                    self.log_message(f"خطا در نظارت: {e}")
                    time.sleep(5)
                    
        except Exception as e:
            self.log_message(f"خطای جدی در نظارت: {e}")
    
    def get_real_system_data(self) -> Dict[str, Any]:
        """Get REAL system monitoring data"""
        try:
            import psutil
            
            # REAL CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # REAL memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # REAL disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # REAL network usage
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024 * 1024)  # MB
            network_recv = network.bytes_recv / (1024 * 1024)  # MB
            
            # REAL temperature (if available)
            temperature = self.get_real_temperature()
            
            return {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'disk': disk_percent,
                'network_sent': network_sent,
                'network_recv': network_recv,
                'temperature': temperature,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_real_temperature(self) -> float:
        """Get REAL system temperature if available"""
        try:
            # Try to get CPU temperature on Linux
            if os.name == 'posix':
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        return temp
                except:
                    pass
            
            # Try to get temperature using psutil
            try:
                import psutil
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                return entry.current
            except:
                pass
            
            # Return None if temperature not available
            return None
            
        except Exception as e:
            return None
    
    def update_monitoring_display(self, real_data: Dict[str, Any]):
        """Update monitoring display with REAL data"""
        try:
            if 'error' in real_data:
                self.log_message(f"خطا در دریافت داده‌های نظارت: {real_data['error']}")
                return
            
            # Update CPU usage
            cpu_value = real_data.get('cpu', 0)
            self.cpu_label.config(text=f"CPU: {cpu_value:.1f}%")
            
            # Update memory usage
            memory_value = real_data.get('memory', 0)
            self.memory_label.config(text=f"حافظه: {memory_value:.1f}%")
            
            # Update disk usage
            disk_value = real_data.get('disk', 0)
            self.disk_label.config(text=f"دیسک: {disk_value:.1f}%")
            
            # Update network usage
            network_sent = real_data.get('network_sent', 0)
            network_recv = real_data.get('network_recv', 0)
            self.network_label.config(text=f"شبکه: ↑{network_sent:.1f}MB ↓{network_recv:.1f}MB")
            
            # Update temperature if available
            temperature = real_data.get('temperature')
            if temperature is not None:
                self.temperature_label.config(text=f"دما: {temperature:.1f}°C")
            else:
                self.temperature_label.config(text="دما: نامشخص")
            
            # Update REAL-time plot
            self.update_real_time_plot(real_data)
            
        except Exception as e:
            self.log_message(f"خطا در به‌روزرسانی نمایش نظارت: {e}")
    
    def update_real_time_plot(self, real_data: Dict[str, Any]):
        """Update REAL-time plot with actual data"""
        try:
            # Add REAL data to plot
            timestamp = real_data.get('timestamp', time.time())
            
            if hasattr(self, 'monitor_data') and hasattr(self, 'monitor_timestamps'):
                self.monitor_timestamps.append(timestamp)
                self.monitor_data.append(real_data.get('cpu', 0))
                
                # Keep only last 50 data points
                if len(self.monitor_data) > 50:
                    self.monitor_data.pop(0)
                    self.monitor_timestamps.pop(0)
                
                # Update plot
                self.monitor_ax.clear()
                self.monitor_ax.plot(self.monitor_timestamps, self.monitor_data, 'b-', linewidth=2)
                self.monitor_ax.set_title('استفاده CPU (داده‌های واقعی)', fontsize=12)
                self.monitor_ax.set_xlabel('زمان')
                self.monitor_ax.set_ylabel('درصد CPU')
                self.monitor_ax.grid(True, alpha=0.3)
                
                # Format x-axis
                if self.monitor_timestamps:
                    start_time = self.monitor_timestamps[0]
                    self.monitor_ax.set_xlim(start_time, start_time + 100)
                
                self.monitor_canvas.draw()
                
        except Exception as e:
            self.log_message(f"خطا در به‌روزرسانی نمودار: {e}")
    
    def stop_monitoring(self):
        """Stop REAL monitoring"""
        try:
            if self.monitoring_active:
                self.monitoring_active = False
                self.monitor_button.config(text="شروع نظارت", bg="#44ff44")
                
                if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
                    self.monitor_thread.join(timeout=1)
                
                self.log_message("نظارت متوقف شد")
        except Exception as e:
            self.log_message(f"خطا در توقف نظارت: {e}")
    
    def toggle_monitoring(self):
        """Toggle REAL monitoring on/off"""
        try:
            if self.monitoring_active:
                self.stop_monitoring()
            else:
                self.start_monitoring()
        except Exception as e:
            self.log_message(f"خطا در تغییر وضعیت نظارت: {e}")
            
    def open_interactive_map(self):
        """Open interactive map in browser"""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            
            # Create interactive map
            m = folium.Map(location=[lat, lon], zoom_start=15)
            
            # Add current location marker
            folium.Marker(
                [lat, lon],
                popup="Current Scan Location",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Add mining detection zones
            folium.Circle(
                [lat, lon],
                radius=1000,  # 1km radius
                popup="Mining Detection Zone",
                color="red",
                fill=True,
                fillColor="red",
                fillOpacity=0.2
            ).add_to(m)
            
            # Save map
            map_file = "mining_detection_map.html"
            m.save(map_file)
            
            # Open in browser
            webbrowser.open(f"file://{os.path.abspath(map_file)}")
            
            self.map_info.insert(tk.END, f"Map opened: {map_file}\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open map: {str(e)}")
            
    def add_location_to_map(self):
        """Add current location to map info"""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            
            location_info = f"📍 Location: {lat:.6f}, {lon:.6f}\n"
            location_info += f"🕐 Added: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            location_info += f"🔍 Scan Status: {'Active' if self.is_scanning else 'Idle'}\n"
            location_info += "-" * 40 + "\n"
            
            self.map_info.insert(tk.END, location_info)
            self.map_info.see(tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates!")
            
    def export_results(self):
        """Export scan results"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                content = self.results_text.get(1.0, tk.END)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = ModernMiningDetectorGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()