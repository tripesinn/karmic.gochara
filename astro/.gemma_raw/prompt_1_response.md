```astro
---
// src/layouts/BaseLayout.astro
interface Props {
	title: string;
	description: string;
}

const { title, description } = Astro.props;
---

<!DOCTYPE html>
<html lang="fr">
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width" />
		<title>{title}</title>
		<meta name="description" content={description} />

		<!-- Google Fonts -->
		<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:wght@300;400;700&family=DM+Mono:wght@400;700&display=swap" rel="stylesheet">

		<!-- PWA Manifest -->
		<link rel="manifest" href="/manifest.json" />
		<meta name="theme-color" content="#0c0a08" />

		<!-- Icons -->
		<link rel="apple-touch-icon" href="/icons/icon-192.png" />

		<!-- Global Styles -->
		<link rel="stylesheet" href="/src/styles/global.css" />
	</head>
	<body class="dark-theme">
		<slot />

		<!-- Service Worker Registration -->
		<script>
			if ('serviceWorker' in navigator) {
				window.addEventListener('load', () => {
					navigator.serviceWorker.register('/sw.js')
						.then(registration => {
							console.log('SW registered: ', registration);
						})
						.catch(registrationError => {
							console.log('SW registration failed: ', registrationError);
						});
				});
			}
		</script>
	</body>
</html>
```

```css
/* src/styles/global.css */

/* ----------------------------------- */
/* 1. Variables & Reset */
/* ----------------------------------- */
:root {
	/* Color Palette */
	--bg: #0c0a08;
	--gold: #c9a84c;
	--text: #f5f0e8;
	--border: #2a2820;
	--shadow: rgba(201, 168, 76, 0.1);
}

/* Minimal Reset */
*,
*::before,
*::after {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

/* Typography Reset */
body {
	font-family: 'Cormorant Garamond', serif;
	color: var(--text);
	background-color: var(--bg);
	line-height: 1.6;
	min-height: 100vh;
	/* Subtle Gradient Background */
	background-image: linear-gradient(to bottom, var(--bg) 0%, var(--bg) 80%, rgba(201, 168, 76, 0.06) 100%);
	transition: background-color 0.5s ease;
}

h1, h2, h3, h4, h5, h6 {
	font-family: 'Cinzel', serif;
	color: var(--gold);
	letter-spacing: 0.1em;
	margin-bottom: 0.5em;
	text-transform: uppercase;
}

h1 { font-size: 3rem; }
h2 { font-size: 2.5rem; }
h3 { font-size: 1.8rem; }
h4 { font-size: 1.4rem; }
h5 { font-size: 1.1rem; }
h6 { font-size: 0.9rem; }

/* ----------------------------------- */
/* 2. Keyframes & Animations */
/* ----------------------------------- */
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

.animate-fade-up {
	animation: fadeUp 1s ease-out forwards;
}

/* ----------------------------------- */
/* 3. Custom Scrollbar (Webkit) */
/* ----------------------------------- */
body::-webkit-scrollbar {
	width: 12px;
}

body::-webkit-scrollbar-track {
	background: var(--bg);
}

body::-webkit-scrollbar-thumb {
	background-color: var(--gold);
	border-radius: 6px;
	border: 2px solid var(--bg); /* Gives a defined edge */
}

body::-webkit-scrollbar-thumb:hover {
	background-color: #e0c560; /* Slightly lighter gold on hover */
}
```