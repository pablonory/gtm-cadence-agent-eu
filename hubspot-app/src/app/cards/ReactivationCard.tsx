import { useEffect, useState } from 'react';
import {
  Accordion,
  Alert,
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
  Tile,
  hubspot,
} from '@hubspot/ui-extensions';

// The Reactivation tab — for accounts with a prior closed/disqualified deal.
//
// DESIGN NOTE (rewritten 2026-08-13 after rep feedback): the first version rendered each analysis field
// as one long <Text> block, which produced unreadable walls of prose. The fix is in BOTH layers: the
// analysis is now stored structured in `reactivation_json` (not prose paragraphs), and this card renders
// it as real components — a verdict tag, three short action lines, a cycles table, short bullets, and a
// compact evidence row. Long-form narrative lives in collapsed <Accordion>s so depth stays available
// without dominating the page. Answer the rep's question first, hide the reasoning until asked.
//
// Legacy fallback: briefs analysed before reactivation_json existed still hold prose in the four
// reactivation_* textareas. Those render inside accordions rather than being dropped.

const PROPS = [
  'company_name',
  'reactivation_json',
  'reactivation_evidence_basis',
  'reactivation_deal_history',
  'reactivation_call_analysis',
  'reactivation_email_analysis',
  'reactivation_recommendation',
  'reactivation_last_deal_url',
  'reactivation_analysis_date',
];

const BASIS_LABELS: Record<string, string> = {
  none: 'No prior deal',
  deal_only: 'Deal record only',
  deal_calls: 'Deal + calls',
  deal_calls_emails: 'Deal + calls + emails',
  calls_only: 'Calls only',
};

type Verdict = 'reactivate' | 'do_not_reactivate' | 'insufficient_evidence';

const VERDICT_UI: Record<Verdict, { variant: 'success' | 'danger' | 'warning'; label: string }> = {
  reactivate: { variant: 'success', label: 'Worth reactivating' },
  do_not_reactivate: { variant: 'danger', label: 'Do not reactivate' },
  insufficient_evidence: { variant: 'warning', label: 'Not enough evidence' },
};

interface Cycle {
  label?: string;
  dates?: string;
  amount?: string;
  picklist?: string;
  reason?: string;
}

interface DetailSection {
  summary?: string;
  points?: string[];
  quote?: { text?: string; who?: string; when?: string };
}

interface EmailPeriod {
  period?: string;
  count?: number;
  note?: string;
}

interface Analysis {
  verdict?: Verdict;
  verdict_reason?: string;
  lead_with?: { name?: string; title?: string; why?: string };
  hook?: string;
  ask?: string;
  do_not_repeat?: string[];
  why_it_died?: { headline?: string; detail?: string };
  cycles?: Cycle[];
  evidence?: {
    calls?: number;
    substantive_calls?: number;
    emails?: number;
    last_contact?: string;
    current_tools?: string[];
  };
  flags?: string[];
  // Detail sections rendered inside the accordions — bullets, not paragraphs (rep feedback 2026-08-13).
  call_detail?: DetailSection;
  deal_detail?: DetailSection;
  email_detail?: DetailSection & { timeline?: EmailPeriod[] };
}

// HubSpot `date` properties arrive as epoch-ms strings — show YYYY-MM-DD, not 1786579200000.
// Same bug class as the last_run fix on the Cadence Agent card.
function asDate(raw?: string): string {
  if (!raw) return '—';
  const d = new Date(Number(raw) || raw);
  return isNaN(d.getTime()) ? raw : d.toISOString().slice(0, 10);
}

/** Renders a detail section as a short summary + bullets + optional pull-quote, falling back to legacy
 *  prose for briefs analysed before the structured shape existed. */
function Detail({ section, legacy }: { section?: DetailSection; legacy?: string }) {
  const hasStructured = Boolean(section?.summary || section?.points?.length || section?.quote?.text);
  if (!hasStructured) {
    return legacy ? <Text>{legacy}</Text> : <Text variant="microcopy">Nothing recorded.</Text>;
  }
  return (
    <Flex direction="column" gap="sm">
      {section?.summary && <Text format={{ fontWeight: 'bold' }}>{section.summary}</Text>}
      {(section?.points || []).length > 0 && (
        <List variant="unordered">
          {(section?.points || []).map((pt, i) => (
            <Text key={i}>{pt}</Text>
          ))}
        </List>
      )}
      {section?.quote?.text && (
        <Tile compact>
          <Text format={{ fontStyle: 'italic' }}>“{section.quote.text}”</Text>
          <Text variant="microcopy">
            — {section.quote.who || 'prospect'}
            {section.quote.when ? `, ${section.quote.when}` : ''}
          </Text>
        </Tile>
      )}
    </Flex>
  );
}

