import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '../../test/utils/test-utils'
import userEvent from '@testing-library/user-event'
import NotificationCenter from '../NotificationCenter'
import { useNotificationStore } from '../../store/notificationStore'

describe('NotificationCenter', () => {
  beforeEach(() => {
    // Clear notifications before each test
    useNotificationStore.getState().clearAll()
  })

  it('renders bell icon', () => {
    render(<NotificationCenter />)
    const bell = screen.getByLabelText(/notifications/i)
    expect(bell).toBeInTheDocument()
  })

  it('shows unread count badge', () => {
    // Add unread notifications
    useNotificationStore.getState().addNotification({
      type: 'info',
      title: 'Test',
      message: 'Message',
    })
    
    render(<NotificationCenter />)
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('opens dropdown when clicked', async () => {
    const user = userEvent.setup()
    
    // Add notification
    useNotificationStore.getState().addNotification({
      type: 'success',
      title: 'Test Notification',
      message: 'Test message',
    })
    
    render(<NotificationCenter />)
    
    const bell = screen.getByLabelText(/notifications/i)
    await user.click(bell)
    
    expect(screen.getByText('Test Notification')).toBeInTheDocument()
  })

  it('displays empty state when no notifications', async () => {
    const user = userEvent.setup()
    render(<NotificationCenter />)
    
    const bell = screen.getByLabelText(/notifications/i)
    await user.click(bell)
    
    expect(screen.getByText(/no notifications/i)).toBeInTheDocument()
  })

  it('marks notification as read when clicked', async () => {
    const user = userEvent.setup()
    
    // Add notification
    useNotificationStore.getState().addNotification({
      type: 'info',
      title: 'Test',
      message: 'Message',
    })
    
    render(<NotificationCenter />)
    
    const bell = screen.getByLabelText(/notifications/i)
    await user.click(bell)
    
    const notification = screen.getByText('Test')
    await user.click(notification)
    
    // Unread count should decrease
    const state = useNotificationStore.getState()
    expect(state.unreadCount).toBe(0)
  })
})

