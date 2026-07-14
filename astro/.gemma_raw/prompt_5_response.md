```astro
---
// src/components/HeroSection.astro
import type { AstroComponent } from 'astro/types';

const HeroSection: AstroComponent = () => {
    return (
        <section class="bg-gray-900 text-white py-20 px-4 min-h-screen flex flex-col items-center justify-center text-center">
            <div class="max-w-4xl">
                <h1 class="text-6xl md:text-8xl font-cinzel font-bold mb-4 tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-600">
                    ✦ KARMIC GOCHARA
                </h1>
                <p class="text-xl md:text-2xl font-serif font-light mb-8 text-gray-300">
                    <span class="font-cormorant text-amber-300">L'éveil de votre potentiel.</span>
                </p>
                <p class="text-lg text-gray-400 mb-10 max-w-2xl mx-auto">
                    Découvrez une nouvelle dimension de croissance personnelle et de conscience. Accédez à votre chemin.
                </p>
                <a href="/login" class="inline-block bg-amber-500 hover:bg-amber-600 text-gray-900 font-bold py-3 px-8 rounded-lg transition duration-300 shadow-lg transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-amber-500/50">
                    S'identifier
                </a>
            </div>
        </section>
    );
};

export default HeroSection;
```

```astro
---
// src/components/LoginCardLayout.astro
import type { AstroComponent } from 'astro/types';

const LoginCardLayout: AstroComponent = () => {
    return (
        <div class="min-h-screen bg-gray-900 flex items-center justify-center p-4">
            <div class="w-full max-w-md bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700">
                <h2 class="text-3xl font-bold text-center mb-6 text-amber-400">Connexion</h2>

                <form class="space-y-6">
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Adresse e-mail</label>
                        <input
                            type="email"
                            id="email"
                            placeholder="votre@email.com"
                            class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition duration-200"
                            required
                        />
                    </div>

                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Mot de passe</label>
                        <input
                            type="password"
                            id="password"
                            placeholder="••••••••"
                            class="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition duration-200"
                            required
                        />
                    </div>

                    <div class="flex justify-between items-center">
                        <button type="submit" class="w-full bg-amber-500 hover:bg-amber-600 text-gray-900 font-bold py-3 rounded-lg transition duration-300 shadow-md">
                            Se connecter
                        </button>
                    </div>

                    <div class="text-center pt-4">
                        <p class="text-sm text-gray-400">
                            Pas encore inscrit ? 
                            <a href="#" class="text-amber-400 hover:text-amber-300 font-medium ml-1">Créer un compte</a>
                        </p>
                    </div>
                </form>

                <div class="mt-6 pt-4 border-t border-gray-700">
                    <button class="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 py-2 rounded-lg transition duration-300 text-sm">
                        S'inscrire
                    </button>
                </div>

                <div class="mt-4 text-center">
                    <div class="h-4 w-1/2 bg-gray-700 rounded mx-auto mb-2"></div>
                    <p class="text-xs text-gray-500">
                        Vous avez oublié vos identifiants ? 
                        <a href="#" class="text-amber-400 hover:text-amber-300">Réinitialisation</a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginCardLayout;
```