hubspot.extend<'crm.record.tab'>(({ context, actions }) => (
  <ReactivationCard context={context} actions={actions} />
));

function ReactivationCard({ actions }: { context: any; actions: any }) {
  const [p, setP] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    actions
      .fetchCrmObjectProperties(PROPS)
      .then((props: Record<string, string>) => setP(props))
      .catch((e: Error) => setError(e.message));
    if (actions.onCrmPropertiesUpdate) {
      actions.onCrmPropertiesUpdate(PROPS, (props: Record<string, string>) =>
        setP((prev) => ({ ...prev, ...props })),
      );
    }
  }, [actions]);

  if (error) {
    return <Alert title="Could not load the reactivation analysis" variant="error">{error}</Alert>;
  }
  if (!p) {
    return <LoadingSpinner label="Loading reactivation analysis…" />;
  }

  const basis = p.reactivation_evidence_basis || '';
  const analysed = Boolean(basis) && basis !== 'none';

  if (!analysed) {
    return (
      <Flex direction="column" gap="sm">
        <Heading>Reactivation</Heading>
        <Text>
          No closed or disqualified deal on file for {p.company_name || 'this account'} — nothing to
          reactivate. If a deal here later closes lost, re-run the analysis and this tab fills in.
        </Text>
      </Flex>
    );
  }

  const a: Analysis = (() => {
    try {
      const parsed = JSON.parse(p.reactivation_json || '{}');
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  })();

  const verdict = (a.verdict || 'insufficient_evidence') as Verdict;
  const v = VERDICT_UI[verdict] || VERDICT_UI.insufficient_evidence;
  const structured = Boolean(a.verdict || a.hook || a.cycles?.length);

  return (
    <Flex direction="column" gap="md">
      {/* Verdict first — the rep's actual question is "do I work this, and how?" */}
      <Flex direction="row" justify="between" align="center">
        <Flex direction="row" gap="sm" align="center">
          <Heading>Reactivation</Heading>
          <StatusTag variant={v.variant}>{v.label}</StatusTag>
        </Flex>
        <Tag>{BASIS_LABELS[basis] || basis}</Tag>
      </Flex>
      {a.verdict_reason && <Text format={{ fontWeight: 'bold' }}>{a.verdict_reason}</Text>}

      {(a.flags || []).length > 0 && (
        <Alert title="Before you send" variant="warning">
          <List variant="unordered">
            {(a.flags || []).map((f, i) => (
              <Text key={i}>{f}</Text>
            ))}
          </List>
        </Alert>
      )}

      {/* The three things a rep needs to act — short, labelled, scannable. */}
      {structured && (a.lead_with?.name || a.hook || a.ask) && (
        <Tile compact>
          <DescriptionList direction="row">
            {a.lead_with?.name && (
              <DescriptionListItem label="Lead with">
                <Text format={{ fontWeight: 'bold' }}>
                  {a.lead_with.name}
                  {a.lead_with.title ? ` — ${a.lead_with.title}` : ''}
                </Text>
                {a.lead_with.why && <Text variant="microcopy">{a.lead_with.why}</Text>}
              </DescriptionListItem>
            )}
            {a.hook && (
              <DescriptionListItem label="Open on">
                <Text>{a.hook}</Text>
              </DescriptionListItem>
            )}
            {a.ask && (
              <DescriptionListItem label="Ask for">
                <Text>{a.ask}</Text>
              </DescriptionListItem>
            )}
          </DescriptionList>
        </Tile>
      )}

      {/* Why it died — one line, not a paragraph. */}
      {a.why_it_died?.headline && (
        <>
          <Divider />
          <Flex direction="row" gap="sm" align="center">
            <Text format={{ fontWeight: 'bold' }}>Why it died:</Text>
            <Tag>{a.why_it_died.headline}</Tag>
          </Flex>
          {a.why_it_died.detail && <Text variant="microcopy">{a.why_it_died.detail}</Text>}
        </>
      )}

      {(a.do_not_repeat || []).length > 0 && (
        <>
          <Text format={{ fontWeight: 'bold' }}>Don't repeat</Text>
          <List variant="unordered">
            {(a.do_not_repeat || []).map((d, i) => (
              <Text key={i}>{d}</Text>
            ))}
          </List>
        </>
      )}

      {/* Deal cycles as a table — this was the worst offender as prose. */}
      {(a.cycles || []).length > 0 && (
        <>
          <Divider />
          <Text format={{ fontWeight: 'bold' }}>Past cycles</Text>
          <Table>
            <TableHead>
              <TableRow>
                <TableHeader>Cycle</TableHeader>
                <TableHeader>When</TableHeader>
                <TableHeader>Value</TableHeader>
                <TableHeader>Logged reason</TableHeader>
              </TableRow>
            </TableHead>
            <TableBody>
              {(a.cycles || []).map((c, i) => (
                <TableRow key={i}>
                  <TableCell>{c.label || `Cycle ${i + 1}`}</TableCell>
                  <TableCell>{c.dates || '—'}</TableCell>
                  <TableCell>{c.amount || '—'}</TableCell>
                  <TableCell>
                    {c.picklist && <Tag>{c.picklist}</Tag>}
                    {c.reason && <Text variant="microcopy">{c.reason}</Text>}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}

      {/* Compact evidence line — replaces three paragraphs of counts. */}
      {a.evidence && (
        <DescriptionList direction="row">
          {a.evidence.calls != null && (
            <DescriptionListItem label="Calls">
              <Text>
                {a.evidence.calls}
                {a.evidence.substantive_calls != null
                  ? ` (${a.evidence.substantive_calls} substantive)`
                  : ''}
              </Text>
            </DescriptionListItem>
          )}
          {a.evidence.emails != null && (
            <DescriptionListItem label="Logged emails">
              <Text>{a.evidence.emails}</Text>
            </DescriptionListItem>
          )}
          {a.evidence.last_contact && (
            <DescriptionListItem label="Last contact">
              <Text>{a.evidence.last_contact}</Text>
            </DescriptionListItem>
          )}
          {(a.evidence.current_tools || []).length > 0 && (
            <DescriptionListItem label="Tools then">
              <Text>{(a.evidence.current_tools || []).join(', ')}</Text>
            </DescriptionListItem>
          )}
        </DescriptionList>
      )}

      {p.reactivation_last_deal_url && (
        <Link href={p.reactivation_last_deal_url}>Open the deal in HubSpot ↗</Link>
      )}

      {/* Detail, collapsed. Bullets and a pull-quote rather than paragraphs — depth on demand. */}
      <Divider />
      {(a.call_detail || p.reactivation_call_analysis) && (
        <Accordion title="What the calls showed" defaultOpen={false}>
          <Detail section={a.call_detail} legacy={p.reactivation_call_analysis} />
        </Accordion>
      )}
      {(a.deal_detail || p.reactivation_deal_history) && (
        <Accordion title="Deal history detail" defaultOpen={false}>
          <Detail section={a.deal_detail} legacy={p.reactivation_deal_history} />
        </Accordion>
      )}
      {(a.email_detail || p.reactivation_email_analysis) && (
        <Accordion title="Email engagement" defaultOpen={false}>
          <Flex direction="column" gap="sm">
            {(a.email_detail?.timeline || []).length > 0 && (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeader>Period</TableHeader>
                    <TableHeader>Emails</TableHeader>
                    <TableHeader>Note</TableHeader>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(a.email_detail?.timeline || []).map((t, i) => (
                    <TableRow key={i}>
                      <TableCell>{t.period || '—'}</TableCell>
                      <TableCell>{t.count != null ? t.count : '—'}</TableCell>
                      <TableCell>
                        <Text variant="microcopy">{t.note || ''}</Text>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            <Detail section={a.email_detail} legacy={p.reactivation_email_analysis} />
          </Flex>
        </Accordion>
      )}
      {!structured && p.reactivation_recommendation && (
        <Accordion title="Recommendation (unstructured)" defaultOpen>
          <Text>{p.reactivation_recommendation}</Text>
        </Accordion>
      )}

      <Text variant="microcopy">
        Analysed {asDate(p.reactivation_analysis_date)} from the deal record and Gong transcripts confirmed
        by participant email domain. Where evidence is thin, the verdict says so rather than guessing.
      </Text>
    </Flex>
  );
}
