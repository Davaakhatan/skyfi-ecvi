import { CheckCircle, AlertCircle, Clock } from 'lucide-react'
import clsx from 'clsx'
import type { ReviewStatus } from '../types/api'

interface ReviewStatusBadgeProps {
  status: ReviewStatus
  size?: 'sm' | 'md' | 'lg'
}

export default function ReviewStatusBadge({ status, size = 'md' }: ReviewStatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'REVIEWED':
        return {
          icon: CheckCircle,
          iconColor: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-700',
          label: 'Reviewed',
        }
      case 'FLAGGED':
        return {
          icon: AlertCircle,
          iconColor: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-700',
          label: 'Flagged',
        }
      default:
        return {
          icon: Clock,
          iconColor: 'text-gray-400',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-600',
          label: 'Pending',
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  const sizeClasses = {
    sm: {
      container: 'px-2 py-0.5',
      icon: 'w-3 h-3',
      text: 'text-xs',
    },
    md: {
      container: 'px-2.5 py-1',
      icon: 'w-4 h-4',
      text: 'text-xs',
    },
    lg: {
      container: 'px-3 py-1.5',
      icon: 'w-5 h-5',
      text: 'text-sm',
    },
  }

  const sizeConfig = sizeClasses[size]

  return (
    <div
      className={clsx(
        'inline-flex items-center space-x-1.5 rounded-lg border',
        config.bgColor,
        config.borderColor,
        sizeConfig.container
      )}
    >
      <Icon className={clsx(config.iconColor, sizeConfig.icon)} />
      <span className={clsx('font-medium', config.textColor, sizeConfig.text)}>
        {config.label}
      </span>
    </div>
  )
}

