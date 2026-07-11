import fr from '../locales/fr.json';
import en from '../locales/en.json';
import es from '../locales/es.json';
import pt from '../locales/pt.json';
import nl from '../locales/nl.json';
import de from '../locales/de.json';

const translations: Record<string, Record<string, string>> = {
  fr,
  en,
  es,
  pt,
  nl,
  de
};

export const i18n = {
  /** Detect the current language based on localStorage or browser navigator */
  detect(): string {
    return 'en';
  },

  /** Translate a key to the current language */
  t(key: string, lang?: string): string {
    const activeLang = lang || this.detect();
    const dict = translations[activeLang] || translations['fr'];
    return dict[key] || translations['fr'][key] || key;
  },

  /** Apply translations to all elements in the DOM with a data-i18n attribute */
  apply() {
    if (typeof document === 'undefined') return;
    const current = this.detect();
    
    // Set HTML lang attribute
    document.documentElement.lang = current;
    
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (!key) return;
      
      const translation = this.t(key, current);
      
      // Handle inputs placeholder vs regular text
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.setAttribute('placeholder', translation);
      } else {
        el.textContent = translation;
      }
    });
  },

  /** Set active language and save to localStorage, sync with backend */
  async setLang(lang: string) {
    if (typeof window === 'undefined') return;
    if (!translations[lang]) return;
    
    localStorage.setItem('karmic_lang', lang);
    this.apply();
    
    // Dispatch a custom event to notify components that language changed
    window.dispatchEvent(new CustomEvent('karmic-lang-changed', { detail: { lang } }));

    // Sync with backend API
    try {
      await fetch('/set_lang', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ lang }),
      });
    } catch (e) {
      console.warn('Failed to sync language choice with backend API', e);
    }
  }
};
