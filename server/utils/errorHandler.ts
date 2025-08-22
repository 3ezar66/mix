import { Logger } from './logger';
import { Request, Response, NextFunction } from 'express';

interface ErrorResponse {
    status: number;
    message: string;
    code?: string;
    details?: any;
}

export class AppError extends Error {
    public readonly status: number;
    public readonly code: string;
    public readonly details?: any;

    constructor(message: string, status: number = 500, code: string = 'INTERNAL_ERROR', details?: any) {
        super(message);
        this.status = status;
        this.code = code;
        this.details = details;
        Error.captureStackTrace(this, this.constructor);
    }
}

export class ErrorHandler {
    private static logger = Logger.getInstance('ErrorHandler');

    public static handleError(err: Error, req: Request, res: Response, next: NextFunction): void {
        let errorResponse: ErrorResponse;

        if (err instanceof AppError) {
            errorResponse = {
                status: err.status,
                message: err.message,
                code: err.code,
                details: err.details
            };
        } else {
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
            userId: (req as any).user?.id,
            requestId: req.headers['x-request-id'],
            body: req.body,
            query: req.query
        });

        // Send error response
        res.status(errorResponse.status).json(errorResponse);
    }

    public static handleUncaughtException(err: Error): void {
        this.logger.error('Uncaught Exception', { error: err });
        process.exit(1);
    }

    public static handleUnhandledRejection(reason: any): void {
        this.logger.error('Unhandled Rejection', { error: reason });
        process.exit(1);
    }

    // Custom error types
    public static notFound(message: string = 'Resource not found'): AppError {
        return new AppError(message, 404, 'NOT_FOUND');
    }

    public static badRequest(message: string, details?: any): AppError {
        return new AppError(message, 400, 'BAD_REQUEST', details);
    }

    public static unauthorized(message: string = 'Unauthorized'): AppError {
        return new AppError(message, 401, 'UNAUTHORIZED');
    }

    public static forbidden(message: string = 'Forbidden'): AppError {
        return new AppError(message, 403, 'FORBIDDEN');
    }

    public static validation(message: string, details: any): AppError {
        return new AppError(message, 422, 'VALIDATION_ERROR', details);
    }

    public static tooManyRequests(message: string = 'Too many requests'): AppError {
        return new AppError(message, 429, 'TOO_MANY_REQUESTS');
    }
}

// Express middleware for handling async errors
export const asyncHandler = (fn: (req: Request, res: Response, next: NextFunction) => Promise<any>) => {
    return (req: Request, res: Response, next: NextFunction) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};