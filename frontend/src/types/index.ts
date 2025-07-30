// User types
export interface User {
  id: string
  username: string
  email?: string
  first_name?: string
  last_name?: string
  avatar_url?: string
  bio?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
  total_transformations: number
  storage_used: number
}

// Authentication types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  message: string
}

// Transformation types
export interface Transformation {
  id: string
  task_id: string
  status: TransformationStatus
  original_filename: string
  original_url: string
  original_size?: number
  model_name: string
  prompt: string
  negative_prompt?: string
  strength: number
  guidance_scale: number
  num_inference_steps: number
  seed?: number
  result_filename?: string
  result_url?: string
  result_size?: number
  processing_time?: number
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export type TransformationStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface TransformationRequest {
  image: File
  model_name: string
  prompt: string
  negative_prompt?: string
  strength?: number
  guidance_scale?: number
  num_inference_steps?: number
  seed?: number
}

export interface TransformationProgress {
  task_id: string
  status: TransformationStatus
  message: string
  progress: number
  timestamp: string
}

// Gallery types
export interface GalleryItem {
  id: string
  title: string
  description?: string
  tags: string[]
  is_public: boolean
  is_featured: boolean
  share_token?: string
  view_count: number
  like_count: number
  download_count: number
  created_at: string
  updated_at: string
  transformation?: Transformation
}

export interface GalleryItemCreate {
  transformation_id: string
  title: string
  description?: string
  tags?: string[]
  is_public?: boolean
}

// Model types
export interface ModelConfig {
  id: string
  name: string
  display_name: string
  description: string
  model_type: string
  default_prompt?: string
  default_negative_prompt?: string
  max_image_size: number
  supported_formats: string[]
  is_active: boolean
  is_premium: boolean
  avg_processing_time?: number
  usage_count: number
}

// API Response types
export interface ApiResponse<T = any> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface ErrorResponse {
  error: string
  message?: string
  details?: any
}

// WebSocket event types
export interface SocketEvent {
  type: string
  payload: any
}

export interface TransformationProgressEvent extends SocketEvent {
  type: 'transformation_progress'
  payload: TransformationProgress
}

// UI state types
export interface LoadingState {
  isLoading: boolean
  error: string | null
}

export interface UploadState {
  file: File | null
  preview: string | null
  isUploading: boolean
  progress: number
}

// Form types
export interface TransformForm {
  model_name: string
  prompt: string
  negative_prompt: string
  strength: number
  guidance_scale: number
  num_inference_steps: number
  seed: string
}

export interface ProfileForm {
  first_name: string
  last_name: string
  bio: string
  avatar_url: string
}

export interface GalleryForm {
  title: string
  description: string
  tags: string
  is_public: boolean
}

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// Theme types
export interface ThemeConfig {
  primaryColor: string
  secondaryColor: string
  accentColor: string
  backgroundColor: string
  textColor: string
  borderColor: string
}

// Navigation types
export interface NavItem {
  name: string
  href: string
  icon?: any
  current?: boolean
  protected?: boolean
}

// File types
export interface FileUpload {
  file: File
  url: string
  type: string
  size: number
  name: string
}

// Search and filter types
export interface SearchFilters {
  query?: string
  tags?: string[]
  status?: TransformationStatus
  model_name?: string
  is_public?: boolean
  page?: number
  per_page?: number
}

// Settings types
export interface UserSettings {
  notifications: {
    email: boolean
    push: boolean
    transformation_complete: boolean
    gallery_updates: boolean
  }
  privacy: {
    profile_public: boolean
    show_stats: boolean
    allow_downloads: boolean
  }
  preferences: {
    default_model: string
    auto_save_gallery: boolean
    quality_preference: 'fast' | 'balanced' | 'quality'
  }
}

// Statistics types
export interface UserStats {
  total_transformations: number
  successful_transformations: number
  failed_transformations: number
  avg_processing_time: number
  storage_used: number
  gallery_items: number
  public_gallery_items: number
  total_views: number
  total_likes: number
  total_downloads: number
}

export interface AppStats {
  total_users: number
  total_transformations: number
  total_gallery_items: number
  avg_processing_time: number
  popular_models: Array<{
    name: string
    usage_count: number
  }>
}
