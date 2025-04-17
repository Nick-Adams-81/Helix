const API_URL = ''; // Empty string since we're using relative URLs

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
}

export interface ApiErrorResponse {
  error: string;
}

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json() as ApiErrorResponse;
    throw new ApiError(errorData.error || `HTTP error! status: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const authService = {
  login: async (data: LoginData): Promise<User> => {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include', // Important for session cookies
    });
    return handleResponse<User>(response);
  },

  signup: async (data: SignupData): Promise<User> => {
    const response = await fetch(`${API_URL}/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    return handleResponse<User>(response);
  },

  logout: async (): Promise<void> => {
    const response = await fetch(`${API_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    await handleResponse<void>(response);
  },

  getCurrentUser: async (): Promise<User | null> => {
    try {
      const response = await fetch(`${API_URL}/me`, {
        credentials: 'include',
      });
      if (response.status === 401) {
        return null;
      }
      return handleResponse<User>(response);
    } catch (error) {
      if (error instanceof ApiError && error.message.includes('401')) {
        return null;
      }
      throw error;
    }
  }
};

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
}

export const chatService = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
      credentials: 'include',
    });
    return handleResponse<ChatResponse>(response);
  }
}; 