// Writes rep feedback onto the Cadence Brief record (rep_feedback / variant_copied).
// Called from CadenceBriefCard.tsx via hubspot.serverless('record_feedback', {...}).
//
// Runs server-side inside HubSpot with the app's access token
// (PRIVATE_APP_ACCESS_TOKEN is injected for static-auth private apps).
// Only whitelisted properties can be written — this function is not a generic
// record editor.

// Enum fields: both the property AND the value are whitelisted.
const ALLOWED_ENUM = new Set(['rep_feedback', 'variant_copied']);
const ALLOWED_VALUES = new Set(['none', 'up', 'down', 'primary', 'softer']);

// Free-text fields: the property is whitelisted, the value is validated by type and length instead of
// an enum. Kept separate so this never becomes a generic record editor.
const ALLOWED_TEXT = new Set(['rep_feedback_detail']);
const MAX_TEXT = 5000;

exports.main = async (context) => {
  const { objectTypeId, objectId, property, value } = context.parameters || {};

  if (!objectTypeId || !objectId) {
    throw new Error('Missing objectTypeId/objectId');
  }

  if (ALLOWED_TEXT.has(property)) {
    if (typeof value !== 'string') {
      throw new Error(`${property} must be a string.`);
    }
    if (value.length > MAX_TEXT) {
      throw new Error(`${property} is too long (${value.length} > ${MAX_TEXT}).`);
    }
  } else if (!ALLOWED_ENUM.has(property) || !ALLOWED_VALUES.has(value)) {
    throw new Error(`Refusing to write ${property}=${value} — not a whitelisted feedback field.`);
  }

  const token = process.env.PRIVATE_APP_ACCESS_TOKEN;
  if (!token) {
    throw new Error('PRIVATE_APP_ACCESS_TOKEN not available to the function.');
  }

  const res = await fetch(
    `https://api.hubapi.com/crm/v3/objects/${objectTypeId}/${objectId}`,
    {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ properties: { [property]: value } }),
    },
  );

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`HubSpot API ${res.status}: ${detail}`);
  }
  return { ok: true, property, value };
};
