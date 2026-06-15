        const T = window.SERVER_DATA.lang;
        const CURRENT_PSEUDO = window.SERVER_DATA.session_user;
        const CURRENT_PLAN = window.SERVER_DATA.plan;

        // ── Variables Globales ──────────────────────────────────────────────────────
        let transitGeo = null;
        let birthGeo = null;
        let lastSynthesis = '';
        let chatHistory = [];
        let _cityTimer = null;
        let _birthCityTimer = null;
        let _pendingRating = 0;
        let calYear = new Date().getFullYear();
        let calMonth = new Date().getMonth() + 1;
        let calOpen = false;
        window._expandUsed = false;
        window._emailCtx = null;

        // ── Persistance Locale ──────────────────────────────────────────────────────
        const KarmicStore = {
            _key() { return 'kg_data_' + (CURRENT_PSEUDO || 'guest'); },
            save(data) {
                const current = this.get();
                localStorage.setItem(this._key(), JSON.stringify({ ...current, ...data }));
            },
            get() {
                try {
                    return JSON.parse(localStorage.getItem(this._key()) || '{}');
                } catch { return {}; }
            },
            clear() {
                localStorage.removeItem(this._key());
            }
        };

        // ── Cache Hors-Ligne (IndexedDB) ────────────────────────────────────────────
        const OfflineStore = {
            dbName: 'KarmicGocharaOffline',
            storeName: 'transits',
            async init() {
                return new Promise((resolve, reject) => {
                    const req = indexedDB.open(this.dbName, 1);
                    req.onupgradeneeded = (e) => {
                        const db = e.target.result;
                        if (!db.objectStoreNames.contains(this.storeName)) {
                            db.createObjectStore(this.storeName, { keyPath: 'date' });
                        }
                    };
                    req.onsuccess = () => resolve(req.result);
                    req.onerror = () => reject(req.error);
                });
            },
            async saveYear(yearData) {
                const db = await this.init();
                return new Promise((resolve, reject) => {
                    const tx = db.transaction(this.storeName, 'readwrite');
                    const store = tx.objectStore(this.storeName);
                    for (const [date, data] of Object.entries(yearData)) {
                        store.put({ date, data });
                    }
                    tx.oncomplete = () => resolve();
                    tx.onerror = () => reject(tx.error);
                });
            },
            async getDay(dateStr) {
                const db = await this.init();
                return new Promise((resolve, reject) => {
                    const tx = db.transaction(this.storeName, 'readonly');
                    const store = tx.objectStore(this.storeName);
                    const req = store.get(dateStr);
                    req.onsuccess = () => resolve(req.result ? req.result.data : null);
                    req.onerror = () => reject(req.error);
                });
            }
        };

        // ── Local AI ──────────────────────────────────────────────────────────────────
        // Chrome Built-in AI (window.LanguageModel) — Chrome 127+ desktop avec flag
        const ChromeAI = {
            _api() { return window.LanguageModel || window.ai?.languageModel || null; },
            async isAvailable() {
                try {
                    const api = this._api();
                    if (!api) return false;
                    const av = await api.availability();
                    return av === 'available';
                } catch { return false; }
            },
            async generate(system, user) {
                const api = this._api();
                const session = await api.create({ systemPrompt: system, temperature: 0.7, topK: 40 });
                try {
                    const raw = await session.prompt(user);
                    return { ok: true, synthesis: raw.trim(), local: true, model: 'chrome-ai' };
                } finally { try { session.destroy(); } catch { } }
            },
        };

