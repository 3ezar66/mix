import jwt from 'jsonwebtoken';
import { FastifyRequest } from 'fastify';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

export interface AuthUser {
  id: number;
  username: string;
  role: string;
}

export function verifyToken(request: FastifyRequest): AuthUser | null {
  try {
    const token = request.headers.authorization?.split(' ')[1];
    if (!token) return null;

    const user = jwt.verify(token, JWT_SECRET) as AuthUser;
    return user;
  } catch (error) {
    return null;
  }
}

export function generateToken(user: AuthUser): string {
  return jwt.sign(user, JWT_SECRET, { expiresIn: '24h' });
}
