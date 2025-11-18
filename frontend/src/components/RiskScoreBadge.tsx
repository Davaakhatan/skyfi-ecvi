import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

interface RiskScoreBadgeProps {
  score: number
  category: 'LOW' | 'MEDIUM' | 'HIGH'
}

export default function RiskScoreBadge({ score, category }: RiskScoreBadgeProps) {
  const getCategoryStyles = () => {
    switch (category) {
      case 'LOW':
        return {
          bg: 'bg-green-50',
          text: 'text-green-700',
          border: 'border-green-200',
          icon: CheckCircle,
        }
      case 'MEDIUM':
        return {
          bg: 'bg-yellow-50',
          text: 'text-yellow-700',
          border: 'border-yellow-200',
          icon: AlertCircle,
        }
      case 'HIGH':
        return {
          bg: 'bg-red-50',
          text: 'text-red-700',
          border: 'border-red-200',
          icon: AlertTriangle,
        }
      default:
        return {
          bg: 'bg-gray-50',
          text: 'text-gray-700',
          border: 'border-gray-200',
          icon: AlertCircle,
        }
    }
  }

  const styles = getCategoryStyles()
  const Icon = styles.icon

  return (
    <div
      className={clsx(
        'flex items-center space-x-2 px-3 py-1.5 rounded-lg border',
        styles.bg,
        styles.text,
        styles.border
      )}
    >
      <Icon className="w-4 h-4" />
      <span className="text-sm font-semibold">{score}</span>
      <span className="text-xs capitalize">{category.toLowerCase()}</span>
    </div>
  )
}

