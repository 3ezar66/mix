import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';
import { EventEmitter } from 'events';

interface RFData {
    powerConsumption: number;  // 0-1 normalized value
    heatSignature: number;    // 0-1 normalized value
    timestamp: Date;
}

export class RFAnalyzer extends EventEmitter {
    private port: SerialPort | null = null;
    private parser: ReadlineParser | null = null;
    private calibrationData: Map<string, number> = new Map();
    private baselinePower: number = 0;
    private baselineHeat: number = 0;

    constructor() {
        super();
        this.initializeSerialConnection();
        this.calibrate();
    }

    private async initializeSerialConnection() {
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

            this.parser.on('data', (data: string) => {
                this.processRFData(data);
            });
        } catch (error) {
            console.error('Failed to initialize RF Analyzer:', error);
        }
    }

    private async calibrate() {
        // کالیبراسیون اولیه دستگاه
        console.log('Calibrating RF Analyzer...');
        
        // جمع‌آوری داده‌های پایه برای 60 ثانیه
        const baselineData: RFData[] = [];
        
        return new Promise((resolve) => {
            const timeout = setTimeout(() => {
                this.baselinePower = this.calculateAverage(baselineData.map(d => d.powerConsumption));
                this.baselineHeat = this.calculateAverage(baselineData.map(d => d.heatSignature));
                console.log('Calibration complete');
                resolve(true);
            }, 60000);

            this.on('rfData', (data: RFData) => {
                baselineData.push(data);
            });
        });
    }

    private calculateAverage(values: number[]): number {
        return values.reduce((a, b) => a + b, 0) / values.length;
    }

    private processRFData(rawData: string) {
        try {
            const data = JSON.parse(rawData);
            const rfData: RFData = {
                powerConsumption: this.normalizePowerConsumption(data.power),
                heatSignature: this.normalizeHeatSignature(data.heat),
                timestamp: new Date()
            };
            this.emit('rfData', rfData);
        } catch (error) {
            console.error('Error processing RF data:', error);
        }
    }

    private normalizePowerConsumption(value: number): number {
        // نرمال‌سازی مقادیر توان مصرفی
        const normalized = (value - this.baselinePower) / (this.baselinePower * 3);
        return Math.min(1, Math.max(0, normalized));
    }

    private normalizeHeatSignature(value: number): number {
        // نرمال‌سازی مقادیر سیگنال حرارتی
        const normalized = (value - this.baselineHeat) / (this.baselineHeat * 2);
        return Math.min(1, Math.max(0, normalized));
    }

    public async analyze(ipAddress: string): Promise<{
        powerConsumption: number;
        heatSignature: number;
    }> {
        return new Promise((resolve) => {
            const readings: RFData[] = [];
            const timeout = setTimeout(() => {
                const avgPower = this.calculateAverage(readings.map(r => r.powerConsumption));
                const avgHeat = this.calculateAverage(readings.map(r => r.heatSignature));
                
                resolve({
                    powerConsumption: avgPower,
                    heatSignature: avgHeat
                });
            }, 5000); // 5 seconds of readings

            const dataHandler = (data: RFData) => {
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

    public async disconnect() {
        if (this.port) {
            await new Promise<void>((resolve) => {
                this.port!.close(() => resolve());
            });
        }
    }
}
