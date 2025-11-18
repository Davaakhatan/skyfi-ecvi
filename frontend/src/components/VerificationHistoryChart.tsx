import { useMemo } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { format } from 'date-fns'
import type { VerificationResult } from '../types/api'

interface VerificationHistoryChartProps {
  history: VerificationResult[]
}

export default function VerificationHistoryChart({ history }: VerificationHistoryChartProps) {
  // Prepare data for charts - reverse to show oldest first
  const chartData = useMemo(() => {
    return [...history]
      .reverse()
      .map((result, index) => ({
        index: index + 1,
        date: format(new Date(result.created_at), 'MMM d, HH:mm'),
        fullDate: result.created_at,
        riskScore: result.risk_score,
        riskCategory: result.risk_category,
        status: result.verification_status,
        // Color mapping for risk categories
        riskColor:
          result.risk_category === 'HIGH'
            ? '#ef4444'
            : result.risk_category === 'MEDIUM'
            ? '#f59e0b'
            : '#10b981',
      }))
  }, [history])

  // Risk category counts
  const categoryCounts = useMemo(() => {
    const counts = { LOW: 0, MEDIUM: 0, HIGH: 0 }
    history.forEach((result) => {
      counts[result.risk_category]++
    })
    return [
      { category: 'Low', count: counts.LOW, color: '#10b981' },
      { category: 'Medium', count: counts.MEDIUM, color: '#f59e0b' },
      { category: 'High', count: counts.HIGH, color: '#ef4444' },
    ]
  }, [history])

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {entry.name === 'Risk Score' ? ' / 100' : ''}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  if (history.length < 2) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Risk Score Trend Line Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Risk Score Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis
              domain={[0, 100]}
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              label={{ value: 'Risk Score', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="riskScore"
              name="Risk Score"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
            />
            {/* Reference lines for risk thresholds */}
            <Line
              type="monotone"
              dataKey={() => 70}
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="High Risk Threshold"
              legendType="line"
            />
            <Line
              type="monotone"
              dataKey={() => 40}
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="Medium Risk Threshold"
              legendType="line"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Category Distribution Bar Chart */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Risk Category Distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={categoryCounts} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="category" stroke="#6b7280" fontSize={12} tick={{ fill: '#6b7280' }} />
            <YAxis stroke="#6b7280" fontSize={12} tick={{ fill: '#6b7280' }} />
            <Tooltip
              content={({ active, payload }: any) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                      <p className="text-sm font-medium text-gray-900">
                        {payload[0].payload.category} Risk: {payload[0].value} verification{payload[0].value !== 1 ? 's' : ''}
                      </p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Bar dataKey="count" name="Count" radius={[4, 4, 0, 0]}>
              {categoryCounts.map((entry, index) => (
                <Bar.Cell key={index} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Score Comparison (Side by side) */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Risk Score Comparison</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              domain={[0, 100]}
              stroke="#6b7280"
              fontSize={12}
              tick={{ fill: '#6b7280' }}
              label={{ value: 'Risk Score', angle: -90, position: 'insideLeft', style: { fill: '#6b7280' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="riskScore" name="Risk Score" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Bar.Cell key={`cell-${index}`} fill={entry.riskColor} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

