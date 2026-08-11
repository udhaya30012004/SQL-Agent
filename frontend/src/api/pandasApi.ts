import { apiClient } from './client';
import { CsvUploadResponse } from '../types/pandas';

export const pandasApi = {
  uploadCsv: async (file: File): Promise<CsvUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<CsvUploadResponse>('/pandas/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
};
