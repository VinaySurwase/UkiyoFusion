import { io, Socket } from 'socket.io-client'
import toast from 'react-hot-toast'

import type { TransformationProgress, SocketEvent } from '@/types'

class SocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  initialize(): void {
    if (this.socket?.connected) {
      return
    }

    const socketUrl = import.meta.env.VITE_WS_URL || window.location.origin
    
    this.socket = io(socketUrl, {
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      timeout: 20000,
    })

    this.setupEventListeners()
  }

  private setupEventListeners(): void {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      
      // Join authenticated user's room
      const authData = localStorage.getItem('auth-storage')
      if (authData) {
        try {
          const { state } = JSON.parse(authData)
          if (state?.user?.id) {
            this.socket?.emit('join_user_room', { user_id: state.user.id })
          }
        } catch (error) {
          console.error('Error parsing auth data for socket:', error)
        }
      }
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.reconnect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        toast.error('Failed to establish real-time connection')
      }
    })

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts')
      toast.success('Real-time connection restored')
    })

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed')
      toast.error('Failed to restore real-time connection')
    })

    // Listen for transformation progress updates
    this.socket.on('transformation_progress', (data: TransformationProgress) => {
      this.handleTransformationProgress(data)
    })

    // Listen for other app events
    this.socket.on('gallery_update', (data: any) => {
      this.handleGalleryUpdate(data)
    })

    this.socket.on('user_notification', (data: any) => {
      this.handleUserNotification(data)
    })
  }

  private handleTransformationProgress(data: TransformationProgress): void {
    // Emit custom event for components to listen to
    window.dispatchEvent(new CustomEvent('transformation_progress', {
      detail: data
    }))

    // Show toast notifications for important status changes
    if (data.status === 'completed') {
      toast.success('Transformation completed!')
    } else if (data.status === 'failed') {
      toast.error(`Transformation failed: ${data.message}`)
    }
  }

  private handleGalleryUpdate(data: any): void {
    // Emit custom event for gallery components
    window.dispatchEvent(new CustomEvent('gallery_update', {
      detail: data
    }))
  }

  private handleUserNotification(data: any): void {
    // Show user notifications
    if (data.type === 'info') {
      toast(data.message)
    } else if (data.type === 'success') {
      toast.success(data.message)
    } else if (data.type === 'warning') {
      toast(data.message, { icon: '⚠️' })
    } else if (data.type === 'error') {
      toast.error(data.message)
    }
  }

  joinTaskRoom(taskId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('join_room', { room: `task_${taskId}` })
    }
  }

  leaveTaskRoom(taskId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('leave_room', { room: `task_${taskId}` })
    }
  }

  emit(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }

  on(event: string, callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event: string, callback?: (data: any) => void): void {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  private reconnect(): void {
    setTimeout(() => {
      if (this.socket && !this.socket.connected) {
        this.socket.connect()
      }
    }, this.reconnectDelay)
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false
  }
}

// Create singleton instance
const socketService = new SocketService()

// Export utility functions
export const initializeSocket = (): void => {
  socketService.initialize()
}

export const disconnectSocket = (): void => {
  socketService.disconnect()
}

export const joinTaskRoom = (taskId: string): void => {
  socketService.joinTaskRoom(taskId)
}

export const leaveTaskRoom = (taskId: string): void => {
  socketService.leaveTaskRoom(taskId)
}

export const emitSocketEvent = (event: string, data: any): void => {
  socketService.emit(event, data)
}

export const onSocketEvent = (event: string, callback: (data: any) => void): void => {
  socketService.on(event, callback)
}

export const offSocketEvent = (event: string, callback?: (data: any) => void): void => {
  socketService.off(event, callback)
}

export const isSocketConnected = (): boolean => {
  return socketService.isConnected()
}

// Hook for React components to listen to transformation progress
export const useTransformationProgress = (
  taskId: string,
  onProgress: (data: TransformationProgress) => void
): void => {
  React.useEffect(() => {
    const handleProgress = (event: CustomEvent<TransformationProgress>) => {
      if (event.detail.task_id === taskId) {
        onProgress(event.detail)
      }
    }

    // Join the specific task room
    joinTaskRoom(taskId)

    // Listen for progress events
    window.addEventListener('transformation_progress', handleProgress as EventListener)

    return () => {
      // Leave the task room
      leaveTaskRoom(taskId)
      
      // Remove event listener
      window.removeEventListener('transformation_progress', handleProgress as EventListener)
    }
  }, [taskId, onProgress])
}

export default socketService
