export const config = { runtime: 'edge' };

export default async function handler(request) {
  const url = new URL(request.url);
  const youtubeUrl = url.searchParams.get('url');
  const type = url.pathname.includes('/audio') ? 'mp3' : 'mp4';
  
  if (!youtubeUrl) {
    return new Response(JSON.stringify({ error: 'URL não fornecida' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Extrair ID
  let videoId = '';
  if (youtubeUrl.includes('youtu.be/')) {
    videoId = youtubeUrl.split('youtu.be/')[1].split('?')[0];
  } else if (youtubeUrl.includes('v=')) {
    videoId = youtubeUrl.split('v=')[1].split('&')[0];
  }
  
  if (!videoId) {
    return new Response(JSON.stringify({ error: 'URL inválida' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Redirecionar para serviço que FUNCIONA
  const redirectUrl = type === 'mp3' 
    ? `https://onlinevideoconverter.pro/pt/youtube-converter?v=${videoId}&t=mp3`
    : `https://onlinevideoconverter.pro/pt/youtube-converter?v=${videoId}&t=mp4`;
  
  return Response.redirect(redirectUrl, 302);
}
