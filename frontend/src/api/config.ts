const DEFAULT_BACKEND_ORIGIN = 'https://sql-agent-jwi7.onrender.com';
const API_V1_PATH = '/api/v1';

const trimTrailingSlashes = (value: string): string => value.replace(/\/+$/, '');

export const BACKEND_ORIGIN = trimTrailingSlashes(
  import.meta.env.VITE_BACKEND_ORIGIN || DEFAULT_BACKEND_ORIGIN
);

export const API_BASE_URL = trimTrailingSlashes(
  import.meta.env.VITE_API_BASE_URL || `${BACKEND_ORIGIN}${API_V1_PATH}`
);

export const buildBackendUrl = (path: string): string => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${BACKEND_ORIGIN}${normalizedPath}`;
};
