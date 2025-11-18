import { useState } from 'react'
import { ChevronDown, ChevronUp, CheckCircle, AlertCircle, AlertTriangle } from 'lucide-react'
import VerificationIndicator, { VerificationStatus } from './VerificationIndicator'

interface VerificationDetailsProps {
  data: {
    field: string
    value: string
    status: VerificationStatus
    confidence?: number
    sources?: number
    matches?: number
    discrepancies?: Array<{
      source: string
      value: string
      type: string
    }>
  }[]
}

export default function VerificationDetails({ data }: VerificationDetailsProps) {
  const [expandedFields, setExpandedFields] = useState<Set<string>>(new Set())

  const toggleField = (field: string) => {
    const newExpanded = new Set(expandedFields)
    if (newExpanded.has(field)) {
      newExpanded.delete(field)
    } else {
      newExpanded.add(field)
    }
    setExpandedFields(newExpanded)
  }

  const getStatusIcon = (status: VerificationStatus) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'partial':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />
      case 'discrepancy':
        return <AlertTriangle className="w-4 h-4 text-red-600" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-3">
      {data.map((item) => {
        const isExpanded = expandedFields.has(item.field)
        const hasDetails = item.discrepancies && item.discrepancies.length > 0

        return (
          <div
            key={item.field}
            className="border border-gray-200 rounded-lg overflow-hidden bg-white"
          >
            <button
              onClick={() => hasDetails && toggleField(item.field)}
              className={`
                w-full px-4 py-3 flex items-center justify-between
                hover:bg-gray-50 transition-colors
                ${hasDetails ? 'cursor-pointer' : 'cursor-default'}
              `}
            >
              <div className="flex items-center space-x-3 flex-1 min-w-0">
                {getStatusIcon(item.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {item.field.replace('_', ' ')}
                    </span>
                    <VerificationIndicator status={item.status} label="" size="sm" />
                  </div>
                  <p className="text-sm text-gray-600 mt-1 truncate">{item.value}</p>
                  {item.confidence !== undefined && (
                    <p className="text-xs text-gray-500 mt-1">
                      Confidence: {Math.round(item.confidence * 100)}%
                      {item.sources && ` • ${item.sources} sources`}
                      {item.matches !== undefined && ` • ${item.matches} matches`}
                    </p>
                  )}
                </div>
              </div>
              {hasDetails && (
                <div className="ml-4">
                  {isExpanded ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              )}
            </button>

            {isExpanded && hasDetails && item.discrepancies && (
              <div className="px-4 pb-4 border-t border-gray-200 bg-gray-50">
                <div className="mt-3 space-y-2">
                  <p className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                    Discrepancies Found
                  </p>
                  {item.discrepancies.map((disc, idx) => (
                    <div
                      key={idx}
                      className="bg-white rounded border border-red-200 p-3"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-xs font-medium text-red-700">
                            {disc.source}
                          </p>
                          <p className="text-sm text-gray-900 mt-1">{disc.value}</p>
                          <p className="text-xs text-gray-500 mt-1 capitalize">
                            Type: {disc.type.replace('_', ' ')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

