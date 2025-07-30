const GalleryPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Gallery</h1>
        <p className="text-gray-600 mt-2">Your personal collection of transformed images.</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-center text-gray-600 py-12">
          No gallery items yet. Start by transforming some images!
        </p>
      </div>
    </div>
  )
}

export default GalleryPage
