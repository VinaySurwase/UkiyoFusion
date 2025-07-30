const TransformPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Transform Images</h1>
        <p className="text-gray-600 mt-2">Upload an image and transform it with AI-powered diffusion models.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Image</h2>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <p className="text-gray-600">Drag and drop an image here, or click to select</p>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Settings</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select className="w-full input">
                <option>Stable Diffusion v1.5</option>
                <option>Ukiyo-e Style Transfer</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Prompt</label>
              <textarea className="w-full input" rows={3} placeholder="Describe the style you want..."></textarea>
            </div>
            
            <button className="btn-primary w-full">
              Transform Image
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TransformPage
