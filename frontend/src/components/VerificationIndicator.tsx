import { CheckCircle, AlertCircle, AlertTriangle, HelpCircle } from 'lucide-react'
import clsx from 'clsx'

export type VerificationStatus = 'verified' | 'partial' | 'discrepancy' | 'unknown'

interface VerificationIndicatorProps {
  status: VerificationStatus
  label: string
  tooltip?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function VerificationIndicator({
  status,
  label,
  tooltip,
  size = 'md',
}: VerificationIndicatorProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'verified':
        return {
          icon: CheckCircle,
          iconColor: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-700',
        }
      case 'partial':
        return {
          icon: AlertCircle,
          iconColor: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-700',
        }
      case 'discrepancy':
        return {
          icon: AlertTriangle,
          iconColor: 'text-red-600',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-700',
        }
      default:
        return {
          icon: HelpCircle,
          iconColor: 'text-gray-400',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-600',
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  const sizeClasses = {
    sm: {
      container: 'px-2 py-1',
      icon: 'w-3 h-3',
      text: 'text-xs',
    },
    md: {
      container: 'px-3 py-1.5',
      icon: 'w-4 h-4',
      text: 'text-sm',
    },
    lg: {
      container: 'px-4 py-2',
      icon: 'w-5 h-5',
      text: 'text-base',
    },
  }

  const sizeConfig = sizeClasses[size]

  return (
    <div
      className={clsx(
        'inline-flex items-center space-x-2 rounded-lg border transition-colors',
        config.bgColor,
        config.borderColor,
        sizeConfig.container
      )}
      title={tooltip || label}
    >
      <Icon className={clsx(config.iconColor, sizeConfig.icon)} />
      <span className={clsx('font-medium', config.textColor, sizeConfig.text)}>
        {label}
      </span>
    </div>
  )
}

