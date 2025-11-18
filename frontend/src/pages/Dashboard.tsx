import { useEffect, useState } from 'react'
import api from '../services/api'
import { Building2, AlertTriangle, CheckCircle2, Clock } from 'lucide-react'
import type { CompanyListResponse } from '../types/api'

interface DashboardStats {
  total_companies: number
  verified_companies: number
  pending_verifications: number
  high_risk_companies: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch dashboard stats
    // For now, we'll use a placeholder. In production, create a dedicated endpoint
    const fetchStats = async () => {
      try {
        const response = await api.get<CompanyListResponse>('/companies/', { params: { limit: 1 } })
        const total = response.data.total || 0
        // Placeholder stats - replace with actual endpoint
        setStats({
          total_companies: total,
          verified_companies: Math.floor(total * 0.7),
          pending_verifications: Math.floor(total * 0.15),
          high_risk_companies: Math.floor(total * 0.1),
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    {
      title: 'Total Companies',
      value: stats?.total_companies || 0,
      icon: Building2,
      color: 'bg-blue-500',
    },
    {
      title: 'Verified',
      value: stats?.verified_companies || 0,
      icon: CheckCircle2,
      color: 'bg-green-500',
    },
    {
      title: 'Pending',
      value: stats?.pending_verifications || 0,
      icon: Clock,
      color: 'bg-yellow-500',
    },
    {
      title: 'High Risk',
      value: stats?.high_risk_companies || 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your company verifications</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.title}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/companies"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Building2 className="w-5 h-5 text-primary-600" />
            <span className="font-medium text-gray-900">View All Companies</span>
          </a>
        </div>
      </div>
    </div>
  )
}

