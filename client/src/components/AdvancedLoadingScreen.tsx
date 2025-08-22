import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Search, 
  Network, 
  Cpu, 
  HardDrive, 
  Zap,
  Eye,
  Target,
  Lock,
  Globe,
  Satellite,
  Radio,
  Wifi,
  Database,
  BarChart3,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  MapPin,
  Brain
} from 'lucide-react';

interface LoadingScreenProps {
  onComplete: () => void;
}

interface LoadingStep {
  id: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  progress: number;
}

export const AdvancedLoadingScreen: React.FC<LoadingScreenProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [showLogo, setShowLogo] = useState(false);
  const [showParticles, setShowParticles] = useState(false);
  const [showGrid, setShowGrid] = useState(false);
  const [showScanLines, setShowScanLines] = useState(false);
  const [showHologram, setShowHologram] = useState(false);
  
  const loadingSteps: LoadingStep[] = [
    {
      id: 1,
      title: "راه‌اندازی سیستم",
      description: "بارگذاری هسته اصلی سیستم تشخیص ماینینگ",
      icon: <Cpu className="w-8 h-8" />,
      progress: 10
    },
    {
      id: 2,
      title: "اتصال به شبکه",
      description: "برقراری ارتباط با سرورهای مرکزی",
      icon: <Network className="w-8 h-8" />,
      progress: 25
    },
    {
      id: 3,
      title: "فعال‌سازی ماژول‌های تشخیص",
      description: "راه‌اندازی سیستم‌های RF، صوتی و حرارتی",
      icon: <Radio className="w-8 h-8" />,
      progress: 40
    },
    {
      id: 4,
      title: "بارگذاری نقشه‌های جغرافیایی",
      description: "آماده‌سازی سیستم موقعیت‌یابی دقیق",
      icon: <MapPin className="w-8 h-8" />,
      progress: 55
    },
    {
      id: 5,
      title: "فعال‌سازی هوش مصنوعی",
      description: "راه‌اندازی مدل‌های ML و تحلیل پیشرفته",
      icon: <Cpu className="w-8 h-8" />,
      progress: 70
    },
    {
      id: 6,
      title: "اتصال به بلاکچین",
      description: "برقراری ارتباط با شبکه‌های رمزارز",
      icon: <Globe className="w-8 h-8" />,
      progress: 85
    },
    {
      id: 7,
      title: "آماده‌سازی داشبورد",
      description: "راه‌اندازی رابط کاربری پیشرفته",
      icon: <BarChart3 className="w-8 h-8" />,
      progress: 95
    },
    {
      id: 8,
      title: "سیستم آماده",
      description: "تمام ماژول‌ها فعال و آماده خدمت",
      icon: <CheckCircle className="w-8 h-8" />,
      progress: 100
    }
  ];

  useEffect(() => {
    // شروع انیمیشن‌ها
    const timer = setTimeout(() => setShowLogo(true), 500);
    const particlesTimer = setTimeout(() => setShowParticles(true), 1000);
    const gridTimer = setTimeout(() => setShowGrid(true), 1500);
    const scanTimer = setTimeout(() => setShowScanLines(true), 2000);
    const hologramTimer = setTimeout(() => setShowHologram(true), 2500);

    return () => {
      clearTimeout(timer);
      clearTimeout(particlesTimer);
      clearTimeout(gridTimer);
      clearTimeout(scanTimer);
      clearTimeout(hologramTimer);
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(onComplete, 1000);
          return 100;
        }
        return prev + 1.11; // 100% در 9 ثانیه
      });
    }, 100);

    return () => clearInterval(interval);
  }, [onComplete]);

  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= loadingSteps.length - 1) {
          clearInterval(stepInterval);
          return prev;
        }
        return prev + 1;
      });
    }, 1125); // 9 ثانیه تقسیم بر 8 مرحله

    return () => clearInterval(stepInterval);
  }, []);

  const Brain = ({ className }: { className?: string }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44A2.5 2.5 0 0 1 4.5 17v-1.5A2.5 2.5 0 0 1 2 13.5V11a2.5 2.5 0 0 1 2.5-2.5H7a2.5 2.5 0 0 1 2.5-2.5Z"/>
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44A2.5 2.5 0 0 0 19.5 17v-1.5A2.5 2.5 0 0 0 22 13.5V11a2.5 2.5 0 0 0-2.5-2.5H17a2.5 2.5 0 0 0-2.5-2.5Z"/>
    </svg>
  );

  return (
    <div className="fixed inset-0 bg-black z-50 overflow-hidden">
      {/* Background Grid */}
      <AnimatePresence>
        {showGrid && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.1 }}
            transition={{ duration: 1 }}
            className="absolute inset-0"
            style={{
              backgroundImage: `
                linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)
              `,
              backgroundSize: '50px 50px'
            }}
          />
        )}
      </AnimatePresence>

      {/* Scan Lines */}
      <AnimatePresence>
        {showScanLines && (
          <motion.div
            initial={{ y: -100 }}
            animate={{ y: '100vh' }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0 pointer-events-none"
          >
            <div className="h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-30" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Particles */}
      <AnimatePresence>
        {showParticles && (
          <div className="absolute inset-0 pointer-events-none">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                initial={{ 
                  x: Math.random() * window.innerWidth,
                  y: Math.random() * window.innerHeight,
                  opacity: 0
                }}
                animate={{
                  x: Math.random() * window.innerWidth,
                  y: Math.random() * window.innerHeight,
                  opacity: [0, 1, 0]
                }}
                transition={{
                  duration: Math.random() * 3 + 2,
                  repeat: Infinity,
                  ease: 'linear'
                }}
                className="absolute w-1 h-1 bg-cyan-400 rounded-full"
              />
            ))}
          </div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full">
        
        {/* Logo Section */}
        <AnimatePresence>
          {showLogo && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 1, type: 'spring' }}
              className="text-center mb-8"
            >
              <div className="relative">
                {/* Main Logo */}
                <motion.div
                  animate={{ 
                    boxShadow: [
                      '0 0 20px rgba(0, 255, 255, 0.5)',
                      '0 0 40px rgba(0, 255, 255, 0.8)',
                      '0 0 20px rgba(0, 255, 255, 0.5)'
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block p-6 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600"
                >
                  <Shield className="w-16 h-16 text-white" />
                </motion.div>
                
                {/* Logo Text */}
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                  className="mt-4"
                >
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                    کاشف
                  </h1>
                  <p className="text-lg text-gray-300 mt-2">نسخه شبح حبشی</p>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Hologram Effect */}
        <AnimatePresence>
          {showHologram && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1 }}
              className="absolute inset-0 flex items-center justify-center pointer-events-none"
            >
              <div className="relative">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                  className="w-96 h-96 border border-cyan-400 rounded-full opacity-20"
                />
                <motion.div
                  animate={{ rotate: -360 }}
                  transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-4 border border-blue-400 rounded-full opacity-30"
                />
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-8 border border-purple-400 rounded-full opacity-20"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading Progress */}
        <div className="relative z-20 w-full max-w-2xl px-8">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-300 mb-2">
              <span>پیشرفت سیستم</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="relative h-3 bg-gray-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.1 }}
                className="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 rounded-full"
                style={{
                  boxShadow: '0 0 20px rgba(0, 255, 255, 0.5)',
                  background: 'linear-gradient(90deg, #00ffff, #0080ff, #8000ff)'
                }}
              />
              <motion.div
                animate={{ x: ['0%', '100%'] }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30"
              />
            </div>
          </div>

          {/* Current Step */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
              className="text-center"
            >
              <div className="flex items-center justify-center mb-4">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="mr-3 text-cyan-400"
                >
                  {loadingSteps[currentStep]?.icon}
                </motion.div>
                <h3 className="text-xl font-semibold text-white">
                  {loadingSteps[currentStep]?.title}
                </h3>
              </div>
              <p className="text-gray-400">
                {loadingSteps[currentStep]?.description}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 1 }}
          className="absolute bottom-8 left-8 text-sm text-gray-400"
        >
          <div className="flex items-center space-x-4 space-x-reverse">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse" />
              <span>سیستم فعال</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse" />
              <span>اتصال برقرار</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse" />
              <span>امنیت فعال</span>
            </div>
          </div>
        </motion.div>

        {/* Version Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 3, duration: 1 }}
          className="absolute bottom-8 right-8 text-sm text-gray-500"
        >
          <div>نسخه 2.0.0 - سیستم ملی تشخیص ماینینگ غیرمجاز</div>
          <div>وزارت نیرو - شرکت توانیر - استان ایلام</div>
        </motion.div>
      </div>
    </div>
  );
};