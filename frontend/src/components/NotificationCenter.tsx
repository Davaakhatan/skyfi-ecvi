import { useState, useEffect, useRef } from 'react'
import { Bell, X, CheckCircle, AlertCircle, Info, AlertTriangle, CheckCheck } from 'lucide-react'
import { useNotificationStore, type Notification } from '../store/notificationStore'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'

export default function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { notifications, unreadCount, markAsRead, markAllAsRead, removeNotification } =
    useNotificationStore()

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return CheckCircle
      case 'error':
        return AlertCircle
      case 'warning':
        return AlertTriangle
      default:
        return Info
    }
  }

  const getIconColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-600'
      case 'error':
        return 'text-red-600'
      case 'warning':
        return 'text-yellow-600'
      default:
        return 'text-blue-600'
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id)
    }
    setIsOpen(false)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-red-600 rounded-full">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border border-gray-200 z-50 max-h-[600px] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="p-1.5 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  title="Mark all as read"
                >
                  <CheckCheck className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-sm text-gray-500">No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification: Notification) => {
                  const Icon = getIcon(notification.type)
                  const iconColor = getIconColor(notification.type)
                  const content = notification.actionUrl ? (
                    <Link
                      to={notification.actionUrl}
                      onClick={() => handleNotificationClick(notification)}
                      className="block"
                    >
                      <NotificationItem notification={notification} Icon={Icon} iconColor={iconColor} />
                    </Link>
                  ) : (
                    <div onClick={() => handleNotificationClick(notification)}>
                      <NotificationItem notification={notification} Icon={Icon} iconColor={iconColor} />
                    </div>
                  )

                  return (
                    <div
                      key={notification.id}
                      className={clsx(
                        'relative transition-colors',
                        !notification.read && 'bg-primary-50',
                        notification.actionUrl && 'hover:bg-gray-50 cursor-pointer'
                      )}
                    >
                      {content}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          removeNotification(notification.id)
                        }}
                        className="absolute top-2 right-2 p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                        title="Remove notification"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function NotificationItem({
  notification,
  Icon,
  iconColor,
}: {
  notification: Notification
  Icon: LucideIcon
  iconColor: string
}) {

  return (
    <div className="p-4">
      <div className="flex items-start space-x-3">
        <div className={clsx('flex-shrink-0 mt-0.5', iconColor)}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{notification.title}</p>
              <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
              {notification.companyName && (
                <p className="text-xs text-gray-500 mt-1">Company: {notification.companyName}</p>
              )}
              <p className="text-xs text-gray-400 mt-2">
                {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
              </p>
            </div>
            {!notification.read && (
              <div className="ml-2 flex-shrink-0">
                <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

