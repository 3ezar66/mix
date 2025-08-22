import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { db } from '../db';
import { detectedMiners } from '../../shared/schema';
import { eq } from 'drizzle-orm';
import { verifyToken } from '../../server/security/auth';
import { lookupLocation } from '../../server/services/geoip_lookup';
import { NetworkScanner } from '../../server/services/network_scanner';
import { RFAnalyzer } from '../../server/services/rf_analyzer';

const scanner = new NetworkScanner();
const rfAnalyzer = new RFAnalyzer();

export default async function (fastify: FastifyInstance) {
  // تنظیمات مربوط به امنیت و محدودیت درخواست‌ها
  fastify.addHook('preHandler', verifyToken);
  
  fastify.get('/api/miners', {
    schema: {
      response: {
        200: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              latitude: { type: 'number' },
              longitude: { type: 'number' },
              ip_address: { type: 'string' },
              confidence_score: { type: 'number' },
              owner: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  type: { type: 'string' }
                }
              },
              last_seen: { type: 'string' }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    try {
      // دریافت دستگاه‌های مشکوک از دیتابیس
      const suspectedMiners = await db.select()
        .from(detectedMiners)
        .where(eq(detectedMiners.isActive, "true"));

      // بررسی مجدد هر دستگاه
      const verifiedMiners = await Promise.all(
        suspectedMiners.map(async (device) => {
          // بررسی موقعیت جغرافیایی
          const geoData = await lookupLocation(device.ipAddress);
          
          // اسکن شبکه برای اطمینان از فعال بودن
          const networkData = await scanner.scanDevice(device.ipAddress);
          
          // آنالیز سیگنال‌های RF
          const rfData = await rfAnalyzer.analyze(device.ipAddress);
          
          // محاسبه امتیاز اطمینان جدید
          const newScore = calculateConfidenceScore(
            device,
            networkData,
            rfData,
            geoData
          );

          // به‌روزرسانی دیتابیس
          if (Math.abs(newScore - device.confidenceScore) > 5) {
            await db.update(detectedMiners)
              .set({ confidenceScore: newScore, detectionTime: new Date().toISOString() })
              .where(eq(detectedMiners.id, device.id));
          }

          return {
            id: device.id,
            latitude: geoData.latitude,
            longitude: geoData.longitude,
                         ip_address: device.ipAddress,
             confidence_score: newScore,
             owner: { name: device.hostname || 'Unknown', type: device.deviceType || 'Unknown' },
             last_seen: device.detectionTime
          };
        })
      );

      reply.send(verifiedMiners);
    } catch (error) {
      fastify.log.error(error);
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'خطا در دریافت اطلاعات ماینرها'
      });
    }
  });
}

async function getAllMiners(request: FastifyRequest, reply: FastifyReply) {
  try {
    const miners = await db.select().from(detectedMiners).all();
    return reply.send(miners);
  } catch (error) {
    console.error('Error fetching miners:', error);
    return reply.code(500).send({
      error: 'Internal server error',
      message: 'Failed to fetch miner data'
    });
  }
}

function calculateConfidenceScore(
  device: any,
  networkData: any,
  rfData: any,
  geoData: any
): number {
  let score = 0;
  const weights = {
    network: 0.4,
    rf: 0.3,
    geo: 0.2,
    history: 0.1
  };

  // امتیاز بر اساس الگوی ترافیک شبکه
  if (networkData) {
    score += weights.network * (
      networkData.miningPortsDetected * 20 +
      networkData.highBandwidthUsage * 15 +
      networkData.suspiciousConnections * 10
    );
  }

  // امتیاز بر اساس سیگنال‌های RF
  if (rfData) {
    score += weights.rf * (
      rfData.powerConsumption * 25 +
      rfData.heatSignature * 15
    );
  }

  // امتیاز بر اساس موقعیت جغرافیایی
  if (geoData && geoData.in_ilam) {
    score += weights.geo * 100;
  }

  // امتیاز بر اساس سابقه
     const historyScore = device.confidenceScore || 50;
  score += weights.history * historyScore;

  // محدود کردن امتیاز بین 0 تا 100
  return Math.min(100, Math.max(0, score));
}
