```astro
---
// src/pages/index.astro
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="Karmic Gochara">
  <main class="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
    
    <!-- Hero Section -->
    <section class="text-center max-w-4xl mx-auto py-20">
      <div class="text-7xl mb-6 animate-pulse">✨</div>
      <h1 class="text-6xl font-extrabold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-4">
        ✦ Karmic Gochara
      </h1>
      <p class="text-xl text-gray-300 mb-12">
        Ta carte karmique en transit. Dévoile les cycles cosmiques qui façonnent ton destin.
      </p>
      
      <!-- Scroll CTA -->
      <div class="mt-10">
        <a href="#login-cta" class="inline-flex items-center px-8 py-4 text-lg font-semibold rounded-full shadow-lg transition duration-300 
          bg-purple-600 hover:bg-purple-700 text-white transform hover:scale-105">
          Accéder à ma carte
          <svg class="ml-3 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
        </a>
      </div>
    </section>

    <!-- Placeholder for Login CTA (where client:load component would go) -->
    <div id="login-cta" class="w-full max-w-md text-center mt-16 p-8 border border-purple-500 rounded-xl bg-gray-800 shadow-2xl">
        <h2 class="text-3xl font-bold text-purple-400 mb-4">Prêt à voir ton chemin ?</h2>
        <p class="text-gray-400 mb-6">Connecte-toi pour une lecture karmique personnalisée.</p>
        <!-- This is where the client:load login card would be placed -->
        <button class="px-6 py-3 bg-pink-600 hover:bg-pink-700 rounded-lg font-semibold transition">
            Se Connecter
        </button>
    </div>

  </main>
</BaseLayout>
```

---
```astro
---
// src/pages/404.astro
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="404 - Page Mystère">
  <main class="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4 text-center">
    
    <!-- Cosmic Theme Elements -->
    <div class="text-9xl mb-8 animate-pulse">🌌</div>
    
    <h1 class="text-8xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500 mb-4">
      Page Mystère...
    </h1>
    
    <p class="text-xl text-gray-400 mb-10 max-w-2xl">
      L'univers t'a envoyé à un endroit non cartographié. Il semble que cette page n'existe pas dans nos constellations.
    </p>
    
    <!-- Link to Home -->
    <a href="/" class="inline-flex items-center px-8 py-4 text-lg font-semibold rounded-full shadow-lg transition duration-300 
      bg-purple-600 hover:bg-purple-700 text-white transform hover:scale-105">
      Retour à l'Horizon
    </a>

  </main>
</BaseLayout>
```