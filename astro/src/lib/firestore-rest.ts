// src/lib/firestore-rest.ts — Firestore via REST API (no WebChannel/streaming)
import { Capacitor } from '@capacitor/core';
import { CapacitorHttp } from '@capacitor/core';

const PROJECT_ID = 'karmic-gochara-cloud';
const isEmulator = (import.meta as any).env?.PUBLIC_FIREBASE_EMULATOR === 'true';
const BASE = isEmulator 
  ? `http://127.0.0.1:8080/v1/projects/${PROJECT_ID}/databases/(default)/documents`
  : `https://firestore.googleapis.com/v1/projects/${PROJECT_ID}/databases/(default)/documents`;

export async function getFirestoreDoc(collection: string, docId: string, idToken: string): Promise<Record<string, any> | null> {
  const url = `${BASE}/${collection}/${docId}`;
  const isNative = Capacitor.isNativePlatform();

  try {
    if (isNative) {
      const response = await CapacitorHttp.request({
        method: 'GET',
        url: url,
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Accept': 'application/json',
        },
      });
      if (response.status === 404) return null;
      if (response.status >= 400) throw new Error(`Firestore REST error: ${response.status}`);
      return transformFirestoreDoc(response.data);
    } else {
      const res = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Accept': 'application/json',
        },
      });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`Firestore REST error: ${res.status}`);
      const data = await res.json();
      return transformFirestoreDoc(data);
    }
  } catch (err) {
    console.error('Firestore REST get error:', err);
    throw err;
  }
}

export async function setFirestoreDoc(
  collection: string,
  docId: string,
  fields: Record<string, any>,
  idToken: string
): Promise<void> {
  const url = `${BASE}/${collection}/${docId}`;
  const firebaseData = { fields: toFirestoreFields(fields) };
  const isNative = Capacitor.isNativePlatform();

  try {
    if (isNative) {
      const response = await CapacitorHttp.request({
        method: 'PATCH',
        url: url,
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
        data: firebaseData,
      });
      if (response.status >= 400) throw new Error(`Firestore REST write error: ${response.status}`);
    } else {
      const res = await fetch(url, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(firebaseData),
      });
      if (!res.ok) throw new Error(`Firestore REST write error: ${res.status}`);
    }
  } catch (err) {
    console.error('Firestore REST set error:', err);
    throw err;
  }
}

// ── Firestore REST format transformers ──

function transformFirestoreDoc(doc: any): Record<string, any> | null {
  if (!doc || !doc.fields) return null;
  const result: Record<string, any> = {};
  for (const [key, value] of Object.entries(doc.fields)) {
    result[key] = extractValue(value as any);
  }
  return result;
}

function extractValue(field: any): any {
  if (field.stringValue !== undefined) return field.stringValue;
  if (field.integerValue !== undefined) return parseInt(field.integerValue);
  if (field.doubleValue !== undefined) return parseFloat(field.doubleValue);
  if (field.booleanValue !== undefined) return field.booleanValue;
  if (field.timestampValue !== undefined) return field.timestampValue;
  if (field.nullValue !== undefined) return null;
  if (field.mapValue) return transformFirestoreDoc({ fields: field.mapValue.fields });
  if (field.arrayValue) return field.arrayValue.values?.map(extractValue) ?? [];
  return null;
}

function toFirestoreFields(data: Record<string, any>): Record<string, any> {
  const fields: Record<string, any> = {};
  for (const [key, value] of Object.entries(data)) {
    fields[key] = toFirestoreValue(value);
  }
  return fields;
}

function toFirestoreValue(value: any): any {
  if (value === null || value === undefined) return { nullValue: null };
  if (typeof value === 'string') return { stringValue: value };
  if (typeof value === 'number') {
    return Number.isInteger(value) ? { integerValue: String(value) } : { doubleValue: value };
  }
  if (typeof value === 'boolean') return { booleanValue: value };
  if (typeof value === 'object') {
    if (value._serverTimestamp) return { timestampValue: new Date().toISOString() };
    if (Array.isArray(value)) return { arrayValue: { values: value.map(toFirestoreValue) } };
    return { mapValue: { fields: toFirestoreFields(value) } };
  }
  return { stringValue: String(value) }
}

// Server timestamp helper
export function serverTimestamp() {
  return { _serverTimestamp: true };
}
