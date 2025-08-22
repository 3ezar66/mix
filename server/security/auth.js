import jwt from 'jsonwebtoken';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
export function verifyToken(request) {
    try {
        const token = request.headers.authorization?.split(' ')[1];
        if (!token)
            return null;
        const user = jwt.verify(token, JWT_SECRET);
        return user;
    }
    catch (error) {
        return null;
    }
}
export function generateToken(user) {
    return jwt.sign(user, JWT_SECRET, { expiresIn: '24h' });
}
