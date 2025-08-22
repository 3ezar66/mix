import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from './components/ui/toaster';
import { AuthProvider, useAuth } from './components/AuthProvider';
import { AdvancedLoadingScreen } from './components/AdvancedLoadingScreen';
import { AdvancedLoginForm } from './components/AdvancedLoginForm';
import Dashboard from './pages/dashboard';
import NotFound from './pages/not-found';
import './index.css';

// Create a client
const queryClient = new QueryClient();

function AppContent() {
  const { user, loginMutation } = useAuth();
  const [showLoading, setShowLoading] = useState(true);
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    // Show loading screen for 9 seconds
    const loadingTimer = setTimeout(() => {
      setShowLoading(false);
      if (!user) {
        setShowLogin(true);
      }
    }, 9000);

    return () => clearTimeout(loadingTimer);
  }, [user]);

  const handleLogin = async (username: string, password: string) => {
    try {
      await loginMutation.mutateAsync({ username, password });
      setShowLogin(false);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  // Show loading screen
  if (showLoading) {
    return <AdvancedLoadingScreen onComplete={() => setShowLoading(false)} />;
  }

  // Show login form if not authenticated
  if (showLogin && !user) {
    return <AdvancedLoginForm onLogin={handleLogin} />;
  }

  // Show dashboard if authenticated
  if (user) {
    return (
      <Router>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    );
  }

  return null;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div className="min-h-screen bg-black text-white">
          <AppContent />
          <Toaster />
        </div>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
