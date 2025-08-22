#!/usr/bin/env python3
"""
MinerHunter 🚀 – The Legendary All‑in‑One Crypto‑Miner Detector
==============================================================
Version     : 0.1.0‑alpha  (14 Jun 2025)
Author      : ✨  YOU, the history‑maker  ✨
License     : MIT
Purpose     : Unite several cutting‑edge, power‑agnostic (no power‑meter, no drone, no CCTV) techniques
              into one Python command‑line tool that hunts ASIC/GPU/CPU miners over LAN, Wi‑Fi, BLE,
              RF, and encrypted network flows.

─────────────────────────────────────────────────────────────────────────────
INCLUDED SUB‑MODULES
─────────────────────────────────────────────────────────────────────────────
  • LAN Stratum / ASIC port scan via Nmap or Scapy
  • TLS JA3 / Stratum banner fingerprinting via PyShark
  • NetFlow/PCAP offline ML classifier (placeholder model)
  • BLE beacon and Wi‑Fi probe/SSID matcher (Bleak + Scapy)
  • RF front‑end (RTL‑SDR) hash‑rate‑noise fingerprint (prototype)
  • Acoustic fan‑signature classifier (pyaudio + TF/Lite)
  • USB‑PID hunter (udevadm / pywinusb)
  • SNMP crypto OID crawler
  • Clock‑skew passive fingerprint (p0f‑style)
─────────────────────────────────────────────────────────────────────────────

⚠️  This is a *framework* – many functions are stubs you must finish and
   integrate with your own models, rulesets, and hardware.

"""

import argparse
import asyncio
import logging
import os
import platform
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Optional imports guarded; the script degrades gracefully
try:
    import scapy.all as scapy
except ImportError:
    scapy = None

try:
    import nmap  # python‑nmap
except ImportError:
    nmap = None

try:
    import pyshark
except ImportError:
    pyshark = None

try:
    from bleak import BleakScanner
except ImportError:
    BleakScanner = None

try:
    import pyaudio
    import numpy as np
    # TensorFlow Lite might not be available everywhere
    import tensorflow as tf
except ImportError:
    pyaudio = None

try:
    from pyrtlsdr import RtlSdr
except ImportError:
    RtlSdr = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("MinerHunter")

# ─────────────────────────────────────────────────────────────────────────────
# Utility functions
# ─────────────────────────────────────────────────────────────────────────────

def resolve_interface():
    """Return default interface for scapy if available."""
    if scapy:
        return scapy.conf.iface
    return None


# ─────────────────────────────────────────────────────────────────────────────
# LAN Scanner – ports & banner grab
# ─────────────────────────────────────────────────────────────────────────────
async def lan_scan(targets: str | list[str], fast: bool = True):
    """Scan IP/CIDR ranges for known miner ports."""
    ports = "4028,3333,4444,5555,4233,8233"  # common ASIC/GPU miner ports
    results = []
    if nmap:
        nm = nmap.PortScannerAsync()
        log.info("Starting Nmap async scan on %s", targets)
        await asyncio.to_thread(
            nm.scan,
            hosts=targets,
            ports=ports,
            arguments="-sT -Pn --open --host-timeout 30m" + (" -T5" if fast else ""),
        )
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    service = nm[host][proto][port].get("name", "?")
                    results.append(
                        {"ip": host, "proto": proto, "port": port, "service": service}
                    )
        log.info("LAN scan found %d open miner‑style ports", len(results))
    else:
        log.warning("python‑nmap not installed; skipping LAN scan.")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# TLS / Stratum fingerprint (JA3, banner)
# ─────────────────────────────────────────────────────────────────────────────
# نمونه هش‌های JA3 برای ماینرها (نمونه، واقعی نیست)
MINER_JA3_HASHES = {
    "769c5d6b4b8c5e3e1a1e1e1e1e1e1e1e": "Antminer S9",
    "aabbccddeeff00112233445566778899": "Whatsminer M20S"
}

