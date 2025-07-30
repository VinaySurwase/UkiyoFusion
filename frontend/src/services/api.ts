import axios, { AxiosResponse, AxiosError } from 'axios'
import toast from 'react-hot-toast'

import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  Transformation,
  TransformationRequest,
  GalleryItem,
  GalleryItemCreate,
  ModelConfig,
  ApiResponse,
  PaginatedResponse,
  SearchFilters,
} from '@/types'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authData = localStorage.getItem('auth-storage')
    if (authData) {
      try {
        const { state } = JSON.parse(authData)
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`
        }
      } catch (error) {
        console.error('Error parsing auth data:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const authData = localStorage.getItem('auth-storage')
        if (authData) {
          const { state } = JSON.parse(authData)
          if (state?.refreshToken) {
            const response = await axios.post('/api/auth/refresh', {}, {
              headers: {
                Authorization: `Bearer ${state.refreshToken}`,
              },
            })

            const { access_token } = response.data
            
            // Update stored tokens
            const updatedAuthData = {
              ...JSON.parse(authData),
              state: {
                ...state,
                accessToken: access_token,
              },
            }
            localStorage.setItem('auth-storage', JSON.stringify(updatedAuthData))

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        // Refresh failed, clear auth data and redirect to login
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // Handle other errors
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.')
    } else if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action.')
    }

    return Promise.reject(error)
  }
)

// Authentication API
export const authApi = {
  login: (credentials: LoginCredentials): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/login', credentials),

  register: (data: RegisterData): Promise<AxiosResponse<AuthResponse>> =>
    api.post('/auth/register', data),

  logout: (): Promise<AxiosResponse<ApiResponse>> =>
    api.delete('/auth/logout'),

  refresh: (): Promise<AxiosResponse<{ access_token: string }>> =>
    api.post('/auth/refresh'),

  getProfile: (): Promise<AxiosResponse<{ user: User }>> =>
    api.get('/auth/profile'),

  updateProfile: (data: Partial<User>): Promise<AxiosResponse<{ user: User }>> =>
    api.put('/auth/profile', data),

  changePassword: (data: { current_password: string; new_password: string }): Promise<AxiosResponse<ApiResponse>> =>
    api.put('/auth/change-password', data),
}

// Transformation API
export const transformApi = {
  getModels: (): Promise<AxiosResponse<{ models: ModelConfig[] }>> =>
    api.get('/transform/models'),

  uploadAndTransform: (data: FormData): Promise<AxiosResponse<{ task_id: string; transformation: Transformation }>> =>
    api.post('/transform/upload', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for upload
    }),

  getStatus: (taskId: string): Promise<AxiosResponse<{ transformation: Transformation }>> =>
    api.get(`/transform/status/${taskId}`),

  getResult: (taskId: string): Promise<AxiosResponse<{ transformation: Transformation; download_url: string }>> =>
    api.get(`/transform/result/${taskId}`),

  getHistory: (filters?: SearchFilters): Promise<AxiosResponse<PaginatedResponse<Transformation>>> => {
    const params = new URLSearchParams()
    
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.per_page) params.append('per_page', filters.per_page.toString())
    if (filters?.status) params.append('status', filters.status)
    if (filters?.model_name) params.append('model_name', filters.model_name)

    return api.get(`/transform/history?${params.toString()}`)
  },

  cancelTransformation: (taskId: string): Promise<AxiosResponse<{ transformation: Transformation }>> =>
    api.post(`/transform/cancel/${taskId}`),

  deleteTransformation: (taskId: string): Promise<AxiosResponse<ApiResponse>> =>
    api.delete(`/transform/delete/${taskId}`),
}

// Gallery API
export const galleryApi = {
  getUserGallery: (filters?: SearchFilters): Promise<AxiosResponse<PaginatedResponse<GalleryItem>>> => {
    const params = new URLSearchParams()
    
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.per_page) params.append('per_page', filters.per_page.toString())
    if (filters?.tags?.length) params.append('tags', filters.tags.join(','))

    return api.get(`/gallery?${params.toString()}`)
  },

  createGalleryItem: (data: GalleryItemCreate): Promise<AxiosResponse<{ gallery_item: GalleryItem }>> =>
    api.post('/gallery', data),

  getGalleryItem: (id: string): Promise<AxiosResponse<{ gallery_item: GalleryItem }>> =>
    api.get(`/gallery/${id}`),

  updateGalleryItem: (id: string, data: Partial<GalleryItemCreate>): Promise<AxiosResponse<{ gallery_item: GalleryItem }>> =>
    api.put(`/gallery/${id}`, data),

  deleteGalleryItem: (id: string): Promise<AxiosResponse<ApiResponse>> =>
    api.delete(`/gallery/${id}`),

  getPublicGallery: (filters?: SearchFilters): Promise<AxiosResponse<PaginatedResponse<GalleryItem>>> => {
    const params = new URLSearchParams()
    
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.per_page) params.append('per_page', filters.per_page.toString())
    if (filters?.tags?.length) params.append('tags', filters.tags.join(','))
    if (filters?.query) params.append('featured', 'true')

    return api.get(`/gallery/public?${params.toString()}`)
  },

  getSharedItem: (shareToken: string): Promise<AxiosResponse<{ gallery_item: GalleryItem }>> =>
    api.get(`/gallery/share/${shareToken}`),
}

// Utility functions
export const createFormData = (request: TransformationRequest): FormData => {
  const formData = new FormData()
  
  formData.append('image', request.image)
  formData.append('model_name', request.model_name)
  formData.append('prompt', request.prompt)
  
  if (request.negative_prompt) {
    formData.append('negative_prompt', request.negative_prompt)
  }
  if (request.strength !== undefined) {
    formData.append('strength', request.strength.toString())
  }
  if (request.guidance_scale !== undefined) {
    formData.append('guidance_scale', request.guidance_scale.toString())
  }
  if (request.num_inference_steps !== undefined) {
    formData.append('num_inference_steps', request.num_inference_steps.toString())
  }
  if (request.seed !== undefined) {
    formData.append('seed', request.seed.toString())
  }

  return formData
}

export const downloadFile = async (url: string, filename: string): Promise<void> => {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error('Download failed:', error)
    toast.error('Download failed')
  }
}

export const shareUrl = (url: string): void => {
  if (navigator.share) {
    navigator.share({
      title: 'UkiyoFusion Gallery Item',
      url: url,
    }).catch(console.error)
  } else {
    // Fallback to clipboard
    navigator.clipboard.writeText(url).then(() => {
      toast.success('Link copied to clipboard!')
    }).catch(() => {
      toast.error('Failed to copy link')
    })
  }
}

export default api
