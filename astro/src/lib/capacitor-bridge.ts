import { Capacitor } from '@capacitor/core';

interface CapacitorWindow {
  Capacitor?: {
    Plugins?: Record<string, any>;
  };
}

const capWindow = (typeof window !== 'undefined' ? window : {}) as CapacitorWindow;

export const capacitorBridge = {
  /** Détecte si on tourne dans Capacitor (iOS / Android natif) */
  isNative(): boolean {
    if (typeof window === 'undefined') return false;
    return Capacitor.isNativePlatform();
  },

  /** Appelle un plugin Capacitor natif */
  async callPlugin<T = any>(
    pluginName: string,
    method: string,
    args: Record<string, unknown> = {}
  ): Promise<T | null> {
    if (!this.isNative()) return null;

    const plugin = capWindow.Capacitor?.Plugins?.[pluginName];
    if (!plugin) {
      console.warn(`[capacitor-bridge] Plugin "${pluginName}" not found`);
      return null;
    }

    try {
      const result = await plugin[method](args);
      return result as T;
    } catch (err) {
      console.error(`[capacitor-bridge] Plugin "${pluginName}.${method}" failed:`, err);
      return null;
    }
  },

  /** StatusBar helper */
  statusBar: {
    async setStyle(style: 'DARK' | 'LIGHT'): Promise<void> {
      await capacitorBridge.callPlugin('StatusBar', 'setStyle', { style });
    },
    async setBackgroundColor(color: string): Promise<void> {
      await capacitorBridge.callPlugin('StatusBar', 'setBackgroundColor', { color });
    },
  },

  /** GemmaSynthesis plugin helper (AI locale sur mobile) */
  gemma: {
    async generate(system: string, user: string, type: string = 'synthesis', lang: string = 'fr', profile: any = {}): Promise<string | null> {
      const result = await capacitorBridge.callPlugin<{ synthesis: string }>(
        'GemmaSynthesis',
        'generate',
        { system, user, type, lang, profile }
      );
      return result?.synthesis ?? null;
    },

    async checkAvailability(): Promise<{ available: boolean; status: string; downloading: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'checkAvailability');
    },

    async requestStoragePermission(): Promise<{ ok: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'requestStoragePermission');
    },

    async prepareModel(report: boolean = false): Promise<{ ok: boolean; loraUsed: boolean; cached: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'prepareModel', { report });
    },

    async setModel(modelId: string, modelUrl: string, filename: string): Promise<{ ok: boolean; modelId: string } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'setModel', { modelId, modelUrl, filename });
    },

    async downloadModel(): Promise<{ ok: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'downloadModel');
    },

    async selectLocalModel(): Promise<{ ok: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'selectLocalModel');
    },

    async getModelStatus(): Promise<{ downloaded: boolean; modelId: string; sizeBytes: number } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'getModelStatus');
    },

    async getDeviceMemory(): Promise<{ totalRamGb: number; sufficient: boolean; recommended: string } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'getDeviceMemory');
    },

    async unloadModel(): Promise<{ ok: boolean } | null> {
      return await capacitorBridge.callPlugin('GemmaSynthesis', 'unloadModel');
    },
  },
};

export default capacitorBridge;
