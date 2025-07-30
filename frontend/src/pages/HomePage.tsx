import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles, Image, Palette, Users } from 'lucide-react'

import { useAuthStore } from '@/store/authStore'

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuthStore()

  const features = [
    {
      icon: Image,
      title: 'AI-Powered Transformation',
      description: 'Upload any image and watch as our advanced diffusion models transform it into stunning Ukiyo-e style art.',
    },
    {
      icon: Palette,
      title: 'Multiple Art Styles',
      description: 'Choose from various AI models specialized in different artistic styles and techniques.',
    },
    {
      icon: Users,
      title: 'Community Gallery',
      description: 'Share your creations with the community and discover amazing artworks from other artists.',
    },
    {
      icon: Sparkles,
      title: 'High Quality Results',
      description: 'Get professional-quality results with our state-of-the-art diffusion models and optimization.',
    },
  ]

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="ukiyo-pattern absolute inset-0"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 sm:pt-24 sm:pb-20">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Transform Your Images with{' '}
              <span className="gradient-text">AI-Powered Ukiyo-e</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Experience the fusion of traditional Japanese woodblock printing with cutting-edge AI technology. 
              Create stunning artistic transformations of your photos in seconds.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {isAuthenticated ? (
                <Link
                  to="/transform"
                  className="btn-primary btn-lg inline-flex items-center"
                >
                  Start Creating
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="btn-primary btn-lg inline-flex items-center"
                  >
                    Get Started Free
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Link>
                  <Link
                    to="/gallery/public"
                    className="btn-secondary btn-lg"
                  >
                    View Gallery
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Creative Artists
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform combines the latest in AI technology with intuitive design 
              to make artistic transformation accessible to everyone.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-lg p-6 shadow-soft hover:shadow-lg transition-shadow"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How it Works Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Transform your images in three simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Upload Your Image
              </h3>
              <p className="text-gray-600">
                Simply drag and drop or select an image from your device. 
                We support JPG, PNG, and WebP formats.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Choose Your Style
              </h3>
              <p className="text-gray-600">
                Select from our collection of AI models, each specialized in 
                different artistic styles and techniques.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Get Your Artwork
              </h3>
              <p className="text-gray-600">
                Watch as our AI transforms your image in real-time. 
                Download or share your beautiful creation with the world.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Create Amazing Art?
            </h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join thousands of artists who are already creating beautiful Ukiyo-e style 
              artworks with our AI-powered platform.
            </p>
            {!isAuthenticated && (
              <Link
                to="/register"
                className="bg-white text-primary-600 hover:bg-gray-100 font-semibold px-8 py-3 rounded-md transition-colors inline-flex items-center"
              >
                Start Creating for Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
