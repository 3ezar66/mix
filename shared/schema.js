import { integer, text, real, sqliteTable as table } from 'drizzle-orm/sqlite-core';
import { createInsertSchema } from "drizzle-zod";
// Users table for authentication
export const users = table("users", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    username: text("username").notNull().unique(),
    password: text("password").notNull(),
    role: text("role").default("admin"),
    createdAt: text("created_at").notNull().$defaultFn(() => new Date().toISOString()),
    lastLogin: text("last_login")
});
// RF Signal Analysis for real radio frequency detection
export const rfSignals = table("rf_signals", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    frequency: real("frequency").notNull(), // MHz
    signalStrength: real("signal_strength").notNull(), // dBm
    bandwidth: real("bandwidth"), // MHz
    modulationType: text("modulation_type"),
    noiseFloor: real("noise_floor"), // dBm
    snr: real("snr"), // Signal to Noise Ratio
    location: text("location"),
    deviceSignature: text("device_signature"),
    switchingPattern: text("switching_pattern"), // Mining-specific switching patterns
    harmonics: text("harmonics"), // JSON string of harmonic frequencies
    detectionTime: text("detection_time").notNull().$defaultFn(() => new Date().toISOString()),
    confidenceLevel: real("confidence_level").notNull() // 0-1
});
// Power Line Communication (PLC) Analysis
export const plcAnalysis = table("plc_analysis", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    powerLineFreq: real("power_line_freq").notNull(), // Power line frequency anomalies
    harmonicDistortion: real("harmonic_distortion"),
    powerQuality: real("power_quality"), // THD (Total Harmonic Distortion)
    voltageFluctuation: real("voltage_fluctuation"),
    currentSpikes: text("current_spikes"), // JSON string of current spike data
    powerFactor: real("power_factor"),
    location: text("location"),
    timestamp: text("timestamp").notNull().$defaultFn(() => new Date().toISOString()),
    minerIndicators: text("miner_indicators") // JSON string of mining device indicators
});
// Acoustic Signature Analysis
export const acousticSignatures = table("acoustic_signatures", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    fanSpeedRpm: integer("fan_speed_rpm"),
    acousticFingerprint: text("acoustic_fingerprint"), // Unique acoustic pattern
    frequencySpectrum: text("frequency_spectrum"), // JSON string of audio frequency analysis
    noiseLevel: real("noise_level"), // dB
    fanNoisePattern: text("fan_noise_pattern"),
    coolingSystemType: text("cooling_system_type"),
    deviceModel: text("device_model"), // Detected ASIC/GPU model
    location: text("location"),
    recordingTime: text("recording_time").notNull().$defaultFn(() => new Date().toISOString()),
    matchConfidence: real("match_confidence") // 0-1
});
// Thermal Signature Detection
export const thermalSignatures = table("thermal_signatures", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    surfaceTemp: real("surface_temp"), // Celsius
    ambientTemp: real("ambient_temp"), // Celsius
    tempDifference: real("temp_difference"),
    heatPattern: text("heat_pattern"), // Thermal pattern description
    thermalImage: text("thermal_image"), // Base64 encoded thermal image
    hotspotCount: integer("hotspot_count"),
    thermalEfficiency: real("thermal_efficiency"),
    location: text("location"),
    captureTime: text("capture_time").notNull().$defaultFn(() => new Date().toISOString()),
    deviceType: text("device_type") // ASIC, GPU, etc.
});
// Network Traffic Analysis (Deep Packet Inspection)
export const networkTraffic = table("network_traffic", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    srcIp: text("src_ip").notNull(),
    dstIp: text("dst_ip").notNull(),
    srcPort: integer("src_port"),
    dstPort: integer("dst_port"),
    protocol: text("protocol").notNull(),
    packetSize: integer("packet_size"),
    payloadHash: text("payload_hash"), // Hash of payload for mining protocol detection
    stratumProtocol: text("stratum_protocol").default("false"),
    poolAddress: text("pool_address"), // Mining pool address if detected
    minerAgent: text("miner_agent"), // Mining software user agent
    sessionDuration: integer("session_duration"), // seconds
    dataVolume: integer("data_volume"), // bytes
    timestamp: text("timestamp").notNull().$defaultFn(() => new Date().toISOString()),
    threatLevel: text("threat_level").default("low")
});
export const detectedMiners = table("detected_miners", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    ipAddress: text("ip_address").notNull(),
    macAddress: text("mac_address"),
    hostname: text("hostname"),
    latitude: real("latitude"),
    longitude: real("longitude"),
    city: text("city"),
    detectionMethod: text("detection_method").notNull(),
    powerConsumption: real("power_consumption"),
    hashRate: text("hash_rate"),
    deviceType: text("device_type"),
    processName: text("process_name"),
    cpuUsage: real("cpu_usage"),
    memoryUsage: real("memory_usage"),
    networkUsage: real("network_usage"),
    gpuUsage: real("gpu_usage"),
    detectionTime: text("detection_time").notNull().$defaultFn(() => new Date().toISOString()),
    suspicion_score: integer("suspicion_score").notNull(),
    confidenceScore: integer("confidence_score").notNull(),
    threatLevel: text("threat_level").notNull(),
    status: text("status").default("active"),
    notes: text("notes"),
    isActive: text("is_active").default("true")
});
export const networkConnections = table("network_connections", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    localAddress: text("local_address").notNull(),
    localPort: integer("local_port").notNull(),
    remoteAddress: text("remote_address"),
    remotePort: integer("remote_port"),
    protocol: text("protocol").notNull(),
    status: text("status").notNull(),
    processName: text("process_name"),
    detectionTime: text("detection_time").notNull().$defaultFn(() => new Date().toISOString()),
    minerId: integer("miner_id").references(() => detectedMiners.id)
});
export const scanSessions = table("scan_sessions", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    sessionType: text("session_type").notNull(),
    ipRange: text("ip_range"),
    ports: text("ports"),
    startTime: text("start_time").notNull().$defaultFn(() => new Date().toISOString()),
    endTime: text("end_time"),
    status: text("status").notNull(),
    devicesFound: integer("devices_found").default(0),
    minersDetected: integer("miners_detected").default(0),
    errors: text("errors")
});
export const systemActivities = table("system_activities", {
    id: integer("id").primaryKey({ autoIncrement: true }),
    activityType: text("activity_type").notNull(),
    description: text("description").notNull(),
    severity: text("severity").notNull(),
    timestamp: text("timestamp").notNull().$defaultFn(() => new Date().toISOString()),
    metadata: text("metadata")
});
// Insert schemas
export const insertUserSchema = createInsertSchema(users).omit({
    id: true,
    createdAt: true
});
export const insertMinerSchema = createInsertSchema(detectedMiners).omit({
    id: true,
    detectionTime: true
});
export const insertConnectionSchema = createInsertSchema(networkConnections).omit({
    id: true,
    detectionTime: true
});
export const insertScanSessionSchema = createInsertSchema(scanSessions).omit({
    id: true,
    startTime: true
});
export const insertActivitySchema = createInsertSchema(systemActivities).omit({
    id: true,
    timestamp: true
});
// Additional schemas for new tables
export const insertRfSignalSchema = createInsertSchema(rfSignals).omit({
    id: true,
    detectionTime: true
});
export const insertPlcAnalysisSchema = createInsertSchema(plcAnalysis).omit({
    id: true,
    timestamp: true
});
export const insertAcousticSignatureSchema = createInsertSchema(acousticSignatures).omit({
    id: true,
    recordingTime: true
});
export const insertThermalSignatureSchema = createInsertSchema(thermalSignatures).omit({
    id: true,
    captureTime: true
});
export const insertNetworkTrafficSchema = createInsertSchema(networkTraffic).omit({
    id: true,
    timestamp: true
});
