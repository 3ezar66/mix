import React, { useState, useEffect } from 'react';
import '../styles/auth.css';
import { useAuth } from '@/components/AuthProvider';
import { useLocation } from 'wouter';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Shield, Cpu, Radio, Eye, EyeOff, Lock, User } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AuthPage() {
  const { user, loginMutation, registerMutation } = useAuth();
  const [, setLocation] = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [captcha, setCaptcha] = useState({ question: '', answer: 0, userAnswer: '' });
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Generate random captcha
  const generateCaptcha = () => {
    const num1 = Math.floor(Math.random() * 10) + 1;
    const num2 = Math.floor(Math.random() * 10) + 1;
    const operators = ['+', '-', '*'];
    const operator = operators[Math.floor(Math.random() * operators.length)];
    
    let answer;
    let question;
    
    switch (operator) {
      case '+':
        answer = num1 + num2;
        question = `${num1} + ${num2}`;
        break;
      case '-':
        answer = num1 - num2;
        question = `${num1} - ${num2}`;
        break;
      case '*':
        answer = num1 * num2;
        question = `${num1} × ${num2}`;
        break;
      default:
        answer = num1 + num2;
        question = `${num1} + ${num2}`;
    }
    
    setCaptcha({ question, answer, userAnswer: '' });
  };

  // Initialize captcha on component mount
  useEffect(() => {
    generateCaptcha();
  }, []);

  // Redirect if already logged in
  if (user) {
    setLocation('/');
    return null;
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate captcha
    if (parseInt(captcha.userAnswer) !== captcha.answer) {
      alert('کپچا نادرست است. لطفاً دوباره تلاش کنید.');
      generateCaptcha();
      return;
    }
    
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();
      localStorage.setItem('token', data.token);
      setLocation('/dashboard');
    } catch (err) {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-persian-surface to-background flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0 auth-background" />
      </div>

      <div className="relative z-10 w-full max-w-6xl mx-auto grid lg:grid-cols-2 gap-8 items-center">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center lg:text-right space-y-6"
        >
          {/* Logo */}
          <div className="flex justify-center lg:justify-end mb-8">
            <div className="relative">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="w-32 h-32 border-4 border-transparent border-t-primary border-r-persian-secondary rounded-full"
              />
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                className="absolute inset-4 border-2 border-transparent border-b-persian-accent border-l-persian-warning rounded-full"
              />
              <div className="absolute inset-8 bg-primary rounded-full flex items-center justify-center">
                <Shield className="w-12 h-12 text-white" />
              </div>
            </div>
          </div>

          <h1 className="text-4xl lg:text-5xl font-bold text-foreground leading-tight">
            <span className="text-primary">شبح حبشی</span>
            <br />
            <span className="text-muted-foreground text-2xl">سیستم شناسایی ماینر</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-lg mx-auto lg:mx-0">
            سیستم پیشرفته تشخیص و ردیابی دستگاه‌های استخراج ارز دیجیتال با استفاده از 
            تکنولوژی‌های نوین تحلیل RF و شبکه
          </p>

          <div className="space-y-4">
            <div className="flex items-center justify-center lg:justify-end space-x-reverse space-x-4">
              <div className="flex items-center space-x-reverse space-x-2">
                <Radio className="w-5 h-5 text-primary" />
                <span className="text-muted-foreground">تحلیل امواج رادیویی</span>
              </div>
              <div className="flex items-center space-x-reverse space-x-2">
                <Cpu className="w-5 h-5 text-persian-secondary" />
                <span className="text-muted-foreground">شناسایی هوشمند</span>
              </div>
            </div>

            <div className="text-center lg:text-right">
              <div className="inline-flex items-center px-4 py-2 bg-persian-surface-variant rounded-full text-sm">
                <div className="w-2 h-2 bg-persian-success rounded-full animate-pulse ml-2" />
                ویژه استان ایلام • جمهوری اسلامی ایران
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-persian-surface-variant/50 rounded-lg text-center"
            >
              <Radio className="w-8 h-8 text-primary mx-auto mb-2" />
              <h3 className="font-semibold text-foreground">تحلیل RF</h3>
              <p className="text-xs text-muted-foreground">شناسایی از طریق امواج مغناطیسی</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-persian-surface-variant/50 rounded-lg text-center"
            >
              <Cpu className="w-8 h-8 text-persian-secondary mx-auto mb-2" />
              <h3 className="font-semibold text-foreground">تشخیص هوشمند</h3>
              <p className="text-xs text-muted-foreground">الگوریتم‌های پیشرفته ML</p>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.05 }}
              className="p-4 bg-persian-surface-variant/50 rounded-lg text-center"
            >
              <Shield className="w-8 h-8 text-persian-accent mx-auto mb-2" />
              <h3 className="font-semibold text-foreground">امنیت بالا</h3>
              <p className="text-xs text-muted-foreground">احراز هویت دو مرحله‌ای</p>
            </motion.div>
          </div>
        </motion.div>

        {/* Auth Form */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-full max-w-md mx-auto"
        >
          <Card className="persian-card">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl text-foreground">
                ورود مدیر سیستم
              </CardTitle>
              <p className="text-muted-foreground">
                ورود اختصاصی برای مدیران سیستم شبح حبشی
              </p>
            </CardHeader>

            <CardContent>
              <div className="space-y-4">
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="login-username">نام کاربری</Label>
                      <div className="relative">
                        <User className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="login-username"
                          type="text"
                          placeholder=""
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          className="pr-10 focus-ring"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="login-password">رمز عبور</Label>
                      <div className="relative">
                        <Lock className="absolute right-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="login-password"
                          type={showPassword ? "text" : "password"}
                          placeholder=""
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          className="pr-10 pl-10 focus-ring"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute left-3 top-3 h-4 w-4 text-muted-foreground hover:text-foreground transition-colors"
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="captcha">تأیید انسان بودن</Label>
                      <div className="flex items-center space-x-reverse space-x-2">
                        <div className="flex-1">
                          <Input
                            id="captcha"
                            type="number"
                            placeholder="جواب را وارد کنید"
                            value={captcha.userAnswer}
                            onChange={(e) => setCaptcha(prev => ({ ...prev, userAnswer: e.target.value }))}
                            className="focus-ring"
                            required
                          />
                        </div>
                        <div className="bg-persian-surface-variant px-4 py-2 rounded-lg border min-w-[120px] text-center">
                          <span className="font-mono text-lg text-foreground">{captcha.question} = ?</span>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={generateCaptcha}
                          className="px-3"
                        >
                          🔄
                        </Button>
                      </div>
                    </div>

                    {error && (
                      <Alert variant="destructive">
                        <AlertDescription>{error}</AlertDescription>
                      </Alert>
                    )}

                    <Button 
                      type="submit" 
                      className="w-full bg-primary hover:bg-blue-600 focus-ring"
                      disabled={loginMutation.isPending}
                    >
                      {loginMutation.isPending ? "در حال ورود..." : "ورود به سیستم"}
                    </Button>
                  </form>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
      <footer className="text-center text-muted-foreground text-sm mt-4">
        © 2024 Erfan-Rajabee. All rights reserved. بهار 1404
      </footer>
    </div>
  );
}