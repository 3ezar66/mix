import { Logger } from './logger';
export class AppError extends Error {
    status;
    code;
    details;
    constructor(message, status = 500, code = 'INTERNAL_ERROR', details) {
        super(message);
        this.status = status;
        this.code = code;
        this.details = details;
        Error.captureStackTrace(this, this.constructor);
    }
}
export class ErrorHandler {
    static logger = Logger.getInstance('ErrorHandler');
    static handleError(err, req, res, next) {
        let errorResponse;
        if (err instanceof AppError) {
            errorResponse = {
                status: err.status,
                message: err.message,
                code: err.code,
                details: err.details
            };
        }
        else {
            errorResponse = {
                status: 500,
                message: 'An unexpected error occurred',
                code: 'INTERNAL_ERROR'
            };
        }
        // Log error with context
        this.logger.error(err.message, {
            error: err,
            path: req.path,
            method: req.method,
            ip: req.ip,
            userId: req.user?.id,
            requestId: req.headers['x-request-id'],
            body: req.body,
            query: req.query
        });
        // Send error response
        res.status(errorResponse.status).json(errorResponse);
    }
    static handleUncaughtException(err) {
        this.logger.error('Uncaught Exception', { error: err });
        process.exit(1);
    }
    static handleUnhandledRejection(reason) {
        this.logger.error('Unhandled Rejection', { error: reason });
        process.exit(1);
    }
    // Custom error types
    static notFound(message = 'Resource not found') {
        return new AppError(message, 404, 'NOT_FOUND');
    }
    static badRequest(message, details) {
        return new AppError(message, 400, 'BAD_REQUEST', details);
    }
    static unauthorized(message = 'Unauthorized') {
        return new AppError(message, 401, 'UNAUTHORIZED');
    }
    static forbidden(message = 'Forbidden') {
        return new AppError(message, 403, 'FORBIDDEN');
    }
    static validation(message, details) {
        return new AppError(message, 422, 'VALIDATION_ERROR', details);
    }
    static tooManyRequests(message = 'Too many requests') {
        return new AppError(message, 429, 'TOO_MANY_REQUESTS');
    }
}
// Express middleware for handling async errors
export const asyncHandler = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
