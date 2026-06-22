import { registerPlugin } from '@capacitor/core';

export interface CapacitorFirestorePlugin {
  getDocument(options: { collection: string; docId: string }): Promise<{ data: any }>;
}

export const FirestoreBridge = registerPlugin<CapacitorFirestorePlugin>('CapacitorFirestore');
