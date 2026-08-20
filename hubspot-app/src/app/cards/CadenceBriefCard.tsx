import { useCallback, useEffect, useState } from 'react';
import {
  Accordion,
  Alert,
  Button,
  ButtonRow,
  DescriptionList,
  DescriptionListItem,
  Divider,
  Flex,
  Heading,
  Link,
  List,
  LoadingSpinner,
  StatusTag,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Tag,
  Text,
  TextArea,
  hubspot,
} from '@hubspot/ui-extensions';

// The Cadence Agent card — renders one Cadence Brief record.
// Reads the record's own properties (platform-scoped: a rep only ever opens
// records they own — see the permission set in ../../README.md). Writes
// (rep_feedback / variant_copied) go through the recordFeedback app function,
// which uses the app token server-side.

const PROPS = [
  'company_name',
  'domain',
  'score',
  'score_band',
  'status',
  'vertical',
  'persona',
  'locations',
  'why_now',
  'signals_json',
  'contacts_json',
  'first_touch_subject',
  'first_touch_body',
  'first_touch_alt_subject',
  'first_touch_alt_body',
  'first_touch_rationale',
  'evidence_backed',
  'anti_ai_passed',
  'cadence_template',
  'gong_template_url',
  'rep_feedback',
  'rep_feedback_detail',
  'variant_copied',
  'first_touch_basis',
  'conjunctural_signal',
  'brief_json',
  'last_run',
];

// Structured supplement to the prose properties, so guidance text can render as scannable components
// rather than paragraphs (rep feedback 2026-08-13 — same fix already applied to the Reactivation card).
// Every field is optional and every section falls back to the legacy prose property, so the 90+ briefs
// written before this existed keep rendering.
interface BriefMeta {
  why_now?: { headline?: string; points?: string[] };
  coordinate?: {
    owner?: string;
    last_contacted?: string;
    days_ago?: number;
    deals?: number;
    note?: string;
  };
  corrections?: string[];
  copy_rationale?: { hook?: string; proof?: string; persona?: string; vertical?: string };
}

const LABELS: Record<string, string> = {
  coffee_cafe: 'Coffee & Cafe',
  fast_casual: 'Fast Casual',
  fsr: 'FSR',
  qsr: 'QSR',
  csuite: 'C-Suite',
  finance: 'Finance',
  founder: 'Founder',
  operations: 'Operations',
  queued: 'Queued',
  scored: 'Scored',
  ready: 'Ready to launch',
  in_cadence: 'In cadence',
  high: 'High priority',
  medium: 'Medium',
  low: 'Low',
  thin: 'Thin',
};

interface Signal {
  // canonical shape (what score_accounts.py consumes and the pipeline writes)
  signal?: string;
  present?: boolean;
  strength?: number;
  recency_days?: number;
  confidence?: string;
  hook_detail?: string;
  note?: string;
  evidence?: string;
  stage?: string;
  scored?: boolean;
  scored_reason?: string;
  // legacy shape (older briefs)
  type?: string;
  title?: string;
  detail?: string;
  date?: string;
  source_url?: string;
}

const SIGNAL_LABELS: Record<string, string> = {
  new_location: 'New locations',
  leadership_hire: 'Leadership hire',
  funding: 'Funding / M&A',
  open_jobs: 'Open corporate jobs',
};

// What the opener was built on. Shown so a rep can judge the draft — and so the learning loop can
// compare reply rates by basis (conjunctural is an unproven experiment, see knowledge/conjunctural/).
const BASIS_LABELS: Record<string, string> = {
  account_signal: 'Built on an account signal',
  conjunctural: 'Built on an industry signal',
  vertical_pain: 'Built on the vertical pain (no signal found)',
};

// Pre-opening stages are the more actionable ones — see directives/signals/new_location.md
const STAGE_LABELS: Record<string, string> = {
  permit_filed: 'Permit / licence filed',
  announced: 'Announced',
  fit_out: 'In fit-out',
  opened: 'Open',
};

const signalLabel = (s: Signal) =>
  s.title || SIGNAL_LABELS[s.signal || s.type || ''] || s.signal || s.type || 'Signal';

interface FlowContact {
  id?: string;
  name?: string;
  title?: string | null;
  email?: string;
  reason?: string;
}

interface ContactMap {
  generated?: string;
  total_contacts?: number;
  mapped?: number;
  groups?: { flow: string; persona?: string; suite?: string; contacts: FlowContact[]; truncated?: number }[];
  unmapped?: FlowContact[];
}

