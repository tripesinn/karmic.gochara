// src/pages/api/doctrine.ts

/**
 * API Endpoint for serving daily spiritual and karmic insights.
 * This simulates the call to doctrine.py or a database/AI inference engine.
 * Since this runs server-side (SSR/Build time), it must return a standard Response object.
 */
export async function GET() {
  // Simulate a network delay/complex calculation
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Mock Data for a Karmic/Astrological Reading
  const mockData = {
    title: "Transit de la Lune sur la Maison V",
    date: new Date().toLocaleDateString('fr-FR'),
    text: "Aujourd'hui, les transits lunaires suggèrent que votre énergie est orientée vers la créativité et la joie. Concentrez-vous sur les plaisirs simples et les expressions authentiques. Le karma de cette période est la légèreté.",
    isKarmic: true, // Indicateur d'une forte résonance karmique
    focus_area: "Créativité & Joie",
    recommendation: "Autorisez-vous à vous amuser sans jugement. L'énergie vous y invite.",
    rating: 8.5 // 1 à 10
  };

  // Return the data as a JSON response
  return new Response(
    JSON.stringify(mockData),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
}