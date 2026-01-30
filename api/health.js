export const config = {
  runtime: 'edge',
};

export default async function handler(request) {
  return new Response(JSON.stringify({
    status: 'online',
    service: 'ByteForgeYT',
    timestamp: new Date().toISOString(),
    runtime: 'edge'
  }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache'
    }
  });
}