hubspot.extend<'crm.record.tab'>(({ context, actions }) => (
  <CadenceBriefCard context={context} actions={actions} />
));

function CadenceBriefCard({ context, actions }: { context: any; actions: any }) {
  const [p, setP] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string>('none');
  const [showSofter, setShowSofter] = useState(false);
  const [busy, setBusy] = useState(false);
  // Detail box opens on 👎. This is the highest-value input to the learning loop — it captures WHY a
  // draft was wrong, which a thumbs-down alone never tells us.
  const [showDetail, setShowDetail] = useState(false);
  const [detail, setDetail] = useState('');
  const [detailSaved, setDetailSaved] = useState(false);

  useEffect(() => {
    actions
      .fetchCrmObjectProperties(PROPS)
      .then((props: Record<string, string>) => {
        setP(props);
        setFeedback(props.rep_feedback || 'none');
        if (props.rep_feedback_detail) {
          setDetail(props.rep_feedback_detail);
          setDetailSaved(true);
        }
        if (props.rep_feedback === 'down') setShowDetail(true);
      })
      .catch((e: Error) => setError(e.message));
    // Live-refresh when the agent updates the record.
    if (actions.onCrmPropertiesUpdate) {
      actions.onCrmPropertiesUpdate(PROPS, (props: Record<string, string>) =>
        setP((prev) => ({ ...prev, ...props })),
      );
    }
  }, [actions]);

  const writeProperty = useCallback(
    async (property: string, value: string) => {
      setBusy(true);
      try {
        await hubspot.serverless('record_feedback', {
          parameters: {
            objectTypeId: context.crm?.objectTypeId,
            objectId: context.crm?.objectId,
            property,
            value,
          },
        });
        return true;
      } catch (e) {
        actions.addAlert({
          type: 'warning',
          message: 'Could not save — try again or note it in the weekly digest.',
        });
        return false;
      } finally {
        setBusy(false);
      }
    },
    [actions, context],
  );

  const copyEmail = useCallback(
    async (variant: 'primary' | 'softer') => {
      if (!p) return;
      const subject = variant === 'softer' ? p.first_touch_alt_subject : p.first_touch_subject;
      const body = variant === 'softer' ? p.first_touch_alt_body : p.first_touch_body;
      const text = `Subject: ${subject}\n\n${body}`;
      try {
        await actions.copyTextToClipboard(text);
        actions.addAlert({ type: 'success', message: 'Email copied — paste into the Gong Email 1 slot.' });
      } catch {
        actions.addAlert({
          type: 'info',
          message: 'Clipboard unavailable — select the email text and copy manually.',
        });
      }
      // Which variant the rep uses = preference data for the learning loop.
      writeProperty('variant_copied', variant);
    },
    [p, actions, writeProperty],
  );

  const giveFeedback = useCallback(
    async (value: 'up' | 'down') => {
      const next = feedback === value ? 'none' : value;
      const ok = await writeProperty('rep_feedback', next);
      if (ok) {
        setFeedback(next);
        setShowDetail(next === 'down');
        if (next === 'up') {
          actions.addAlert({ type: 'success', message: 'Logged as a good draft — feeds the learning loop.' });
        }
        // On 👎 we don't toast — the detail box opens instead and asks the useful question.
      }
    },
    [feedback, writeProperty, actions],
  );

  const saveDetail = useCallback(async () => {
    const text = detail.trim();
    if (!text) return;
    const ok = await writeProperty('rep_feedback_detail', text);
    if (ok) {
      setDetailSaved(true);
      actions.addAlert({
        type: 'success',
        message: 'Thanks — that goes straight into how the next draft gets written.',
      });
    }
  }, [detail, writeProperty, actions]);

  if (error) {
    return <Alert title="Could not load the brief" variant="error">{error}</Alert>;
  }
  if (!p) {
    return <LoadingSpinner label="Loading cadence brief…" />;
  }

  const score = Number(p.score || 0);
  const signals: Signal[] = (() => {
    try {
      const parsed = JSON.parse(p.signals_json || '[]');
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  })();
  const contactMap: ContactMap = (() => {
    try {
      const parsed = JSON.parse(p.contacts_json || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  })();
  const meta: BriefMeta = (() => {
    try {
      const parsed = JSON.parse(p.brief_json || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  })();
  const isQueued = (p.status || 'queued') === 'queued';
  // HubSpot date properties arrive as epoch-ms strings — show YYYY-MM-DD, not 1786406400000.
  const lastRun = (() => {
    if (!p.last_run) return '—';
    const d = new Date(Number(p.last_run) || p.last_run);
    return isNaN(d.getTime()) ? p.last_run : d.toISOString().slice(0, 10);
  })();
  const subject = showSofter ? p.first_touch_alt_subject : p.first_touch_subject;
  const body = showSofter ? p.first_touch_alt_body : p.first_touch_body;
  const hasSofter = Boolean(p.first_touch_alt_body);

  if (isQueued) {
    return (
      <Flex direction="column" gap="md">
        <Flex direction="row" gap="sm">
          <Tag>{LABELS[p.vertical] || p.vertical}</Tag>
          <Tag>{LABELS[p.persona] || p.persona}</Tag>
          <Tag>Queued</Tag>
        </Flex>
        <Text>
          No Tier-1 signals confirmed yet. The signal hunters run on the next pass — once anything lands
          (new hire, funding, jobs, a new site), this account gets scored and a bespoke first touch is
          drafted here.
        </Text>
      </Flex>
    );
  }

  return (
    <Flex direction="column" gap="md">
      {/* Score + classification */}
      <Flex direction="row" justify="between" align="center">
        <Heading>{score}/100 — {LABELS[p.score_band] || p.score_band || ''}</Heading>
        <Flex direction="row" gap="sm">
          <Tag>{LABELS[p.vertical] || p.vertical}</Tag>
          <Tag>{LABELS[p.persona] || p.persona}</Tag>
          <Tag>{LABELS[p.status] || p.status}</Tag>
        </Flex>
      </Flex>
      {/* WHY NOW — headline + bullets when structured; legacy prose otherwise. */}
      {meta.why_now?.headline || (meta.why_now?.points || []).length ? (
        <Flex direction="column" gap="sm">
          {meta.why_now?.headline && (
            <Text format={{ fontWeight: 'bold' }}>Why now: <Text inline>{meta.why_now.headline}</Text></Text>
          )}
          {(meta.why_now?.points || []).length > 0 && (
            <List variant="unordered">
              {(meta.why_now?.points || []).map((pt, i) => (
                <Text key={i}>{pt}</Text>
              ))}
            </List>
          )}
        </Flex>
      ) : (
        <Text format={{ fontWeight: 'bold' }}>Why now: <Text inline>{p.why_now}</Text></Text>
      )}

      {/* Coordination risk deserves its own alert — buried in a paragraph it gets skimmed past, and
          sending over a colleague's live thread is the most expensive mistake this card can allow. */}
      {meta.coordinate && (meta.coordinate.owner || meta.coordinate.note) && (
        <Alert title="Coordinate before you send" variant="warning">
          <DescriptionList direction="row">
            {meta.coordinate.owner && (
              <DescriptionListItem label="Record owner">
                <Text format={{ fontWeight: 'bold' }}>{meta.coordinate.owner}</Text>
              </DescriptionListItem>
            )}
            {meta.coordinate.last_contacted && (
              <DescriptionListItem label="Last contacted">
                <Text>
                  {meta.coordinate.last_contacted}
                  {meta.coordinate.days_ago != null ? ` (${meta.coordinate.days_ago} days ago)` : ''}
                </Text>
              </DescriptionListItem>
            )}
            {meta.coordinate.deals != null && (
              <DescriptionListItem label="Deals on record">
                <Text>{meta.coordinate.deals}</Text>
              </DescriptionListItem>
            )}
          </DescriptionList>
          {meta.coordinate.note && <Text>{meta.coordinate.note}</Text>}
        </Alert>
      )}

      {/* Data corrections — short, and only where the CRM/enrichment is actually wrong. */}
      {(meta.corrections || []).length > 0 && (
        <Accordion title={`Data corrections (${(meta.corrections || []).length})`} defaultOpen={false}>
          <List variant="unordered">
            {(meta.corrections || []).map((c, i) => (
              <Text key={i}>{c}</Text>
            ))}
          </List>
        </Accordion>
      )}
      <Divider />

      {/* Signals — found ones in the table, checked-but-absent ones as an honest note */}
      <Heading>The signals</Heading>
      {(() => {
        const found = signals.filter((s) => s.present !== false);
        const notFound = signals.filter((s) => s.present === false);
        return (
          <>
            {found.length === 0 ? (
              <Text variant="microcopy">No Tier-1 signal in window.</Text>
            ) : (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeader>Signal</TableHeader>
                    <TableHeader>Detected</TableHeader>
                    <TableHeader>Confidence</TableHeader>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {found.map((s, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <Flex direction="row" gap="sm" align="center">
                          <Text format={{ fontWeight: 'bold' }}>{signalLabel(s)}</Text>
                          {s.stage && <Tag>{STAGE_LABELS[s.stage] || s.stage}</Tag>}
                        </Flex>
                        <Text variant="microcopy">{s.hook_detail || s.detail || ''}</Text>
                        {s.scored === false && s.scored_reason && (
                          <Text variant="microcopy">Context only — {s.scored_reason}</Text>
                        )}
                      </TableCell>
                      <TableCell>
                        {s.date ||
                          (s.recency_days != null
                            ? `~${s.recency_days} days ago`
                            : 'date not published')}
                      </TableCell>
                      <TableCell>
                        {s.source_url ? (
                          <Link href={s.source_url}>view ↗</Link>
                        ) : (
                          [s.confidence, s.strength != null ? `strength ${s.strength}/5` : '']
                            .filter(Boolean)
                            .join(' · ') || '—'
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            {/* The "we looked and found nothing" trail. It matters (it's the honesty record), but it
                was rendering as one run-on paragraph of every research note. Collapsed, one signal per
                row, reason as microcopy. No data change — this reads from signals_json as it already is. */}
            {notFound.length > 0 && (
              <Accordion
                title={`Checked, nothing in window (${notFound.length})`}
                defaultOpen={false}
              >
                <Flex direction="column" gap="sm">
                  {notFound.map((s, i) => (
                    <Flex key={i} direction="column">
                      <Flex direction="row" gap="sm" align="center">
                        <StatusTag variant="default">{signalLabel(s)}</StatusTag>
                      </Flex>
                      <Text variant="microcopy">
                        {s.note || s.evidence || s.detail || 'No detail recorded.'}
                      </Text>
                    </Flex>
                  ))}
                </Flex>
              </Accordion>
            )}
          </>
        );
      })()}
      <Divider />

      {/* The bespoke first touch */}
      <Flex direction="row" justify="between" align="center">
        <Heading>Your first touch {showSofter ? '(softer variant)' : ''}</Heading>
        <Flex direction="row" gap="sm">
          {p.anti_ai_passed === 'true' && <Tag>✓ Anti-AI gate</Tag>}
          {p.evidence_backed !== 'true' && <Tag>Positioning-only</Tag>}
        </Flex>
      </Flex>
      <Text format={{ fontWeight: 'bold' }}>Subject: <Text inline>{subject}</Text></Text>
      <Text>{body}</Text>
      {p.first_touch_basis && (
        <Flex direction="row" gap="sm" align="center">
          <Tag>{BASIS_LABELS[p.first_touch_basis] || p.first_touch_basis}</Tag>
          {p.first_touch_basis === 'conjunctural' && p.conjunctural_signal && (
            <Text variant="microcopy">{p.conjunctural_signal}</Text>
          )}
        </Flex>
      )}
      {/* "Why this copy" is justification, not instruction — it belongs behind a click. Structured as
          labelled rows where the pipeline provided them, legacy prose otherwise. */}
      {(meta.copy_rationale || p.first_touch_rationale) && (
        <Accordion title="Why this copy" defaultOpen={false}>
          {meta.copy_rationale ? (
            <DescriptionList direction="column">
              {meta.copy_rationale.hook && (
                <DescriptionListItem label="Hook">
                  <Text>{meta.copy_rationale.hook}</Text>
                </DescriptionListItem>
              )}
              {meta.copy_rationale.proof && (
                <DescriptionListItem label="Proof used">
                  <Text>{meta.copy_rationale.proof}</Text>
                </DescriptionListItem>
              )}
              {meta.copy_rationale.persona && (
                <DescriptionListItem label="Persona call">
                  <Text>{meta.copy_rationale.persona}</Text>
                </DescriptionListItem>
              )}
              {meta.copy_rationale.vertical && (
                <DescriptionListItem label="Vertical call">
                  <Text>{meta.copy_rationale.vertical}</Text>
                </DescriptionListItem>
              )}
            </DescriptionList>
          ) : (
            <Text>{p.first_touch_rationale}</Text>
          )}
        </Accordion>
      )}
      <ButtonRow>
        <Button variant="primary" onClick={() => copyEmail(showSofter ? 'softer' : 'primary')}>
          Copy email
        </Button>
        {hasSofter && (
          <Button onClick={() => setShowSofter(!showSofter)}>
            {showSofter ? 'Show primary' : 'Show softer variant'}
          </Button>
        )}
        <Button disabled={busy} onClick={() => giveFeedback('up')}>
          {feedback === 'up' ? '👍 Good draft ✓' : '👍'}
        </Button>
        <Button disabled={busy} onClick={() => giveFeedback('down')}>
          {feedback === 'down' ? '👎 Needs work ✓' : '👎'}
        </Button>
      </ButtonRow>

      {/* Why was it wrong? Free text beats a thumbs-down — it's what actually improves the next draft. */}
      {showDetail && (
        <Flex direction="column" gap="sm">
          <Text format={{ fontWeight: 'bold' }}>What was off?</Text>
          <Text variant="microcopy">
            Be specific and blunt — wrong signal, wrong person, wrong angle, tone, too long, factually
            off, or already in a live thread. This is the only place the agent learns why.
          </Text>
          <TextArea
            name="rep_feedback_detail"
            label=""
            value={detail}
            rows={4}
            placeholder="e.g. The hook was a store that opened 6 months ago — they've been asked about it 5 times already. Lead on the new site they haven't announced yet."
            onChange={(v: string) => {
              setDetail(v);
              setDetailSaved(false);
            }}
          />
          <ButtonRow>
            <Button variant="primary" disabled={busy || !detail.trim() || detailSaved} onClick={saveDetail}>
              {detailSaved ? 'Feedback saved ✓' : 'Send feedback'}
            </Button>
            {detailSaved && (
              <Button disabled={busy} onClick={() => setShowDetail(false)}>
                Close
              </Button>
            )}
          </ButtonRow>
        </Flex>
      )}
      <Divider />

      {/* The cadence to run — every CRM contact, grouped by the US Flow that fits their title.
          Falls back to the single primary flow line when no contact map exists yet. */}
      <Flex direction="row" justify="between" align="center">
        <Heading>The cadence to run</Heading>
        {p.gong_template_url && <Link href={p.gong_template_url}>Open in Gong ↗</Link>}
      </Flex>
      {(contactMap.groups?.length || 0) > 0 ? (
        <>
          <Text variant="microcopy">
            All {contactMap.total_contacts} CRM contacts on this company, grouped by the US Flow that
            matches their title ({contactMap.mapped} mapped). The Primary flow's first touch is the
            bespoke email above — other groups run their flow's templated first touch.
          </Text>
          <Table>
            <TableHead>
              <TableRow>
                <TableHeader>Contact</TableHeader>
                <TableHeader>Title</TableHeader>
                <TableHeader>Run this flow</TableHeader>
              </TableRow>
            </TableHead>
            <TableBody>
              {(contactMap.groups || []).flatMap((g) =>
                g.contacts.map((c, i) => (
                  <TableRow key={`${g.flow}-${c.id || i}`}>
                    <TableCell>
                      <Text format={{ fontWeight: 'bold' }}>{c.name}</Text>
                      {c.email && <Text variant="microcopy">{c.email}</Text>}
                    </TableCell>
                    <TableCell>{c.title || '—'}</TableCell>
                    <TableCell>
                      {i === 0 ? (
                        <Tag>{g.flow === p.cadence_template ? `${g.flow} · Primary` : g.flow}</Tag>
                      ) : (
                        <Text variant="microcopy">{g.flow}</Text>
                      )}
                    </TableCell>
                  </TableRow>
                )),
              )}
            </TableBody>
          </Table>
          {(contactMap.unmapped?.length || 0) > 0 && (
            <Text variant="microcopy">
              Not mapped to a flow:{' '}
              {(contactMap.unmapped || [])
                .map((c) => `${c.name} (${c.title || c.reason || 'no title'})`)
                .join(' · ')}
              {' '}— no Tier-1 persona match; add/fix the job title in HubSpot and re-run to include them.
            </Text>
          )}
        </>
      ) : (
        <Text format={{ fontWeight: 'bold' }}>{p.cadence_template}</Text>
      )}
      <Text variant="microcopy">
        Ready-built in Gong's US Flows folder — you assemble + activate it. Only the first touch above is
        bespoke; every later step follows the flow. Nothing sends automatically.
      </Text>

      <Text variant="microcopy">
        Last agent run: {lastRun} · You see this brief because you own it.
      </Text>
    </Flex>
  );
}
