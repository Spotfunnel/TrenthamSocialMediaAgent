export default async function handler(req, res) {
  const { id } = req.query;
  if (!id) return res.status(400).json({ error: 'Missing draft id' });

  const PAT = process.env.AIRTABLE_PAT;
  const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const BASE = 'app3fWPgMxZlPYSgA';
  const TABLE = 'tblhwcZsM7wh85HFq'; // V2 Drafts

  try {
    const response = await fetch(
      `https://api.airtable.com/v0/${BASE}/${TABLE}/${id}`,
      { headers: { 'Authorization': `Bearer ${PAT}` } }
    );
    const data = await response.json();

    if (data.error) return res.status(404).json({ error: 'Draft not found' });

    const f = data.fields || {};

    // Resolve photo URLs
    let photos = [];
    if (f.image_url) {
      photos = f.image_url.split(',').map(s => s.trim()).filter(Boolean);
    }
    if (photos.length === 0 && f.photo_file_ids && BOT_TOKEN) {
      const fileIds = f.photo_file_ids.split(',').map(s => s.trim()).filter(Boolean);
      for (const fid of fileIds) {
        try {
          const fr = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fid}`);
          const fd = await fr.json();
          if (fd.ok && fd.result.file_path) {
            photos.push(`https://api.telegram.org/file/bot${BOT_TOKEN}/${fd.result.file_path}`);
          }
        } catch(e) {}
      }
    }

    let igCaption = f.content_ig || '';

    const preview = {
      posts: [{
        label: (f.content_brief || 'Post Preview').substring(0, 150),
        photos: photos,
        instagram: igCaption ? { caption: igCaption } : null,
        gbp: f.content_gbp ? { body: f.content_gbp } : null,
        facebook: (f.content_fb || igCaption) ? { caption: f.content_fb || igCaption } : null
      }]
    };

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).json(preview);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
