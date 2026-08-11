export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserLoginPayload {
  email: string;
  password: string;
}

export interface UserSignupPayload {
  email: string;
  username: string;
  password: string;
}

export interface RefreshTokenPayload {
  refresh_token: string;
}
