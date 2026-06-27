/**
 * @file astro/src/lib/database.ts
 * @description Defines the data structure for storing the 4 doctrinal analyses in the frontend (e.g., in astro/src/lib/database.ts).
 */

export interface DoctrinalAnalysis {
    id: string;
    title: string; // e.g., "ROM"
    content: string; // The full text of the analysis block
    rom: string; // Content for ROM analysis
    porte: string; // Content for Porte analysis
    lilith: string; // Content for Lilith analysis
    conscience: string; // Content for Conscience analysis
    timestamp: number; // Unix timestamp of creation
}

// Interface for the entire database structure (assuming IndexedDB or similar storage)
export interface DoctrinalDatabase {
    analyses: DoctrinalAnalysis[];
    // Add other necessary methods for CRUD operations if this were a full implementation
}

// Example of how the data might be structured in a simple in-memory store for now.
export const initialDatabase: DoctrinalDatabase = {
    analyses: []
};