async def live_capture(interface: str, duration: int = 60):
    if not pyshark:
        log.warning("pyshark not available; cannot perform live capture.")
        return []
    log.info("Starting live capture on %s for %ds", interface, duration)
    cap = pyshark.LiveCapture(
        interface=interface,
        bpf_filter="tcp port 3333 or tcp port 5555 or tcp port 4444",
    )
    cap.sniff(timeout=duration)
    alerts = []
    for pkt in cap:
        try:
            if hasattr(pkt, "tls"):
                ja3 = getattr(pkt.tls, 'handshake_extensions_type', None)
                ja3_str = str(ja3)
                miner_name = MINER_JA3_HASHES.get(ja3_str)
                if miner_name:
                    log.info(f"Miner detected by JA3: {miner_name}")
                    alerts.append({"type": "TLS", "src": pkt.ip.src, "ja3": ja3_str, "miner": miner_name})
                else:
                    log.info(f"TLS JA3 hash: {ja3_str}")
                    alerts.append({"type": "TLS", "src": pkt.ip.src, "ja3": ja3_str})
            elif hasattr(pkt, 'tcp') and hasattr(pkt.tcp, 'payload') and b"mining.subscribe" in bytes(pkt.tcp.payload):
                alerts.append({"type": "Stratum", "src": pkt.ip.src, "info": "subscribe"})
        except Exception as e:
            log.error(f"Error in live_capture: {e}")
            continue
    log.info("Live capture produced %d suspect flows", len(alerts))
    return alerts


# ─────────────────────────────────────────────────────────────────────────────
# BLE Scanner
# ─────────────────────────────────────────────────────────────────────────────
async def ble_scan(timeout=30):
    if not BleakScanner:
        log.warning("bleak missing; skipping BLE scan")
        return []
    log.info("Scanning BLE for %d seconds", timeout)
    devices = await BleakScanner.discover(timeout=timeout)
    miners = [d for d in devices if "antminer" in (d.name or "").lower()]
    for m in miners:
        log.info("Found BLE miner candidate: %s (%s)", m.address, m.name)
    return miners


# ─────────────────────────────────────────────────────────────────────────────
# Wi‑Fi Probe / SSID scanner
# ─────────────────────────────────────────────────────────────────────────────
def wifi_probe_scan(interface="wlan0", timeout=60):
    """Passive Wi‑Fi probe request scan via scapy."""
    if scapy is None:
        log.warning("Scapy missing; skipping Wi‑Fi probe scan")
        return []
    log.info("Listening for Wi‑Fi probes on %s", interface)
    miners = []

    def handler(pkt):
        if pkt.haslayer(scapy.Dot11ProbeReq):
            ssid = pkt.info.decode(errors="ignore").lower()
            if "antminer" in ssid:
                miners.append({"mac": pkt.addr2, "ssid": ssid})

    scapy.sniff(
        iface=interface,
        prn=handler,
        store=False,
        timeout=timeout,
        monitor=True,
    )
    log.info("Probe scan caught %d miner probes", len(miners))
    return miners


# ─────────────────────────────────────────────────────────────────────────────
# Acoustic Fan Signature
# ─────────────────────────────────────────────────────────────────────────────
def acoustic_scan(seconds=10):
    if pyaudio is None or np is None:
        log.warning("pyaudio / numpy / tensorflow missing; skipping acoustic scan")
        return [{"error": "pyaudio/numpy/tensorflow not available"}]
    log.info("Recording audio for %ds", seconds)
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(np.frombuffer(data, dtype=np.int16))
    stream.stop_stream()
    stream.close()
    p.terminate()
    audio = np.concatenate(frames)
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1/RATE)
    peak_freq = freqs[np.argmax(fft)]
    log.info(f"Peak fan frequency: {peak_freq:.1f} Hz")
    return [{"peak_fan_freq": float(peak_freq)}]


# ─────────────────────────────────────────────────────────────────────────────
# RTL‑SDR RF scan
# ─────────────────────────────────────────────────────────────────────────────
async def rf_scan(center_freq=2.4e9, samp_rate=2e6, duration=30):
    if RtlSdr is None:
        log.warning("pyrtlsdr missing; skipping RF scan")
        return [{"error": "pyrtlsdr not available"}]
    log.info("Starting RF scan around %.1f MHz", center_freq / 1e6)
    sdr = RtlSdr()
    sdr.sample_rate = samp_rate
    sdr.center_freq = center_freq
    sdr.gain = 'auto'
    samples = sdr.read_samples(int(samp_rate * duration))
    sdr.close()
    power = np.abs(np.fft.fft(samples))
    freqs = np.fft.fftfreq(len(samples), 1/samp_rate)
    peak_freq = freqs[np.argmax(power)] + center_freq
    log.info(f"Peak RF frequency: {peak_freq/1e6:.2f} MHz")
    return [{"peak_rf_freq": float(peak_freq)}]


