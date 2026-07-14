```astro
---
// src/layouts/BaseLayout.astro
import '../styles/global.css';
import '../scripts/service-worker.js'; // Assuming you have a service worker script

interface Props {
  title: string;
  description: string;
}

const { title, description } = Astro.props;
---

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Karmic Gochara</title>
  <meta name="description" content={description} />
  <link rel="icon" type="image/png" href="/static/icons/icon-192.png" />
  
  <!-- Google Fonts -->
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:wght@400;700&family=DM+Mono:wght@400;700&display=swap" rel="stylesheet">

  <!-- PWA Manifest -->
  <link rel="manifest" href="/static/manifest.json">
  
  <!-- Apple Touch Icon -->
  <link rel="apple-touch-icon" href="/static/icons/icon-192.png">

  <!-- Custom Styles -->
  <style>
    /* Base styles for layout structure */
    body {
      font-family: 'Cormorant Garamond', serif;
      background-color: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 0;
      min-height: 100vh;
      overflow-x: hidden;
    }
    
    /* Ensure the custom scrollbar is applied globally */
    ::-webkit-scrollbar {
      width: 8px;
    }
    
    ::-webkit-scrollbar-track {
      background: var(--bg);
    }
    
    ::-webkit-scrollbar-thumb {
      background: var(--gold);
      border-radius: 4px;
    }

    /* Animation for content loading */
    @keyframes fadeUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  </style>
</head>
<body>
  <main>
    <slot />
  </main>

  <!-- Service Worker Registration -->
  <script src="/static/scripts/service-worker.js"></script>
</body>
</html>
```

```css
/* src/styles/global.css */

/* --- Variables --- */
:root {
  --bg: #0c0a08;
  --gold: #c9a84c;
  --text: #f5f0e8;
  --border: #2a2820;
}

/* --- Reset & Base Styles --- */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Cormorant Garamond', serif;
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

/* --- Typography --- */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Cinzel', serif;
  color: var(--gold);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* --- Background Gradient --- */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, transparent 0%, rgba(201, 168, 76, 0.06) 100%);
  z-index: -1;
}

/* --- Scrollbar Customization (Dark Mode) --- */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg);
}

::-webkit-scrollbar-thumb {
  background: var(--gold);
  border-radius: 4px;
  border: 2px solid var(--bg);
}

::-webkit-scrollbar-thumb:hover {
  background: #e0c060; /* Slightly lighter gold on hover */
}

/* --- Keyframes --- */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* --- Content Styling Examples --- */
.card {
  background-color: var(--border);
  border: 1px solid var(--border);
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}
```