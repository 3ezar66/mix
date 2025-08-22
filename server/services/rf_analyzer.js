import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';
import { EventEmitter } from 'events';
export class RFAnalyzer extends EventEmitter {
    port = null;
    parser = null;
    calibrationData = new Map();
    baselinePower = 0;
    baselineHeat = 0;
    constructor() {
        super();
        this.initializeSerialConnection();
        this.calibrate();
    }
    async initializeSerialConnection() {
        try {
            // اتصال به دستگاه آنالایزر RF
            this.port = new SerialPort({
                path: process.env.RF_ANALYZER_PORT || 'COM3',
                baudRate: 115200
            });
            this.parser = this.port.pipe(new ReadlineParser());
            this.port.on('error', (err) => {
                console.error('RF Analyzer connection error:', err);
                this.emit('error', err);
            });
            this.parser.on('data', (data) => {
                this.processRFData(data);
            });
        }
        catch (error) {
            console.error('Failed to initialize RF Analyzer:', error);
        }
    }
    async calibrate() {
        // کالیبراسیون اولیه دستگاه
        console.log('Calibrating RF Analyzer...');
        // جمع‌آوری داده‌های پایه برای 60 ثانیه
        const baselineData = [];
        return new Promise((resolve) => {
            const timeout = setTimeout(() => {
                this.baselinePower = this.calculateAverage(baselineData.map(d => d.powerConsumption));
                this.baselineHeat = this.calculateAverage(baselineData.map(d => d.heatSignature));
                console.log('Calibration complete');
                resolve(true);
            }, 60000);
            this.on('rfData', (data) => {
                baselineData.push(data);
            });
        });
    }
    calculateAverage(values) {
        return values.reduce((a, b) => a + b, 0) / values.length;
    }
    processRFData(rawData) {
        try {
            const data = JSON.parse(rawData);
            const rfData = {
                powerConsumption: this.normalizePowerConsumption(data.power),
                heatSignature: this.normalizeHeatSignature(data.heat),
                timestamp: new Date()
            };
            this.emit('rfData', rfData);
        }
        catch (error) {
            console.error('Error processing RF data:', error);
        }
    }
    normalizePowerConsumption(value) {
        // نرمال‌سازی مقادیر توان مصرفی
        const normalized = (value - this.baselinePower) / (this.baselinePower * 3);
        return Math.min(1, Math.max(0, normalized));
    }
    normalizeHeatSignature(value) {
        // نرمال‌سازی مقادیر سیگنال حرارتی
        const normalized = (value - this.baselineHeat) / (this.baselineHeat * 2);
        return Math.min(1, Math.max(0, normalized));
    }
    async analyze(ipAddress) {
        return new Promise((resolve) => {
            const readings = [];
            const timeout = setTimeout(() => {
                const avgPower = this.calculateAverage(readings.map(r => r.powerConsumption));
                const avgHeat = this.calculateAverage(readings.map(r => r.heatSignature));
                resolve({
                    powerConsumption: avgPower,
                    heatSignature: avgHeat
                });
            }, 5000); // 5 seconds of readings
            const dataHandler = (data) => {
                readings.push(data);
            };
            this.on('rfData', dataHandler);
            // Cleanup
            timeout.unref();
            setTimeout(() => {
                this.off('rfData', dataHandler);
            }, 5000);
        });
    }
    async disconnect() {
        if (this.port) {
            await new Promise((resolve) => {
                this.port.close(() => resolve());
            });
        }
    }
}
