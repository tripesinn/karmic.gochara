import type { APIRoute } from 'astro';

export const POST: APIRoute = async ({ request, cookies }) => {
  try {
    // 1. Récupération des données du corps de la requête
    const body = await request.json();
    const { pseudo, email, birthDate } = body;

    // 2. Validation simple des champs requis
    if (!pseudo || !email || !birthDate) {
      return new Response(
        JSON.stringify({ 
          error: "Tous les champs (Pseudo, Email, Date de naissance) sont requis." 
        }),
        { 
          status: 400, 
          headers: { "Content-Type": "application/json" } 
        }
      );
    }

    // 3. Simulation de validation (Mock)
    // Pour les besoins du mock, on accepte n'importe quelle adresse email valide.
    // On simule ici la création d'un JWT d'accès et d'un token de rafraîchissement.
    const mockAccessToken = "mock_access_token_jwt_karmic_gochara";
    const mockRefreshToken = "mock_refresh_token_jwt_karmic_gochara";

    // 4. Stockage des jetons dans des cookies sécurisés HttpOnly via l'API Astro
    cookies.set("auth_token", mockAccessToken, {
      path: "/",
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      maxAge: 60 * 15, // 15 minutes
    });

    cookies.set("refresh_token", mockRefreshToken, {
      path: "/",
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      maxAge: 60 * 60 * 24 * 7, // 7 jours
    });

    // 5. Réponse de succès
    return new Response(
      JSON.stringify({
        success: true,
        message: "Connexion réussie.",
        user: { pseudo, email }
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" }
      }
    );

  } catch (error) {
    console.error("Erreur d'authentification:", error);
    return new Response(
      JSON.stringify({ 
        error: "Une erreur interne est survenue lors de la connexion." 
      }),
      { 
        status: 500, 
        headers: { "Content-Type": "application/json" } 
      }
    );
  }
};