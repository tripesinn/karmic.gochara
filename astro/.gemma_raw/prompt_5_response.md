```astro
---
// src/components/HeroSection.astro
---
<section class="min-h-screen flex items-center justify-center bg-gray-950 text-white p-4 font-sans">
    <div class="max-w-4xl text-center space-y-8">
        <!-- Title -->
        <h1 class="text-7xl md:text-9xl font-display tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-yellow-300 font-cinzel">
            ✦ KARMIC GOCHARA
        </h1>

        <!-- Subtitle -->
        <p class="text-xl md:text-3xl font-cormorant text-gray-300 tracking-wider">
            L'alchimie des cycles cosmiques
        </p>

        <!-- Teaser -->
        <div class="pt-4 text-lg text-gray-400 leading-relaxed">
            <p>Explorez les influences astrologiques profondes qui façonnent votre destinée.</p>
            <p>Comprenez les transits planétaires et alignez-vous avec le flux universel.</p>
        </div>

        <!-- Button -->
        <a href="#login" 
           class="inline-block px-10 py-4 text-lg font-semibold rounded-full transition duration-300 
                  bg-gradient-to-r from-pink-600 to-purple-700 hover:from-pink-700 hover:to-purple-800 
                  text-white shadow-lg shadow-purple-500/30 transform hover:scale-105">
            S'identifier
        </a>
    </div>
</section>
```

```astro
---
// src/components/LoginCardLayout.astro
---
<div class="min-h-screen flex items-center justify-center bg-gray-950 p-4">
    <div class="w-full max-w-md bg-gray-900 border border-gray-800 rounded-xl shadow-2xl p-8 space-y-6">
        <h2 class="text-3xl font-bold text-center text-yellow-400 tracking-wider">
            Connexion
        </h2>

        <!-- Error Message -->
        <div class="text-sm text-red-400 h-5">
            <!-- Error message will appear here -->
        </div>

        <!-- Form Group: Email -->
        <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input type="email" id="email" placeholder="votre@email.com" 
                   class="w-full px-4 py-3 bg-gray-800 text-white border border-gray-700 rounded-lg 
                          focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition duration-200"
                   required>
        </div>

        <!-- Form Group: Password -->
        <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Mot de passe</label>
            <input type="password" id="password" placeholder="••••••••" 
                   class="w-full px-4 py-3 bg-gray-800 text-white border border-gray-700 rounded-lg 
                          focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500 transition duration-200"
                   required>
        </div>

        <!-- Login Button -->
        <button type="submit" 
                class="w-full py-3 mt-4 text-lg font-semibold rounded-lg 
                       bg-gradient-to-r from-yellow-500 to-amber-600 text-gray-950 
                       hover:from-yellow-600 hover:to-amber-700 transition duration-300 
                       shadow-md shadow-yellow-500/40">
            Se connecter
        </button>

        <!-- Register Toggle -->
        <div class="text-center pt-4">
            <p class="text-gray-400 text-sm">
                Pas encore de compte ? 
                <button class="text-yellow-400 font-medium hover:text-yellow-300 transition duration-200">
                    S'inscrire
                </button>
            </p>
        </div>
    </div>
</div>
```