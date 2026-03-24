import React from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-6">
        <Outlet />
      </main>
    </div>
  )
}
