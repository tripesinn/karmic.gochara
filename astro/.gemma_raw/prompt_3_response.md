```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="Karmic Gochara">
    <main class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
        <div class="text-center max-w-4xl">
            <h1 class="text-6xl md:text-8xl font-extrabold mb-4 text-yellow-400 tracking-wider">
                ✦ Karmic Gochara
            </h1>
            <p class="text-xl md:text-2xl text-gray-300 mb-10 italic">
                Ta carte karmique en transit
            </p>

            <!-- Sigil SVG Emoji -->
            <div class="text-7xl mb-12 animate-pulse">
                ✨
            </div>

            <!-- Scroll CTA -->
            <a href="/login" class="inline-block bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition duration-300 shadow-lg transform hover:scale-105">
                Accéder à la carte
            </a>
        </div>
    </main>
</BaseLayout>
```

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="404 - Page Mystère">
    <main class="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-900 text-center">
        <div class="max-w-md">
            <h1 class="text-7xl mb-6 text-red-500">
                404
            </h1>
            <p class="text-2xl text-gray-300 mb-8">
                Page mystère...
            </p>
            <p class="text-lg mb-8 text-yellow-400">
                Le chemin s'est égaré dans les cycles cosmiques.
            </p>
            <a href="/" class="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-300">
                Retour à l'origine
            </a>
        </div>
    </main>
</BaseLayout>
```