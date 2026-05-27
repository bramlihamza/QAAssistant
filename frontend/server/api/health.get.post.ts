/**
 * GET /api/health
 * Vérifie l'état de santé de l'API
 */

export default defineEventHandler(async (event) => {
  const checks = {
    api: "✅ OK",
    openai_api_key: process.env.OPENAI_API_KEY ? "✅ Configured" : "❌ Missing",
    pinecone_api_key: process.env.PINECONE_API_KEY ? "✅ Configured" : "❌ Missing",
    pinecone_index: process.env.PINECONE_INDEX ? "✅ Configured" : "❌ Missing",
  };

  const allOk = Object.values(checks).every((v) => v.includes("✅"));

  return {
    status: allOk ? "healthy" : "degraded",
    checks,
    timestamp: new Date().toISOString(),
    version: "0.1.0",
  };
});
