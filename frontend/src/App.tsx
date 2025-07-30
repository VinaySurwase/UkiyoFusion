import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

// Store
import { useAuthStore } from '@/store/authStore'

// Components
import Layout from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'

// Pages
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import TransformPage from '@/pages/TransformPage'
import GalleryPage from '@/pages/GalleryPage'
import ProfilePage from '@/pages/ProfilePage'
import PublicGalleryPage from '@/pages/PublicGalleryPage'
import NotFoundPage from '@/pages/NotFoundPage'

// Services
import { initializeSocket } from '@/services/socketService'

function App() {
  const { user, checkAuth, isLoading } = useAuthStore()

  useEffect(() => {
    // Check authentication status on app load
    checkAuth()
    
    // Initialize WebSocket connection if user is authenticated
    if (user) {
      initializeSocket()
    }
  }, [checkAuth, user])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-lg font-medium text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
        <Route path="register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
        <Route path="gallery/public" element={<PublicGalleryPage />} />
        <Route path="gallery/share/:shareToken" element={<PublicGalleryPage />} />
        
        {/* Protected routes */}
        <Route path="dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        <Route path="transform" element={
          <ProtectedRoute>
            <TransformPage />
          </ProtectedRoute>
        } />
        <Route path="gallery" element={
          <ProtectedRoute>
            <GalleryPage />
          </ProtectedRoute>
        } />
        <Route path="profile" element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        } />
        
        {/* 404 page */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
