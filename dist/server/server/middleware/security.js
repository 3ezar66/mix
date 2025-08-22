import { RateLimiterMemory } from 'rate-limiter-flexible';
import { Logger } from '../utils/logger';
const logger = Logger.getInstance('SecurityMiddleware');
// محدودیت تعداد درخواست
const rateLimiter = new RateLimiterMemory({
    points: Number(process.env.RATE_LIMIT_MAX) || 100,
    duration: Number(process.env.RATE_LIMIT_WINDOW) || 900, // 15 minutes
});
export async function rateLimitMiddleware(request, reply) {
    try {
        const ip = request.ip;
        await rateLimiter.consume(ip);
    }
    catch (error) {
        logger.security('Rate limit exceeded', {
            ip: request.ip,
            path: request.url,
            method: request.method
        });
        reply.status(429).send({
            error: 'Too Many Requests',
            message: 'لطفاً کمی صبر کنید و دوباره تلاش کنید'
        });
    }
}
// بررسی IP های مجاز
const ALLOWED_IPS = new Set([
    '127.0.0.1',
    // اضافه کردن IP های مجاز
]);
export function ipFilterMiddleware(request, reply) {
    const ip = request.ip;
    if (!ALLOWED_IPS.has(ip)) {
        logger.security('Unauthorized IP access attempt', {
            ip,
            path: request.url,
            method: request.method
        });
        reply.status(403).send({
            error: 'Forbidden',
            message: 'دسترسی غیرمجاز'
        });
    }
}
// محدودیت های CORS
export const corsOptions = {
    origin: process.env.NODE_ENV === 'production'
        ? ['https://your-production-domain.com']
        : true,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true,
    maxAge: 86400 // 24 hours
};