# ─────────────────────────────────────────────────────────────────────────────
# SNMP Miner OID crawl
# ─────────────────────────────────────────────────────────────────────────────
from pysnmp.hlapi import *

async def snmp_crawl(hosts, community="public"):
    alerts = []
    for host in hosts:
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),
                UdpTransportTarget((host, 161), timeout=1, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.4.1.30297.101.1.0")),  # Bitmain sample OID
            )

            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            if errorIndication:
                continue
            if errorStatus:
                continue

            for varBind in varBinds:
                alerts.append({"host": host, "hashrate": str(varBind[1])})
        except Exception as e:
            continue

    log.info("SNMP crawl done; %d miners found", len(alerts))
    return alerts


# ─────────────────────────────────────────────────────────────────────────────
# Clock‑skew fingerprint via p0f‑like passive capture
# ─────────────────────────────────────────────────────────────────────────────
def clock_skew_analyse(pcap_file):
    try:
        import pyshark
    except ImportError:
        log.warning("pyshark not available; skipping clock skew analysis")
        return [{"error": "pyshark not available"}]
    cap = pyshark.FileCapture(pcap_file)
    times = []
    for pkt in cap:
        if hasattr(pkt, 'sniff_time'):
            times.append(pkt.sniff_time.timestamp())
    cap.close()
    if len(times) < 2:
        return [{"error": "Not enough packets for analysis"}]
    diffs = np.diff(times)
    skew = float(np.std(diffs))
    log.info(f"Clock skew stddev: {skew:.6f} s")
    return [{"clock_skew_stddev": skew}]


# ─────────────────────────────────────────────────────────────────────────────
# NetFlow/PCAP offline ML classifier (در حال حاضر پشتیبانی نمی‌شود)
# ─────────────────────────────────────────────────────────────────────────────
def netflow_ml_classifier(*args, **kwargs):
    log.warning("NetFlow/PCAP offline ML classifier is not implemented in this version.")
    return [{"error": "NetFlow/PCAP ML classifier not implemented"}]


# ─────────────────────────────────────────────────────────────────────────────
# Argparse & Orchestration
# ─────────────────────────────────────────────────────────────────────────────
async def main():
    p = argparse.ArgumentParser(
        description="MinerHunter 🚀 – Multi‑modal crypto‑miner detection Swiss‑army knife"
    )
    p.add_argument(
        "--targets",
        help="IP/CIDR targets for LAN scan (default: 192.168.0.0/24)",
        default="192.168.0.0/24",
    )
    p.add_argument("--interface", help="Interface for live capture or Wi‑Fi scans")
    p.add_argument("--fast", action="store_true", help="Fast Nmap timings")
    p.add_argument("--ble", action="store_true", help="Enable BLE scanner")
    p.add_argument("--wifi", action="store_true", help="Enable Wi‑Fi probe scanner")
    p.add_argument("--acoustic", action="store_true", help="Enable acoustic fan scan")
    p.add_argument("--rf", action="store_true", help="Enable RTL‑SDR RF scan")
    p.add_argument("--snmp", action="store_true", help="Enable SNMP OID crawl")
    args = p.parse_args()

    findings = []

    findings += await lan_scan(args.targets, fast=args.fast)

    if args.interface:
        findings += await live_capture(args.interface)

    if args.ble:
        findings += await ble_scan()

    if args.wifi:
        findings += wifi_probe_scan(interface=args.interface or "wlan0")

    if args.acoustic:
        findings += acoustic_scan()

    if args.rf:
        findings += await rf_scan()

    if args.snmp:
        targets = [f["ip"] for f in findings if "ip" in f]
        findings += await snmp_crawl(targets)

    if findings:
        print("\n🚩  POTENTIAL MINERS DETECTED  🚩")
        for f in findings:
            print(f)
    else:
        print("✅  No miners detected (yet) – keep watching!")
    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(130)
