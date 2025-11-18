import { describe, it, expect, beforeEach } from 'vitest'
import { useNotificationStore } from '../notificationStore'

describe('notificationStore', () => {
  beforeEach(() => {
    // Clear all notifications before each test
    useNotificationStore.getState().clearAll()
  })

  it('initializes with empty notifications', () => {
    const state = useNotificationStore.getState()
    expect(state.notifications).toEqual([])
    expect(state.unreadCount).toBe(0)
  })

  it('adds notification correctly', () => {
    useNotificationStore.getState().addNotification({
      type: 'success',
      title: 'Test Title',
      message: 'Test Message',
    })

    const state = useNotificationStore.getState()
    expect(state.notifications).toHaveLength(1)
    expect(state.notifications[0].title).toBe('Test Title')
    expect(state.unreadCount).toBe(1)
  })

  it('marks notification as read', () => {
    // Add notification
    useNotificationStore.getState().addNotification({
      type: 'info',
      title: 'Test',
      message: 'Message',
    })

    const state1 = useNotificationStore.getState()
    const notificationId = state1.notifications[0].id

    // Mark as read
    useNotificationStore.getState().markAsRead(notificationId)

    const state2 = useNotificationStore.getState()
    expect(state2.notifications[0].read).toBe(true)
    expect(state2.unreadCount).toBe(0)
  })

  it('removes notification', () => {
    // Add notification
    useNotificationStore.getState().addNotification({
      type: 'warning',
      title: 'Test',
      message: 'Message',
    })

    const state1 = useNotificationStore.getState()
    const notificationId = state1.notifications[0].id

    // Remove notification
    useNotificationStore.getState().removeNotification(notificationId)

    const state2 = useNotificationStore.getState()
    expect(state2.notifications).toHaveLength(0)
  })

  it('marks all notifications as read', () => {
    // Add multiple notifications
    useNotificationStore.getState().addNotification({
      type: 'info',
      title: 'Test 1',
      message: 'Message 1',
    })
    useNotificationStore.getState().addNotification({
      type: 'info',
      title: 'Test 2',
      message: 'Message 2',
    })

    // Mark all as read
    useNotificationStore.getState().markAllAsRead()

    const state = useNotificationStore.getState()
    expect(state.unreadCount).toBe(0)
    expect(state.notifications.every(n => n.read)).toBe(true)
  })

  it('limits notifications to 50', () => {
    // Add 55 notifications
    for (let i = 0; i < 55; i++) {
      useNotificationStore.getState().addNotification({
        type: 'info',
        title: `Test ${i}`,
        message: `Message ${i}`,
      })
    }

    const state = useNotificationStore.getState()
    expect(state.notifications).toHaveLength(50)
  })
})

