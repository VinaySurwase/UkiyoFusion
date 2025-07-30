import { Link } from 'react-router-dom'
import { Heart, Github, Twitter, Mail } from 'lucide-react'

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-white font-bold text-sm">UF</span>
                </div>
                <span className="text-xl font-bold gradient-text">UkiyoFusion</span>
              </div>
              <p className="text-gray-600 text-sm mb-4 max-w-md">
                Transform your images into beautiful Ukiyo-e style art using cutting-edge AI diffusion models. 
                Experience the fusion of traditional Japanese aesthetics with modern technology.
              </p>
              <div className="flex space-x-4">
                <a
                  href="https://github.com/UkiyoFusion"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-primary-600 transition-colors"
                >
                  <Github className="w-5 h-5" />
                </a>
                <a
                  href="https://twitter.com/UkiyoFusion"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-primary-600 transition-colors"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a
                  href="mailto:hello@ukiyofusion.com"
                  className="text-gray-400 hover:text-primary-600 transition-colors"
                >
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Navigation Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">
                Platform
              </h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/transform" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Transform Images
                  </Link>
                </li>
                <li>
                  <Link to="/gallery/public" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Public Gallery
                  </Link>
                </li>
                <li>
                  <Link to="/gallery" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    My Gallery
                  </Link>
                </li>
                <li>
                  <Link to="/dashboard" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>

            {/* Support Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">
                Support
              </h3>
              <ul className="space-y-3">
                <li>
                  <a href="/help" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="/docs" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="/api" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    API Reference
                  </a>
                </li>
                <li>
                  <a href="/contact" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    Contact Us
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-6 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center text-sm text-gray-600 mb-4 md:mb-0">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-red-500 mx-1" />
              <span>by the UkiyoFusion Team</span>
            </div>
            
            <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
              <div className="flex space-x-6 text-sm text-gray-600">
                <a href="/privacy" className="hover:text-primary-600 transition-colors">
                  Privacy Policy
                </a>
                <a href="/terms" className="hover:text-primary-600 transition-colors">
                  Terms of Service
                </a>
                <a href="/cookies" className="hover:text-primary-600 transition-colors">
                  Cookie Policy
                </a>
              </div>
              
              <div className="text-sm text-gray-600">
                © {currentYear} UkiyoFusion. All rights reserved.
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
