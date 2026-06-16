// src/lib/capacitor-bridge.ts — Bridge pour plugins natifs Capacitor

interface CapacitorWindow {
  Capacitor?: {
    isNative?: boolean;
    Plugins?: Record<string, any>;
  };
}

const capWindow = (typeof window !== 'undefined' ? window : {}) as CapacitorWindow;

export const capacitorBridge = {
  /** Détecte si on tourne dans Capacitor (iOS / Android natif) */
  isNative(): boolean {
    return !!(capWindow.Capacitor?.isNative);
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
    async synthesize(prompt: string, options?: {
      temperature?: number;
      maxTokens?: number;
    }): Promise<string | null> {
      const result = await capacitorBridge.callPlugin<{ text: string }>(
        'GemmaSynthesis',
        'synthesize',
        { prompt, ...options }
      );
      return result?.text ?? null;
    },
  },
};

export default capacitorBridge;
