import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface Contact {
  id: number;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  company: string | null;
  position: string | null;
  owner_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export function useContacts(search?: string) {
  return useQuery({
    queryKey: ['contacts', search],
    queryFn: async () => {
      const params = search ? { search } : {};
      const response = await api.get('/api/v1/contacts', { params });
      return response.data as Contact[];
    },
  });
}

export function useContact(id: number) {
  return useQuery({
    queryKey: ['contact', id],
    queryFn: async () => {
      const response = await api.get(`/api/v1/contacts/${id}`);
      return response.data as Contact;
    },
    enabled: !!id,
  });
}

export function useCreateContact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Contact>) => {
      const response = await api.post('/api/v1/contacts', data);
      return response.data as Contact;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useUpdateContact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...data }: Partial<Contact> & { id: number }) => {
      const response = await api.put(`/api/v1/contacts/${id}`, data);
      return response.data as Contact;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}

export function useDeleteContact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/api/v1/contacts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });
}
