import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ImageUpload from '../components/ImageUpload';

// Mock getUserMedia
const mockGetUserMedia = jest.fn();
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: mockGetUserMedia,
  },
});

// Mock video element
HTMLVideoElement.prototype.play = jest.fn();

describe('ImageUpload Camera Feature', () => {
  const mockOnImageUpload = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders camera button', () => {
    render(<ImageUpload onImageUpload={mockOnImageUpload} />);
    
    const cameraButton = screen.getByText('Take Photo');
    expect(cameraButton).toBeInTheDocument();
  });

  test('opens camera dialog when camera button is clicked', async () => {
    // Mock successful camera access
    const mockStream = {
      getTracks: () => [{ stop: jest.fn() }],
    };
    mockGetUserMedia.mockResolvedValueOnce(mockStream);

    render(<ImageUpload onImageUpload={mockOnImageUpload} />);
    
    const cameraButton = screen.getByText('Take Photo');
    fireEvent.click(cameraButton);

    await waitFor(() => {
      expect(screen.getByText('Take a Photo')).toBeInTheDocument();
    });
  });

  test('handles camera permission error', async () => {
    // Mock camera access denial
    mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));

    render(<ImageUpload onImageUpload={mockOnImageUpload} />);
    
    const cameraButton = screen.getByText('Take Photo');
    fireEvent.click(cameraButton);

    // Wait for the dialog to open first
    await waitFor(() => {
      expect(screen.getByText('Take a Photo')).toBeInTheDocument();
    });

    // Then wait for the error message
    await waitFor(() => {
      expect(screen.getByText(/Unable to access camera/)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  test('renders switch camera button when camera is active', async () => {
    const mockStream = {
      getTracks: () => [{ stop: jest.fn() }],
    };
    mockGetUserMedia.mockResolvedValueOnce(mockStream);

    render(<ImageUpload onImageUpload={mockOnImageUpload} />);
    
    const cameraButton = screen.getByText('Take Photo');
    fireEvent.click(cameraButton);

    await waitFor(() => {
      expect(screen.getByText('Switch')).toBeInTheDocument();
    });
  });

  test('closes camera dialog when close button is clicked', async () => {
    const mockStream = {
      getTracks: () => [{ stop: jest.fn() }],
    };
    mockGetUserMedia.mockResolvedValueOnce(mockStream);

    render(<ImageUpload onImageUpload={mockOnImageUpload} />);
    
    const cameraButton = screen.getByText('Take Photo');
    fireEvent.click(cameraButton);

    await waitFor(() => {
      expect(screen.getByText('Take a Photo')).toBeInTheDocument();
    });

    // Find and click the close button (X icon)
    const closeButtons = screen.getAllByRole('button');
    const closeButton = closeButtons.find(button => 
      button.querySelector('[data-testid="CloseIcon"]')
    );
    
    if (closeButton) {
      fireEvent.click(closeButton);
    }

    await waitFor(() => {
      expect(screen.queryByText('Take a Photo')).not.toBeInTheDocument();
    });
  });
});
