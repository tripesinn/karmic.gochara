import type { APIRoute } from 'astro';

/**
 * Mock authentication route for Karmic Gochara.
 * Accepts only 'pseudo' (min 2 chars).
 * Sets auth_token and refresh_token cookies as httpOnly.
 */
export const POST: APIRoute = async ({ request, cookies }) => {
  try {
    // Only look for the pseudo field
    const body = await request.json();
    const { pseudo } = body;

    // 1. Validation: Pseudo must exist and be at least 2 characters long
    if (!pseudo || typeof pseudo !== 'string' || pseudo.length < 2) {
      return new Response(JSON.stringify({ ok: false, error: "Le pseudo est requis et doit contenir au moins 2 caractères." }), { status: 400, headers: { 'Content-Type': 'application/json' } });
    }

    // 2. Mock Auth setup
    const mockAccessToken = 'mock_access_token_jwt_karmic_gochara';
    const mockRefreshToken = 'mock_refresh_token_jwt_karmic_gochara';

    // 3. Set httpOnly cookies
    // MaxAge 15 minutes (auth_token)
    cookies.set('auth_token', mockAccessToken, { path: '/', httpOnly: true, secure: true, sameSite: 'strict', maxAge: 60 * 15 });
    // MaxAge 7 days (refresh_token)
    cookies.set('refresh_token', mockRefreshToken, { path: '/', httpOnly: true, secure: true, sameSite: 'strict', maxAge: 60 * 60 * 24 * 7 });

    // 4. Successful response: {ok: true, pseudo, token}
    return new Response(JSON.stringify({ ok: true, pseudo: pseudo, token: mockAccessToken }), { status: 200, headers: { 'Content-Type': 'application/json' } });

  } catch (error) {
    console.error("Erreur d'authentification:", error);
    // 5. Failure response: {ok: false, error}
    return new Response(JSON.stringify({ ok: false, error: "Une erreur interne est survenue lors de la connexion." }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }
};
