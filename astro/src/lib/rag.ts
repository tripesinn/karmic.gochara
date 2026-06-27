/**
 * @file astro/src/lib/rag.ts
 * @description Core RAG logic for parsing responses and building the context for the light prompt.
 */

import { DoctrinalAnalysis } from './database';

// Mock function to simulate fetching analysis data from the database
// In a real app, this would interact with IndexedDB.
const mockDatabase = {
    analyses: [
        { id: 'rom', title: 'ROM', content: 'The ROM analysis details...', rom: 'ROM analysis details...', porte: '', lilith: '', conscience: '', timestamp: Date.now() - 1000 },
        { id: 'porte', title: 'Porte', content: 'The Porte analysis details...', rom: '', porte: 'Porte analysis details...', lilith: '', conscience: '', timestamp: Date.now() - 5000 },
        { id: 'lilith', title: 'Lilith', content: 'The Lilith analysis details...', rom: '', porte: '', lilith: 'Lilith analysis details...', conscience: '', timestamp: Date.now() - 10000 },
        { id: 'conscience', title: 'Conscience', content: 'The Conscience analysis details...', rom: '', porte: '', lilith: '', conscience: 'Conscience analysis details...', timestamp: Date.now() - 15000 }
    ]
};

// Mock function to simulate saving a new analysis
export const saveAnalysis = (analysis: DoctrinalAnalysis) => {
    console.log(`[DB] Saving analysis: ${analysis.title}`);
    mockDatabase.analyses.push(analysis);
    return analysis.id;
};

// Mock function to simulate fetching an analysis by ID
export const getAnalysisById = (id: string): DoctrinalAnalysis | undefined => {
    return mockDatabase.analyses.find(a => a.id === id);
};

// Mock function to simulate fetching all analyses
export const getAllAnalyses = (): DoctrinalAnalysis[] => {
    return mockDatabase.analyses;
};


/**
 * Step 4: Develop `parseResponse(fullResponse: string)` using Regex to split the response into the 4 doctrinal blocks.
 * This function is crucial for extracting the raw text for each analysis type.
 * @param fullResponse The complete text response from the LLM.
 * @returns An object containing the 4 extracted analysis blocks.
 */
export function parseResponse(fullResponse: string): { rom: string, porte: string, lilith: string, conscience: string } {
    // Regex patterns are placeholders based on the plan.
    // In a real scenario, these would be highly specific to the LLM's output format.
    const romRegex = /ROM Analysis:\s*([\s\S]*?)(?=Porte Analysis:|$)/;
    const porteRegex = /Porte Analysis:\s*([\s\S]*?)(?=Lilith Analysis:|$)/;
    const lilithRegex = /Lilith Analysis:\s*([\s\S]*?)(?=Conscience Analysis:|$)/;
    const conscienceRegex = /Conscience Analysis:\s*([\s\S]*)/; // Last one doesn't need a lookahead

    const romMatch = fullResponse.match(romRegex);
    const porteMatch = fullResponse.match(porteRegex);
    const lilithMatch = fullResponse.match(lilithRegex);
    const conscienceMatch = fullResponse.match(conscienceRegex);

    return {
        rom: romMatch ? romMatch[1].trim() : 'No ROM analysis found.',
        porte: porteMatch ? porteMatch[1].trim() : 'No Porte analysis found.',
        lilith: lilithMatch ? lilithMatch[1].trim() : 'No Lilith analysis found.',
        conscience: conscienceMatch ? conscienceMatch[1].trim() : 'No Conscience analysis found.',
    };
}


/**
 * Step 5: Develop `buildRAGContext(analysisId: string, question: string)` implementing keyword matching to select relevant blocks and construct the condensed "Light Prompt".
 * @param analysisId The ID of the analysis block to retrieve.
 * @param question The user's follow-up question.
 * @returns The condensed prompt string to be sent to the LLM.
 */
export function buildRAGContext(analysisId: string, question: string): string {
    const analysis = getAnalysisById(analysisId);
    if (!analysis) {
        return `Context for analysis ID ${analysisId} not found.`;
    }

    // Keyword Matching Logic (Placeholder - needs specific keywords)
    let relevantContent = analysis.content;
    let keyword = question.toLowerCase();

    if (keyword.includes('saturn') || keyword.includes('saturnus')) {
        // Example: If the question is about Saturn, prioritize the ROM block.
        relevantContent = analysis.rom;
        keyword = 'saturn';
    } else if (keyword.includes('chiron') || keyword.includes('chironus')) {
        // Example: If the question is about Chiron, prioritize the Lilith block.
        relevantContent = analysis.lilith;
        keyword = 'chiron';
    } else if (keyword.includes('dasha') || keyword.includes('dasha')) {
        // Example: If the question is about Dasha, prioritize the Porte block.
        relevantContent = analysis.porte;
        keyword = 'dasha';
    } else {
        // Default: Use the full content if no specific keyword is matched.
        relevantContent = analysis.content;
    }

    // Construct the condensed "Light Prompt"
    const lightPrompt = `
    You are an expert in Karmic Gochara analysis.
    Use ONLY the following context to answer the user's question.
    
    --- CONTEXT ---
    ${relevantContent}
    --- END CONTEXT ---
    
    User Question: ${question}
  `;

    return lightPrompt;
}