const API_BASE = window.Capacitor?.isNative ? 'https://gochara-api-732214018947.europe-west9.run.app' : '';

        const NativeAI = {
            plugin() { return window.Capacitor?.Plugins?.NativeAI ?? null; },
            isWeb() { return !window.Capacitor?.isNative; },
            async checkModels() { 
                try { 
                    if (this.isWeb()) return { loaded: false }; 
                    return await this.plugin().checkModels(); 
                } catch { return { loaded: false }; } 
            },
            async isAvailable() { 
                try { 
                    if (await ChromeAI.isAvailable()) return true; 
                    if (this.isWeb()) return false;
                    const r = await this.checkModels(); 
                    return r.loaded; 
                } catch { return false; } 
            },
            async generate(s, u) { 
                if (await ChromeAI.isAvailable()) return ChromeAI.generate(s, u); 
                if (!this.isWeb()) return await this.plugin().generate({ system: s, user: u }); 
                throw new Error('Aucun modèle local disponible'); 
            },
        };

        // ── Monétisation AdMob & Unlock ──────────────────────────────────────────────
        const AD_UNIT_BANNER = 'ca-app-pub-3940256099942544/6300978111';
        const AD_UNIT_INTERSTITIAL = 'ca-app-pub-3940256099942544/1033173712';

        const Monetization = {
            _unlocked: null,
            async isUnlocked() { if (this._unlocked !== null) return this._unlocked; const p = window.Capacitor?.Plugins?.Unlock; if (!p) { this._unlocked = false; return false; } try { const r = await p.isUnlocked(); this._unlocked = r.unlocked; return r.unlocked; } catch { this._unlocked = false; return false; } },
            async purchase() { const p = window.Capacitor?.Plugins?.Unlock; if (!p) return false; try { const r = await p.purchase(); if (r.unlocked) { this._unlocked = true; hideBannerAd(); showUnlockSuccess(); } return r.unlocked; } catch (e) { if (e.message !== 'USER_CANCELED') alert('Erreur achat : ' + e.message); return false; } },
            async restore() { const p = window.Capacitor?.Plugins?.Unlock; if (!p) return false; try { const r = await p.restore(); if (r.unlocked) { this._unlocked = true; hideBannerAd(); } return r.unlocked; } catch { return false; } },
        };

        async function initAdMob() {
            const { AdMob } = window.Capacitor?.Plugins ?? {};
            if (!AdMob) return;
            if (await Monetization.isUnlocked()) return;
            try { await AdMob.initialize({ testingDevices: [], initializeForTesting: true }); await AdMob.showBanner({ adId: AD_UNIT_BANNER, adSize: 'BANNER', position: 'BOTTOM_CENTER', margin: 0 }); } catch (e) { console.warn('AdMob:', e); }
        }
        function hideBannerAd() { const { AdMob } = window.Capacitor?.Plugins ?? {}; if (AdMob) AdMob.hideBanner().catch(() => { }); }
        function showUnlockSuccess() { const btn = document.getElementById('btn-unlock'); if (btn) { btn.textContent = T.js_unlock_success; btn.style.color = '#6ab56a'; btn.disabled = true; } }

        function switchTab(tabId) {
            const gocharaBtn = document.getElementById('tab-gochara');
            const carteBtn = document.getElementById('tab-carte');
            const viewGochara = document.getElementById('view-gochara');
            const viewCarte = document.getElementById('view-carte');

            if (tabId === 'carte') {
                if (carteBtn) {
                    carteBtn.style.color = 'var(--gold)';
                    carteBtn.style.borderBottomColor = 'var(--gold)';
                }
                if (gocharaBtn) {
                    gocharaBtn.style.color = 'var(--text-dim)';
                    gocharaBtn.style.borderBottomColor = 'transparent';
                }
                if (viewGochara) viewGochara.style.display = 'none';
                if (viewCarte) {
                    viewCarte.style.display = 'block';
                    // Passer la date de transit sélectionnée pour afficher les planètes du jour
                    const tDate = document.getElementById('transit-date')?.value || '';
                    const tHour = new Date().getHours();
                    const chartParams = tDate
                        ? `date=${tDate}&hour=${tHour}&t=${Date.now()}`
                        : `t=${Date.now()}`;
                    const img = document.getElementById('karmic-chart-img');
                    if (img) img.src = '/chart/karmic.svg?' + chartParams;
                }
            } else {
                if (gocharaBtn) {
                    gocharaBtn.style.color = 'var(--gold)';
                    gocharaBtn.style.borderBottomColor = 'var(--gold)';
                }
                if (carteBtn) {
                    carteBtn.style.color = 'var(--text-dim)';
                    carteBtn.style.borderBottomColor = 'transparent';
                }
                if (viewCarte) viewCarte.style.display = 'none';
                if (viewGochara) viewGochara.style.display = 'block';
            }
        }

        function setLang(code) {
            fetch(API_BASE + '/set_lang', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lang: code })
            }).then(() => location.reload());
        }

        function toggleRegistration() {
            const fields = document.getElementById('registration-fields');
            const mainBtn = document.getElementById('main-action-btn');
            const toggleBtn = document.getElementById('toggle-reg-btn');
            const errDiv = document.getElementById('login-error');
            if (fields.style.display === 'none' || fields.style.display === '') {
                fields.style.display = 'block';
                mainBtn.innerHTML = T.js_toggle_register;
                mainBtn.onclick = register;
                toggleBtn.innerHTML = T.js_toggle_login;
            } else {
                fields.style.display = 'none';
                mainBtn.innerHTML = T.login || "CONNEXION";
                mainBtn.onclick = login;
                toggleBtn.innerHTML = T.create_profile || "CRÉER UN PROFIL";
            }
            errDiv.textContent = "";
        }

        function login() {
            const pseudo = document.getElementById('pseudo-input').value.trim();
            const errDiv = document.getElementById('login-error');
            const btn = document.getElementById('main-action-btn');
            if (!pseudo) { errDiv.textContent = T.js_err_pseudo; return; }
            errDiv.style.color = "var(--gold)";
            errDiv.innerHTML = '<span class="spinner"></span> ' + T.js_login_loading;
            if (btn) { btn.disabled = true; btn.style.opacity = '0.6'; }
            fetch(API_BASE + '/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pseudo: pseudo })
            })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        if (data.hook_natal) sessionStorage.setItem('hook_natal', data.hook_natal);
                        if (data.hook_engine) sessionStorage.setItem('hook_engine', data.hook_engine);
                        sessionStorage.setItem('currentPseudo', data.pseudo || pseudo);
                        location.reload();
                    } else {
                        errDiv.style.color = "#c97a6b";
                        errDiv.textContent = data.error || T.js_err_unknown;
                        if (btn) { btn.disabled = false; btn.style.opacity = ''; }
                    }
                })
                .catch(() => {
                    errDiv.style.color = "#c97a6b";
                    errDiv.textContent = T.js_err_network;
                    if (btn) { btn.disabled = false; btn.style.opacity = ''; }
                });
        }

        function register() {
            const pseudo = document.getElementById('pseudo-input').value.trim();
            const birthDate = document.getElementById('birth-date').value;
            const birthTime = document.getElementById('birth-time').value;
            const birthCity = document.getElementById('birth-city').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const errDiv = document.getElementById('login-error');
            if (!pseudo || !birthDate || !birthTime || !birthCity) {
                errDiv.style.color = "#c97a6b";
                errDiv.textContent = T.js_err_birth;
                return;
            }
            if (!email || !email.includes('@')) {
                errDiv.style.color = "#c97a6b";
                errDiv.textContent = T.js_err_email;
                return;
            }
            const btn = document.getElementById('main-action-btn');
            if (btn) { btn.disabled = true; btn.style.opacity = '0.6'; }
            errDiv.style.color = 'var(--gold)';
            errDiv.innerHTML = '<span class="spinner"></span> ' + (T.js_register_loading || 'Création du profil…');
            const [year, month, day] = birthDate.split('-').map(Number);
            const [hour, minute] = birthTime.split(':').map(Number);
            const payload = {
                pseudo, email,
                name: pseudo,
                year, month, day, hour, minute,
                city: birthGeo ? birthGeo.city : birthCity,
                lat: birthGeo ? birthGeo.lat : 48.8566,
                lon: birthGeo ? birthGeo.lon : 2.3522,
                tz: birthGeo ? birthGeo.tz : 'Europe/Paris',
            };
            fetch(API_BASE + '/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) location.reload();
                    else {
                        errDiv.style.color = "#c97a6b";
                        errDiv.textContent = data.error;
                        if (btn) { btn.disabled = false; btn.style.opacity = ''; }
                    }
                })
                .catch(() => {
                    errDiv.style.color = "#c97a6b";
                    errDiv.textContent = T.js_err_network;
                    if (btn) { btn.disabled = false; btn.style.opacity = ''; }
                });
        }

        // ── Stripe checkout ───────────────────────────────────────────────────────────
        async function stripeCheckoutPublic(plan) {
            // if (window.Capacitor?.isNative) {
            //     await Monetization.purchase();
            //     return;
            // }
            const errEl = document.getElementById('pricing-error');
            if (errEl) errEl.style.display = 'none';
            try {
                const res = await fetch(API_BASE + '/stripe/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_type: plan })
                });
                const data = await res.json();
                if (data.url) {
                    window.location.href = data.url;
                } else {
                    if (errEl) { errEl.textContent = data.error || T.js_err_payment; errEl.style.display = 'block'; }
                    else { alert(data.error || T.js_err_payment); }
                }
            } catch (e) {
                if (errEl) { errEl.textContent = T.js_err_network; errEl.style.display = 'block'; }
                else { alert(T.js_err_network); }
            }
        }

        async function stripeCheckout(plan) {
            // if (window.Capacitor?.isNative) {
            //     await Monetization.purchase();
            //     return;
            // }
            const errEl = document.getElementById('payment-error');
            if (errEl) errEl.style.display = 'none';
            try {
                const res = await fetch(API_BASE + '/stripe/checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_type: plan })
                });
                const data = await res.json();
                if (data.url) {
                    const savedProfile = localStorage.getItem('gochara_profile');
                    const pseudo = savedProfile ? (JSON.parse(savedProfile).pseudo || '') : '';
                    if (pseudo) sessionStorage.setItem('paymentPending', pseudo);
                    window.location.href = data.url;
                } else if (data.ok && data.beta) {
                    if (errEl) errEl.style.display = 'none';
                    location.reload();
                } else {
                    if (errEl) { errEl.textContent = data.error || T.js_err_payment; errEl.style.display = 'block'; }
                    else { alert(data.error || T.js_err_payment); }
                }
            } catch (e) {
                if (errEl) { errEl.textContent = T.js_err_network; errEl.style.display = 'block'; }
                else { alert(T.js_err_network); }
            }
        }

        // Détection retour d'app après paiement dans navigateur externe (Chrome sur Android)
        document.addEventListener('visibilitychange', async () => {
            if (document.visibilityState !== 'visible') return;
            const pseudo = sessionStorage.getItem('paymentPending');
            if (!pseudo) return;
            try {
                const r = await fetch(API_BASE + '/api/plan_check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pseudo })
                });
                const d = await r.json();
                if (d.ok && d.plan) {
                    sessionStorage.removeItem('paymentPending');
                    // Recharger la page pour refléter le nouveau plan
                    window.location.href = '/?payment=success';
                }
            } catch (_) {}
        });

        function showPaymentPlans() {
            const el = document.getElementById('payment-plans');
            if (el) {
                el.style.display = 'block';
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        // ── Nettoyage sortie Gemma pour les hooks (3 phrases max, pas de markdown) ────
        function cleanHook(text) {
            if (!text) return '';
            return text
                .replace(/^#{1,3}\s*\d+[\.\:\-]\s*/gm, '')   // ## 1. ## 2. etc.
                .replace(/^\d+[\.\:\-]\s+/gm, '')              // 1. 2. 3. en début de ligne
                .replace(/\*\*([^*]+)\*\*/g, '$1')             // **bold**
                .replace(/\*([^*]+)\*/g, '$1')                 // *italic*
                .replace(/\n{2,}/g, ' ')                       // sauts de ligne multiples → espace
                .replace(/\n/g, ' ')                           // sauts de ligne simples → espace
                .replace(/\s{2,}/g, ' ')                       // espaces multiples
                .trim()
                .split(/(?<=[.!?])\s+/)                        // découpe en phrases
                .slice(0, 3)                                   // garde les 3 premières
                .join(' ');
        }

        // ── Hook natal ────────────────────────────────────────────────────────────────
        (async function initHookNatal() {
            const hook = sessionStorage.getItem('hook_natal');
            const engine = sessionStorage.getItem('hook_engine') || 'claude';
            const box = document.getElementById('hook-natal-box');
            const text = document.getElementById('hook-natal-text');
            if (!box || !text) return;

            function applyBadge(eng) {
                const badge = document.getElementById('natal-engine-badge');
                if (!badge) return;
                const provider = KarmicStore.get().customProvider;
                if (eng === 'gemma' || eng === 'chrome-ai' || provider === 'local' || eng === 'local') {
                    badge.textContent = provider === 'local' || eng === 'local' ? '☁ Phi-4 Local' : T.js_badge_local;
                    badge.style.cssText = 'background:rgba(180,140,60,0.15);color:var(--gold);border:1px solid rgba(180,140,60,0.3);';
                } else {
                    badge.textContent = T.js_badge_claude;
                    badge.style.cssText = 'background:rgba(100,120,180,0.12);color:#8899cc;border:1px solid rgba(100,120,180,0.25);';
                }
            }
            function addExpandLink() {
                if (text.nextElementSibling?.getAttribute('href') === 'expand:alternative_conscience') return;
                const link = document.createElement('a');
                link.href = 'expand:alternative_conscience';
                link.textContent = T.js_expand_link;
                link.style.display = 'block';
                link.style.marginTop = '0.8rem';
                text.after(link);
            }

            const gemmaReady = await NativeAI.isAvailable();
            if (gemmaReady) {
                box.style.display = 'block';
                text.innerHTML = '<span class="spinner"></span>';
                try {
                    const pr = await fetch(API_BASE + '/synthesis/prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ context: 'natal' })
                    });
                    const pd = await pr.json();
                    if (pd.system && pd.user) {
                        const gr = await NativeAI.generate(pd.system, pd.user);
                        if (gr && gr.synthesis) {
                            text.innerHTML = '';
                            text.textContent = cleanHook(gr.synthesis);
                            applyBadge('gemma');
                            addExpandLink();
                            sessionStorage.removeItem('hook_natal');
                            sessionStorage.removeItem('hook_engine');
                            return;
                        }
                    }
                } catch (e) { console.warn('Gemma natal fallback:', e); }
                text.innerHTML = '';
            }

            if (hook) {
                text.textContent = hook;
                applyBadge(engine);
                addExpandLink();
                box.style.display = 'block';
                sessionStorage.removeItem('hook_natal');
                sessionStorage.removeItem('hook_engine');
            }
        })();

        // ── Expand topic (1 clic limité) ──────────────────────────────────────────────
        window._expandUsed = false;

        async function expandTopic(topic) {
            if (window._expandUsed) return;
            window._expandUsed = true;

            // Grise tous les liens expand
            document.querySelectorAll('a[href^="expand:"]').forEach(a => a.classList.add('used'));

            const clickedLink = document.querySelector('a[href="expand:' + topic + '"]');
            const hookBox = document.getElementById('hook-natal-box');
            const synthBox = document.getElementById('synthesis-content');

            const expandBox = document.createElement('div');
            expandBox.className = 'expand-box';
            expandBox.innerHTML = '<span class="spinner"></span> ' + T.js_expand_loading;

            if (clickedLink) {
                clickedLink.insertAdjacentElement('afterend', expandBox);
            } else if (hookBox) {
                hookBox.querySelector('div').appendChild(expandBox);
            } else if (synthBox) {
                synthBox.appendChild(expandBox);
            }

            function buildExpandCta() {
                const saved = KarmicStore.get();
                if (CURRENT_PLAN !== 'free' || saved.customApiKey) return null;
                const cta = document.createElement('div');
                cta.className = 'expand-cta';
                cta.innerHTML =
                    '<p class="cta-label">' + T.js_cta_label + '</p>' +
                    '<p class="cta-desc">' + T.js_cta_desc + '</p>' +
                    '<button onclick="stripeCheckout(\'test\')" class="btn-primary" style="max-width:280px;margin:0 auto;">' +
                    '<span>' + T.js_cta_btn + '</span></button>';
                return cta;
            }

            try {
                const gemmaReady = await NativeAI.isAvailable();
                if (gemmaReady) {
                    const date = document.getElementById('transit-date')?.value || new Date().toISOString().slice(0, 10);
                    const pr = await fetch(API_BASE + '/synthesis/prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            context: 'conscience', date, hour: 12, minute: 0,
                            ...(transitGeo ? { transit_lat: transitGeo.lat, transit_lon: transitGeo.lon, transit_city: transitGeo.city, transit_tz: transitGeo.tz } : {})
                        })
                    });
                    const pd = await pr.json();
                    if (pd.system && pd.user) {
                        const gr = await NativeAI.generate(pd.system, pd.user);
                        if (gr && gr.synthesis) {
                            expandBox.innerHTML = marked.parse(gr.synthesis);
                            const cta = buildExpandCta();
                            if (cta) expandBox.appendChild(cta);
                            expandBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            return;
                        }
                    }
                }

                const pseudo = sessionStorage.getItem('currentPseudo') || '';
                const saved = KarmicStore.get();
                const res = await fetch(API_BASE + '/expand', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        topic, 
                        pseudo,
                        user_provider: saved.customProvider,
                        user_key: saved.customApiKey,
                        user_model: saved.customModel
                    })
                });
                const data = await res.json();
                expandBox.innerHTML = marked.parse(data.content || '_(aucun contenu)_');
                const cta = buildExpandCta();
                if (cta) expandBox.appendChild(cta);
                expandBox.scrollIntoView({ behavior: 'smooth', block: 'center' });

            } catch (err) {
                expandBox.innerHTML = '⚠ Erreur de connexion.';
                window._expandUsed = false;
                document.querySelectorAll('a[href^="expand:"]').forEach(a => a.classList.remove('used'));
            }
        }

        // Délégation clic liens expand:
        document.addEventListener('click', e => {
            const a = e.target.closest('a[href^="expand:"]');
            if (!a) return;
            e.preventDefault();
            const topic = a.getAttribute('href').replace('expand:', '');
            expandTopic(topic);
        });

        // ── Hook transit SSE ──────────────────────────────────────────────────────────
        async function requestHookTransit() {
            const date = document.getElementById('transit-date').value;
            const btn = document.getElementById('hook-btn');
            const btnText = document.getElementById('hook-btn-text');
            if (!date) { alert(T.js_err_select_date); return; }
            if (!transitGeo) { alert(T.js_err_select_loc); return; }

            const spinner = document.getElementById('hook-transit-spinner');
            const text = document.getElementById('hook-transit-text');
            const box = document.getElementById('hook-transit-box');
            const cta = document.getElementById('synthesis-cta');

            btn.disabled = true;
            btnText.innerHTML = '<span class="spinner"></span> ' + T.js_transit_loading;
            if (box) box.style.display = 'block';
            if (text) text.textContent = '';
            if (spinner) spinner.style.display = 'none';
            if (cta) cta.style.display = 'none';

            const gemmaReady = await NativeAI.isAvailable();
            if (gemmaReady) {
                btnText.innerHTML = '<span class="spinner"></span> ' + T.js_gemma_loading;
                try {
                    const pr = await fetch(API_BASE + '/synthesis/prompt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            context: 'hook_transit', date, hour: 12, minute: 0,
                            transit_lat: transitGeo.lat, transit_lon: transitGeo.lon,
                            transit_city: transitGeo.city, transit_tz: transitGeo.tz,
                        })
                    });
                    const pd = await pr.json();
                    if (pd.system && pd.user) {
                        const gr = await NativeAI.generate(pd.system, pd.user);
                        if (gr && gr.synthesis) {
                            if (text) text.textContent = cleanHook(gr.synthesis);
                            if (cta) { cta.style.display = 'block'; cta.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
                            btnText.innerHTML = T.js_transit_reread;
                            btn.disabled = false;
                            return;
                        }
                    }
                } catch (e) { console.warn('Gemma hook transit fallback:', e); }
                btnText.innerHTML = '<span class="spinner"></span> ' + T.js_transit_loading;
                if (text) text.textContent = '';
            }

            if (spinner) spinner.style.display = 'block';
            try {
                const res = await fetch(API_BASE + '/hook/transit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date, hour: 12, minute: 0,
                        transit_lat: transitGeo.lat, transit_lon: transitGeo.lon,
                        transit_city: transitGeo.city, transit_tz: transitGeo.tz,
                    })
                });
                if (!res.ok) throw new Error('Erreur réseau ' + res.status);

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                if (spinner) spinner.style.display = 'none';

                let ctaData = null;
                let nextIsCta = false;
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop();
                    for (const line of lines) {
                        if (!line.startsWith('data: ')) continue;
                        const payload = line.slice(6).trim();
                        if (payload === '[DONE]') {
                            // Show CTA if available, otherwise show synthesis button
                            if (ctaData && cta) {
                                renderHookCTA(ctaData, cta);
                            } else if (cta) {
                                cta.style.display = 'block';
                            }
                            if (cta) cta.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            btnText.innerHTML = T.js_transit_reread;
                            btn.disabled = false;
                            return;
                        }
                        if (payload.startsWith('[ERROR]')) {
                            btnText.innerHTML = '◆ VOIR LE SIGNAL DU JOUR';
                            btn.disabled = false;
                            return;
                        }
                        if (payload === '[CTA]') {
                            nextIsCta = true;
                            continue;
                        }
                        if (nextIsCta) {
                            nextIsCta = false;
                            try { ctaData = JSON.parse(payload); } catch (e) { console.error('CTA parse error:', e); }
                            continue;
                        }
                        // Regular hook text chunk
                        try { const chunk = JSON.parse(payload); if (text) text.textContent += chunk; } catch { }
                    }
                }
            } catch (e) {
                console.warn('Hook transit échoué :', e);
                btnText.innerHTML = '◆ VOIR LE SIGNAL DU JOUR';
            } finally {
                btn.disabled = false;
                if (spinner) spinner.style.display = 'none';
            }
        }

        function renderHookCTA(cta, container) {
            const lang = document.documentElement.lang || 'fr';
            const ctaText = lang === 'en' ? cta.text_en : cta.text_fr;

            if (CURRENT_PLAN === 'free') {
                container.innerHTML = `
                    <div class="cta-block">
                        <p class="cta-text">${ctaText}</p>
                    </div>
                `;
                container.style.display = 'block';
                showPaymentPlans();
            } else {
                container.style.display = 'block';
            }
        }

        function resetHookTransit() {
            const cta = document.getElementById('synthesis-cta');
            const text = document.getElementById('hook-transit-text');
            const box = document.getElementById('hook-transit-box');
            const btn = document.getElementById('hook-btn-text');
            if (cta) {
                cta.style.display = 'none';
                cta.innerHTML = `
                    <button id="calc-btn" class="btn-primary"
                        style="max-width: 300px; border-color: var(--gold); color: var(--gold);"
                        onclick="calculateWithRouting()">
                        <span id="btn-text">${T.btn_reading || 'Voir l\'analyse complète'}</span>
                    </button>
                    <div
                        style="font-family:var(--mono); font-size:0.65rem; color:var(--text-dim); letter-spacing:0.15em; margin-top:0.5rem;">
                        ${T.interp_credit || ''}
                    </div>
                `;
            }
            if (text) text.textContent = '';
            if (box) box.style.display = 'none';
            if (btn) btn.innerHTML = '◆ VOIR LE SIGNAL DU JOUR';
            document.getElementById('hook-btn').disabled = false;
            // Cacher aussi les plans paiement
            const plans = document.getElementById('payment-plans');
            if (plans) plans.style.display = 'none';
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Pré-charger la ville de transit depuis le profil sauvegardé
            if (window.SERVER_DATA && window.SERVER_DATA.transit_city && window.SERVER_DATA.transit_city !== 'null') {
                transitGeo = {
                    city: window.SERVER_DATA.transit_city,
                    lat:  window.SERVER_DATA.transit_lat,
                    lon:  window.SERVER_DATA.transit_lon,
                    tz:   window.SERVER_DATA.transit_tz,
                };
                const cityInput = document.getElementById('transit-city-input');
                if (cityInput) {
                    cityInput.value = transitGeo.city;
                    document.getElementById('geo-icon').textContent = '✓';
                }
            }

            // Restauration depuis le Store
            const saved = KarmicStore.get();
            const currentTransitDate = document.getElementById('transit-date')?.value;
            
            if (saved.lastSynthesis && saved.lastDate === currentTransitDate) {
                showSynthesis(saved.lastSynthesis, null);
                if (saved.chatHistory && saved.chatHistory.length > 0) {
                    chatHistory = saved.chatHistory;
                    chatHistory.forEach(msg => addChatBubble(msg.role, msg.content));
                }
            }


            const dateInput = document.getElementById('transit-date');
            if (dateInput) dateInput.addEventListener('change', resetHookTransit);

            const chartImg = document.getElementById('karmic-chart-img');
            if (chartImg) {
                chartImg.addEventListener('click', interpretKarmicChart);
            }
        });


        function useGeolocation() {
            const icon = document.getElementById('geo-icon');
            const input = document.getElementById('transit-city-input');
            if (!navigator.geolocation) { input.placeholder = T.js_geo_unsupported; return; }
            icon.textContent = '⏳';
            input.value = ''; input.placeholder = T.js_geo_locating; input.disabled = true;
            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    try {
                        const langCode = T.code || 'fr';
                        const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&accept-language=${langCode}`);
                        const d = await r.json();
                        const city = d.address?.city || d.address?.town || d.address?.village || d.address?.county || 'Position GPS';
                        const country = d.address?.country || '';
                        transitGeo = { lat, lon, city: `${city}, ${country}`.trim().replace(/,$/, ''), tz };
                    } catch {
                        transitGeo = { lat, lon, city: `${lat.toFixed(3)}, ${lon.toFixed(3)}`, tz };
                    }
                    icon.textContent = '✓';
                    input.value = transitGeo.city;
                    input.disabled = false;
                    resetHookTransit();
                },
                (err) => {
                    icon.textContent = '📍';
                    input.disabled = false;
                    input.value = '';
                    input.placeholder = err.code === 1 ? T.js_geo_denied : T.js_geo_error;
                },
                { timeout: 10000 }
            );
        }

        function onCityInput(val) {
            if (!val.trim()) { transitGeo = null; hideSuggestions(); return; }
            clearTimeout(_cityTimer);
            _cityTimer = setTimeout(() => fetchCitySuggestions(val.trim()), 350);
        }

        async function fetchCitySuggestions(q) {
            if (q.length < 2) return;
            try {
                const r = await fetch(`/geocode?q=${encodeURIComponent(q)}`);
                const results = await r.json();
                showSuggestions(results);
            } catch (e) { hideSuggestions(); }
        }

        function showSuggestions(results) {
            const box = document.getElementById('city-suggestions');
            if (!results.length) { hideSuggestions(); return; }
            box.innerHTML = '';
            results.forEach(item => {
                const name = item.display_name || item.name || '';
                const lat = parseFloat(item.lat);
                const lon = parseFloat(item.lon);
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                const div = document.createElement('div');
                div.textContent = name;
                div.style.cssText = 'padding:8px 12px; cursor:pointer; font-size:0.82rem; border-bottom:1px solid var(--border); color:var(--text);';
                div.onmouseenter = () => div.style.background = '#1a1a18';
                div.onmouseleave = () => div.style.background = '';
                div.onclick = () => {
                    transitGeo = { lat, lon, city: name, tz };
                    document.getElementById('transit-city-input').value = name;
                    document.getElementById('geo-icon').textContent = '✓';
                    hideSuggestions();
                    resetHookTransit();
                };
                box.appendChild(div);
            });
            box.style.display = 'block';
        }

        function hideSuggestions() { document.getElementById('city-suggestions').style.display = 'none'; }
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#transit-city-input') && !e.target.closest('#city-suggestions')) hideSuggestions();
            if (!e.target.closest('#birth-city') && !e.target.closest('#birth-city-suggestions')) hideBirthSuggestions();
        });

        // ── Autocomplétion ville de naissance ─────────────────────────────────────────
        function onBirthCityInput(val) {
            if (!val.trim()) { hideBirthSuggestions(); return; }
            clearTimeout(_birthCityTimer);
            _birthCityTimer = setTimeout(() => fetchBirthCitySuggestions(val.trim()), 350);
        }
        async function fetchBirthCitySuggestions(q) {
            if (q.length < 2) return;
            try {
                const r = await fetch(`/geocode?q=${encodeURIComponent(q)}`);
                const results = await r.json();
                showBirthSuggestions(results);
            } catch { hideBirthSuggestions(); }
        }
        function showBirthSuggestions(results) {
            const box = document.getElementById('birth-city-suggestions');
            if (!results.length) { hideBirthSuggestions(); return; }
            box.innerHTML = '';
            results.forEach(item => {
                const name = item.display_name || item.name || '';
                const lat = parseFloat(item.lat);
                const lon = parseFloat(item.lon);
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                const div = document.createElement('div');
                div.textContent = name;
                div.style.cssText = 'padding:8px 12px; cursor:pointer; font-size:0.82rem; border-bottom:1px solid var(--border); color:var(--text);';
                div.onmouseenter = () => div.style.background = '#1a1a18';
                div.onmouseleave = () => div.style.background = '';
                div.onclick = () => {
                    birthGeo = { lat, lon, city: name, tz };
                    document.getElementById('birth-city').value = name;
                    hideBirthSuggestions();
                };
                box.appendChild(div);
            });
            box.style.display = 'block';
        }
        function hideBirthSuggestions() { const b = document.getElementById('birth-city-suggestions'); if (b) b.style.display = 'none'; }

        async function sendSynthesisEmail() {
            if (!lastSynthesis) { alert('Lance d\'abord un calcul pour obtenir ta synthèse.'); return; }
            const btn = document.getElementById('btnEmail');
            const status = document.getElementById('email-status');
            btn.disabled = true;
            status.style.color = 'var(--text-dim)';
            status.textContent = T.js_email_sending;
            try {
                const res = await fetch(API_BASE + '/send_synthesis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ synthesis: lastSynthesis }),
                });
                const data = await res.json();
                if (data.ok) { status.textContent = T.js_email_sent; status.style.color = '#6a9f6a'; }
                else { status.textContent = '✗ Erreur : ' + (data.error || 'inconnu'); status.style.color = '#c06060'; }
            } catch {
                status.textContent = '✗ Erreur réseau.'; status.style.color = '#c06060';
            } finally { btn.disabled = false; }
        }

        function logout() { fetch(API_BASE + '/logout', { method: 'POST' }).then(() => location.reload()); }

        // ── Téléchargement Hors-Ligne ──────────────────────────────────────────────
        async function downloadOfflineYear() {
            const btn = document.getElementById('btn-download-offline');
            const text = document.getElementById('offline-btn-text');
            if (!btn || !text) return;
            
            btn.disabled = true;
            text.innerHTML = '<span class="spinner"></span> Téléchargement en cours... (patientez)';
            
            try {
                const year = new Date().getFullYear();
                const payload = { year };
                if (transitGeo) {
                    payload.transit_loc = transitGeo;
                }
                
                const res = await fetch(API_BASE + '/api/prefetch_year', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.error || 'Erreur réseau');
                }
                const data = await res.json();
                
                text.innerHTML = '<span class="spinner"></span> Sauvegarde en cours...';
                await OfflineStore.saveYear(data);
                
                text.innerHTML = '✅ Année ' + year + ' téléchargée !';
                setTimeout(() => {
                    if (document.getElementById('settings-modal')) closeSettings();
                }, 1500);
            } catch (err) {
                text.innerHTML = '⚠ ' + err.message;
                console.error("Erreur downloadOfflineYear:", err);
            } finally {
                btn.disabled = false;
            }
        }

        if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');


        // ── Calculate avec routage Gemma/Claude ──────────────────────────────────────
        async function calculateWithRouting() {
            const date = document.getElementById('transit-date').value;
            if (!date) return;
            const btn = document.getElementById('calc-btn');
            const btnText = document.getElementById('btn-text');
            const origText = btnText.innerHTML;
            btn.disabled = true;

            const payload = { date, hour: 12, minute: 0 };
            if (transitGeo) { payload.transit_lat = transitGeo.lat; payload.transit_lon = transitGeo.lon; payload.transit_city = transitGeo.city; payload.transit_tz = transitGeo.tz; }

            const gemmaReady = await NativeAI.isAvailable();

            try {
                // 1. Chercher dans le cache hors-ligne
                let pd = null;
                const offlineData = await OfflineStore.getDay(date);
                
                if (offlineData && offlineData.prompts) {
                    // Si on a l'année en cache, on extrait les prompts
                    pd = {
                        system: offlineData.prompts.system,
                        user: offlineData.prompts.user
                    };
                }

                if (gemmaReady) {
                    // 2A. Inférence Locale (Edge AI)
                    if (!pd) {
                        btnText.innerHTML = '<span class="spinner"></span> ' + T.js_calc_loading;
                        const pr = await fetch(API_BASE + '/synthesis/prompt', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                        pd = await pr.json();
                    }
                    if (pd.error === 'quota_exceeded') { showPaymentPlans(); return; }
                    if (pd.error) throw new Error(pd.error);
                    
                    btnText.innerHTML = '<span class="spinner"></span> ' + T.js_gemma_loading;
                    const gr = await NativeAI.generate(pd.system, pd.user);
                    showSynthesis(gr.synthesis, null);
                    showLocalBadge(true, gr.model ?? 'e2b');
                } else {
                    // 2B. Inférence Serveur
                    btnText.innerHTML = '<span class="spinner"></span> ' + T.js_calc_reading;
                    const r = await fetch(API_BASE + '/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                    const data = await r.json();
                    if (data.error === 'quota_exceeded') {
                        showPaymentPlans();
                        return;
                    }
                    if (data.error) { alert(data.error); return; }
                    showSynthesis(data.synthesis, data.remaining);
                    showLocalBadge(false);
                }
            } catch (err) {
                alert('Erreur : ' + err.message);
            } finally {
                btn.disabled = false;
                btnText.innerHTML = origText;
            }
        }

        function showSynthesis(text, remaining) {
            lastSynthesis = text;
            document.getElementById('synthesis-content').innerHTML = marked.parse(text || '');
            document.getElementById('synthesis-box').style.display = 'block';
            document.getElementById('email-status').textContent = '';
            document.getElementById('synthesis-box').scrollIntoView({ behavior: 'smooth' });
            showRatingBar();

            // Persistance de la synthèse
            KarmicStore.save({
                lastSynthesis: text,
                lastDate: document.getElementById('transit-date')?.value
            });

            chatHistory = [];
            KarmicStore.save({ chatHistory: [] });

            // Contexte transit depuis email
            if (window._emailCtx) {
                const { transit, nak, point, regime } = window._emailCtx;
                const banner = document.getElementById('transit-context-banner');
                if (banner && transit) {
                    const regimeLabels = {
                        'ROM_oppression': 'Activation ROM — test karmique',
                        'Dharma_amplification': 'Activation Dharma — opportunité',
                        'Blessure_activation': 'Activation Chiron — seuil',
                    };
                    banner.innerHTML = `⚡ <strong style="color:var(--gold)">${transit}</strong>`
                        + (nak ? ` dans <strong>${nak}</strong>` : '')
                        + (point ? ` — nakshatra de ton ${point} natal` : '')
                        + (regime ? ` &nbsp;·&nbsp; <em>${regimeLabels[regime] || regime}</em>` : '');
                    banner.style.display = 'block';
                }
            }
            initChat().then(() => {
                if (window._emailCtx) {
                    const { transit, nak, point } = window._emailCtx;
                    if (transit) {
                        const question = `${transit} est en ce moment dans ${nak || 'mon nakshatra natal'}${point ? ' — nakshatra de mon ' + point + ' natal' : ''}. Qu'est-ce que ça active concrètement pour moi ?`;
                        setTimeout(() => {
                            const input = document.getElementById('chat-input');
                            if (input && !input.disabled) {
                                input.value = question;
                                sendChatMessage();
                            }
                            window._emailCtx = null;
                        }, 800);
                    }
                }
            });
        }

        function showLocalBadge(isLocal, modelType) {
            let badge = document.getElementById('local-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.id = 'local-badge';
                badge.style.cssText = 'font-size:0.72rem;padding:2px 8px;border-radius:2px;margin-left:8px;';
                const box = document.getElementById('synthesis-box').querySelector('div');
                if (box) box.prepend(badge);
            }
            const provider = KarmicStore.get().customProvider;
            if (isLocal) { 
                badge.textContent = T.js_badge_local; 
                badge.style.cssText += 'background:#1a2a1a;color:#6ab56a;border:1px solid #2a4a2a;'; 
            } else if (provider === 'local') {
                badge.textContent = '☁ Phi-4 Local'; 
                badge.style.cssText += 'background:#1a2a1a;color:#6ab56a;border:1px solid #2a4a2a;'; 
            } else { 
                badge.textContent = '☁ Claude'; 
                badge.style.cssText += 'background:#1a1a2a;color:#9090b0;border:1px solid #2a2a4a;'; 
            }
        }

        // ── Chatbot karmique ──────────────────────────────────────────────────────────

        async function initChat() {
            const section = document.getElementById('chat-section');
            if (!section) return;
            try {
                const saved = KarmicStore.get();
                const hasCustomKey = !!saved.customApiKey;

                const r = await fetch(API_BASE + '/chat/status');
                const d = await r.json();
                const plan = d.plan || 'free';
                
                if (!hasCustomKey && (plan === 'free' || d.limit === 0)) return;
                
                section.style.display = 'block';
                
                if (hasCustomKey) {
                    updateChatQuotaLabel(999, 999, 'custom');
                } else {
                    updateChatQuotaLabel(d.remaining, d.limit, plan);
                }
            } catch (e) { /* silencieux */ }
        }

        function updateChatQuotaLabel(remaining, limit, plan) {
            const el = document.getElementById('chat-quota-label');
            if (!el) return;
            if (remaining === -1 || remaining === 999) {
                el.textContent = T.js_chat_unlimited || '∞ Questions illimitées';
            } else if (remaining <= 0) {
                el.textContent = (T.js_chat_exhausted || 'Questions épuisées (0/{limit})').replace('{limit}', limit);
                document.getElementById('chat-input').disabled = true;
                document.getElementById('chat-send-btn').disabled = true;
                const hint = document.getElementById('chat-upgrade-hint');
                if (hint) { hint.style.display = 'block'; hint.textContent = T.js_chat_upgrade_hint || 'Passe à Illimité pour continuer.'; }
            } else {
                el.textContent = (T.js_chat_remaining || '{n}/{limit} questions').replace('{n}', remaining).replace('{limit}', limit);
            }
        }

        function addChatBubble(role, text) {
            const hist = document.getElementById('chat-history');
            if (!hist) return;
            const isUser = role === 'user';
            const div = document.createElement('div');
            div.style.cssText = `display:flex; justify-content:${isUser ? 'flex-end' : 'flex-start'};`;
            const bubble = document.createElement('div');
            bubble.style.cssText = `max-width:80%; padding:0.6rem 1rem; border-radius:6px; font-size:0.95rem; line-height:1.6;
        background:${isUser ? 'rgba(201,168,76,0.15)' : 'var(--surface)'}; border:1px solid var(--border); color:var(--text);`;
            
            // Sécurité marked
            if (window.marked) bubble.innerHTML = marked.parse(text);
            else bubble.textContent = text;
            
            div.appendChild(bubble);
            hist.appendChild(div);
            hist.scrollTop = hist.scrollHeight;
        }

        async function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const btn = document.getElementById('chat-send-btn');
            const msg = input.value.trim();
            if (!msg) return;

            input.value = '';
            btn.disabled = true;
            addChatBubble('user', msg);

            const localAvailable = await NativeAI.isAvailable();
            chatHistory.push({ role: 'user', content: msg });
            KarmicStore.save({ chatHistory });

            try {
                const r = await fetch(API_BASE + '/chat/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, history: chatHistory.slice(-6), local: localAvailable }),
                });
                const d = await r.json();

                if (d.error === 'quota_exceeded') {
                    addChatBubble('assistant', T.js_chat_exhausted || 'Tu as utilisé toutes tes questions.');
                    document.getElementById('chat-input').disabled = true;
                    btn.disabled = true;
                    return;
                }
                if (d.error) { addChatBubble('assistant', '⚠ ' + d.message); btn.disabled = false; return; }

                let answer = '';
                if (d.answer) {
                    answer = d.answer;
                } else if (d.system && d.user) {
                    const gr = await NativeAI.generate(d.system, d.user);
                    answer = gr.synthesis || gr.answer || '';
                }

                chatHistory.push({ role: 'assistant', content: answer });
                KarmicStore.save({ chatHistory });
                addChatBubble('assistant', answer);
                updateChatQuotaLabel(d.remaining, null, null);
            } catch (e) {
                addChatBubble('assistant', '⚠ ' + (e.message || 'Erreur'));
            } finally {
                btn.disabled = false;
            }
        }

        // ── Alertes transit ───────────────────────────────────────────────────────────
        async function toggleAlerts(enabled) {
            const status = document.getElementById('alerts-status');
            status.textContent = T.js_alerts_updating;
            try {
                const res = await fetch(API_BASE + '/toggle_alerts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ enabled }) });
                const data = await res.json();
                if (data.ok) { status.textContent = enabled ? T.js_alerts_enabled : T.js_alerts_disabled; status.style.color = '#6a9f6a'; }
                else { status.textContent = '✗ ' + (data.error || 'Erreur'); status.style.color = '#c06060'; document.getElementById('alerts-toggle').checked = !enabled; }
            } catch { status.textContent = T.js_email_network_err; status.style.color = '#c06060'; document.getElementById('alerts-toggle').checked = !enabled; }
        }

        async function testAlert() {
            const status = document.getElementById('alerts-status');
            status.textContent = '⟳ Envoi test…'; status.style.color = 'var(--gold)';
            try {
                const res = await fetch(API_BASE + '/alert/test', { method: 'POST' });
                const data = await res.json();
                if (data.ok) { status.textContent = '✓ Email envoyé (' + data.events + ' événement(s)) → ' + data.email; status.style.color = '#6a9f6a'; }
                else { status.textContent = '✗ ' + (data.error || 'Erreur'); status.style.color = '#c06060'; }
            } catch { status.textContent = '✗ Erreur réseau'; status.style.color = '#c06060'; }
        }

        // ── Calendrier mensuel ────────────────────────────────────────────────────────
        const MONTH_FR = T.js_months;

        function toggleCalendar() { const panel = document.getElementById('calendar-panel'); calOpen = !calOpen; panel.style.display = calOpen ? 'block' : 'none'; if (calOpen) loadCalendar(); }
        function shiftMonth(delta) { calMonth += delta; if (calMonth > 12) { calMonth = 1; calYear++; } if (calMonth < 1) { calMonth = 12; calYear--; } loadCalendar(); }

        async function loadCalendar() {
            const title = document.getElementById('calendar-title'), loading = document.getElementById('calendar-loading'), content = document.getElementById('calendar-content');
            title.textContent = `${MONTH_FR[calMonth]} ${calYear}`; loading.style.display = 'block'; content.innerHTML = '';
            
            try {
                let days = {};
                // Vérifier si l'année est dans le cache hors-ligne
                const offlineYearStr = `${calYear}`; // Clé de stockage (si on veut optimiser on pourrait vérifier par mois)
                // Pour simplifier, on scanne tous les jours du mois dans OfflineStore
                const daysInMonth = new Date(calYear, calMonth, 0).getDate();
                
                let foundOffline = false;
                for (let i = 1; i <= daysInMonth; i++) {
                    const dayStr = String(i).padStart(2, '0');
                    const monthStr = String(calMonth).padStart(2, '0');
                    const dateKey = `${calYear}-${monthStr}-${dayStr}`;
                    
                    const offlineData = await OfflineStore.getDay(dateKey);
                    if (offlineData && offlineData.aspects && offlineData.aspects.length > 0) {
                        foundOffline = true;
                        // Filtrer les aspects hors-ligne
                        const filteredEvents = offlineData.aspects.filter(a => {
                            const isSlowTransit = ["Jupiter ♃", "Saturne ♄", "Uranus ♅", "Neptune ♆", "Pluton ♇", "Chiron ⚷", "Nœud Nord ☊", "Nœud Sud ☋"].includes(a.transit_planet);
                            const isTargetNatal = ["Nœud Sud ☋", "Chiron ⚷", "Nœud Nord ☊", "Soleil ☀", "Lune ☽"].includes(a.natal_planet);
                            return isSlowTransit && isTargetNatal;
                        });
                        if (filteredEvents.length > 0) {
                            days[dateKey] = filteredEvents;
                        }
                    }
                }

                if (!foundOffline) {
                    // Fallback réseau (legacy behavior)
                    const res = await fetch(`/calendar?year=${calYear}&month=${calMonth}`); 
                    const data = await res.json();
                    if (data.error) { loading.style.display = 'none'; content.innerHTML = `<p style="color:#c06060;">${data.error}</p>`; return; }
                    days = data.days || {};
                }

                loading.style.display = 'none';
                
                if (!Object.keys(days).length) { content.innerHTML = '<p style="color:var(--text-dim);text-align:center;font-size:0.85rem;">' + T.js_calendar_empty + '</p>'; return; }
                
                let html = '<div style="display:flex;flex-direction:column;gap:10px;">';
                for (const [dateKey, events] of Object.entries(days).sort()) {
                    const day = dateKey.split('-')[2];
                    html += `<div style="background:#0f0f22;border:1px solid var(--border);border-radius:3px;padding:10px 14px;"><div style="color:var(--gold);font-size:0.78rem;font-family:var(--display);margin-bottom:6px;">${day} ${MONTH_FR[calMonth]} ${calYear}</div>`;
                    
                    for (const e of events) {
                        // Mapping pour offline ou fallback
                        const tLabel = e.transit_display || e.transit_label || e.transit_planet;
                        const nLabel = e.natal_display || e.natal_label || e.natal_planet;
                        const aspectName = e.aspect || 'Conjonction'; // Par défaut conjonction si fallback serveur simple
                        const retro = e.retrograde ? '<span style="color:#c06060;margin-left:4px;">℞</span>' : '';
                        const orb = parseFloat(e.orb).toFixed(1);
                        
                        // Déterminer la couleur basée sur l'aspect
                        let aspectColor = "var(--text-dim)";
                        if (aspectName === "Conjonction") aspectColor = "var(--gold)"; // Or
                        else if (["Carré", "Opposition"].includes(aspectName)) aspectColor = "#e57373"; // Rouge
                        else if (["Trigone", "Sextile"].includes(aspectName)) aspectColor = "#6ab56a"; // Vert
                        
                        // Générer le handler de clic
                        const clickHandler = `document.getElementById('transit-date').value = '${dateKey}'; toggleCalendar(); calculateWithRouting();`;

                        html += `
                        <div onclick="${clickHandler}" style="display:flex;gap:8px;align-items:baseline;margin-top:6px;padding:6px;border-left:3px solid ${aspectColor};background:rgba(255,255,255,0.02);cursor:pointer;border-radius:2px;transition:background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background='rgba(255,255,255,0.02)'">
                            <span style="color:var(--text);font-size:0.85rem;font-weight:bold;">${tLabel}${retro}</span>
                            <span style="color:${aspectColor};font-size:0.75rem;">${aspectName.substring(0,3).toUpperCase()}</span>
                            <span style="color:var(--text);font-size:0.82rem;">${nLabel}</span>
                            <span style="color:var(--text-dim);font-size:0.72rem;margin-left:auto;">${orb}°</span>
                        </div>`; 
                    }
                    html += '</div>';
                }
                html += '</div>'; 
                content.innerHTML = html;
            } catch (err) { 
                console.error(err);
                loading.style.display = 'none'; 
                content.innerHTML = '<p style="color:#c06060;">Erreur lors du chargement du calendrier.</p>'; 
            }
        }

        async function downloadAnnualReport() {
            const btn = document.getElementById('btn-annual-report'), orig = btn.textContent; btn.disabled = true; btn.textContent = T.js_report_loading;
            try { const res = await fetch(API_BASE + '/report/annual'); if (!res.ok) { const data = await res.json().catch(() => ({})); alert('Erreur : ' + (data.error || res.statusText)); return; } const blob = await res.blob(); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `karmic_gochara_${new Date().getFullYear()}.pdf`; a.click(); URL.revokeObjectURL(url); }
            catch { alert(T.js_report_err); }
            finally { btn.disabled = false; btn.textContent = orig; }
        }

        async function interpretKarmicChart() {
            const box = document.getElementById('chart-interpretation-box');
            const textDiv = document.getElementById('chart-interpretation-text');
            const spinner = document.getElementById('chart-interpretation-spinner');
            
            if (!box || !textDiv || !spinner) return;
            
            box.style.display = 'block';
            textDiv.style.display = 'none';
            textDiv.innerHTML = '';
            spinner.style.display = 'block';
            box.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            try {
                const res = await fetch(API_BASE + '/chart/interpret', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                spinner.style.display = 'none';
                textDiv.style.display = 'block';
                if (data.ok) {
                    if (window.marked) {
                        textDiv.innerHTML = marked.parse(data.interpretation);
                    } else {
                        textDiv.innerHTML = data.interpretation.replace(/\n/g, '<br>');
                    }
                } else {
                    textDiv.innerHTML = '<span style="color:#ff6b6b;">✗ ' + (data.error || 'Erreur') + '</span>';
                }
            } catch (e) {
                spinner.style.display = 'none';
                textDiv.style.display = 'block';
                textDiv.innerHTML = '<span style="color:#ff6b6b;">✗ Erreur réseau</span>';
            }
        }
    