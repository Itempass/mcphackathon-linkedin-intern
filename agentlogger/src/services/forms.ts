// Form data interfaces
export interface ContactFormData {
  name: string;
  email: string;
  message: string;
}

export interface WaitlistFormData {
  email: string;
  reference: string;
  waitlist: string;
  message?: string;
}

export interface EarlyAccessFormData {
  email: string;
  reference: string;
}

// API response interface
export interface ApiResponse {
  success?: boolean;
  error?: string;
}

// Configuration - Updated for Next.js API routes
const API_BASE_URL = '/api/forms';

// Generic API request function
async function makeApiRequest<T>(
  endpoint: string, 
  data: T
): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Contact form submission
export async function submitContactForm(data: ContactFormData): Promise<ApiResponse> {
  // Validate required fields
  if (!data.email || !data.name || !data.message) {
    throw new Error('All fields (name, email, message) are required');
  }

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    throw new Error('Please enter a valid email address');
  }

  return makeApiRequest('/submit_contact_form', data);
}

// Waitlist form submission
export async function submitWaitlistForm(data: WaitlistFormData): Promise<ApiResponse> {
  // Validate required fields
  if (!data.email || !data.reference || !data.waitlist) {
    throw new Error('All fields (email, reference, waitlist) are required');
  }

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    throw new Error('Please enter a valid email address');
  }

  return makeApiRequest('/submit_waitlist_form', data);
}

// Early access form submission
export async function submitEarlyAccessForm(data: EarlyAccessFormData): Promise<ApiResponse> {
  // Validate required fields
  if (!data.email || !data.reference) {
    throw new Error('Both email and reference are required');
  }

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    throw new Error('Please enter a valid email address');
  }

  return makeApiRequest('/submit_early_access_form', data);
}

// Helper function to get common form references
export const FormReferences = {
  LANDING_PAGE: 'landing page',
  CONTACT_PAGE: 'contact page',
  FOOTER: 'footer',
  NAVBAR: 'navbar',
  HERO_SECTION: 'hero section',
  PRICING_PAGE: 'pricing page',
  ABOUT_PAGE: 'about page',
} as const;

// Helper function to get common waitlist types
export const WaitlistTypes = {
  BETA_ACCESS: 'beta access',
  EARLY_BIRD: 'early bird',
  PRODUCT_LAUNCH: 'product launch',
  FEATURE_REQUEST: 'feature request',
} as const;

// Utility function for form state management
export interface FormState {
  isSubmitting: boolean;
  isSuccess: boolean;
  error: string | null;
}

export function createInitialFormState(): FormState {
  return {
    isSubmitting: false,
    isSuccess: false,
    error: null,
  };
}

// Hook-like helper for handling form submission states
export function createFormHandler<T>(
  submitFunction: (data: T) => Promise<ApiResponse>
) {
  return async (
    data: T,
    onStateChange: (state: FormState) => void
  ): Promise<boolean> => {
    onStateChange({
      isSubmitting: true,
      isSuccess: false,
      error: null,
    });

    try {
      const result = await submitFunction(data);
      
      if (result.success) {
        onStateChange({
          isSubmitting: false,
          isSuccess: true,
          error: null,
        });
        return true;
      } else {
        onStateChange({
          isSubmitting: false,
          isSuccess: false,
          error: result.error || 'Submission failed',
        });
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      onStateChange({
        isSubmitting: false,
        isSuccess: false,
        error: errorMessage,
      });
      return false;
    }
  };
}

// Pre-configured form handlers
export const contactFormHandler = createFormHandler(submitContactForm);
export const waitlistFormHandler = createFormHandler(submitWaitlistForm);
export const earlyAccessFormHandler = createFormHandler(submitEarlyAccessForm);
