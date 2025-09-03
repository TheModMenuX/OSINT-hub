import { jwtVerify, SignJWT } from 'jose';
import { cookies } from 'next/headers';

const SECRET_KEY = new TextEncoder().encode(process.env.JWT_SECRET_KEY);

export async function signIn(username: string, password: string) {
  // In production, verify against secure database
  if (username === 'mgthi555-ai' && password === 'secure_password') {
    const token = await new SignJWT({ username })
      .setProtectedHeader({ alg: 'HS256' })
      .setExpirationTime('24h')
      .sign(SECRET_KEY);
    
    cookies().set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 86400 // 24 hours
    });
    
    return { success: true, username };
  }
  return { success: false, error: 'Invalid credentials' };
}