curl -s http://127.0.0.1:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "model": "unsloth--gemma-4-E4B-it-UD-MLX-4bit",
  "messages": [
    {
      "role": "user",
      "content": "Réécris ce fichier Astro pour qu'il accepte UNIQUEMENT le champ pseudo (au moins 2 caractères). Pas d'email ni birthDate. Mock auth — retourne {ok: true, pseudo, token} si ok, sinon {ok: false, error}. Garde les cookies httpOnly auth_token et refresh_token. Code TypeScript complet, pas de troncature.\n\nVoici le code actuel :\n\nimport type { APIRoute } from 'astro';\n\nexport const POST: APIRoute = async ({ request, cookies }) => {\n  try {\n    const body = await request.json();\n    const { pseudo, email, birthDate } = body;\n    if (!pseudo || !email || !birthDate) {\n      return new Response(JSON.stringify({ error: \"Tous les champs (Pseudo, Email, Date de naissance) sont requis.\" }), { status: 400, headers: { 'Content-Type': 'application/json' } });\n    }\n    const mockAccessToken = 'mock_access_token_jwt_karmic_gochara';\n    const mockRefreshToken = 'mock_refresh_token_jwt_karmic_gochara';\n    cookies.set('auth_token', mockAccessToken, { path: '/', httpOnly: true, secure: true, sameSite: 'strict', maxAge: 60 * 15 });\n    cookies.set('refresh_token', mockRefreshToken, { path: '/', httpOnly: true, secure: true, sameSite: 'strict', maxAge: 60 * 60 * 24 * 7 });\n    return new Response(JSON.stringify({ success: true, message: 'Connexion réussie.', user: { pseudo, email } }), { status: 200, headers: { 'Content-Type': 'application/json' } });\n  } catch (error) {\n    console.error(\"Erreur d'authentification:\", error);\n    return new Response(JSON.stringify({ error: \"Une erreur interne est survenue lors de la connexion.\" }), { status: 500, headers: { 'Content-Type': 'application/json' } });\n  }\n};"
    }
  ],
  "temperature": 0.2
}
EOF