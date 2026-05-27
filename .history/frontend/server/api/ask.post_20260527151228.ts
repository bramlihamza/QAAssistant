/**
 * POST /api/ask
 * Génère des cas de test via l'agent QA
 */

export default defineEventHandler(async (event) => {
  try {
    // Récupérer le body
    const body = await readBody(event);
    const question = body?.question?.trim();

    if (!question) {
      throw createError({
        statusCode: 400,
        statusMessage: "question est obligatoire",
      });
    }

    // Vérifier les clés API
    const openaiKey = process.env.OPENAI_API_KEY;
    const pineconeKey = process.env.PINECONE_API_KEY;

    if (!openaiKey || !pineconeKey) {
      throw createError({
        statusCode: 500,
        statusMessage: "API keys not configured",
      });
    }

    // Stub response (agent à intégrer)
    return {
      status: "success",
      question,
      answer: "Endpoint /api/ask opérationnel sur Vercel.",
      test_cases: [],
      warnings: ["⚠️  Agent QA en cours d'intégration"],
      sources: [],
      requires_human_validation: true,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.error("Error in /api/ask:", error);
    throw createError({
      statusCode: 500,
      statusMessage: error.message || "Internal server error",
    });
  }
});
