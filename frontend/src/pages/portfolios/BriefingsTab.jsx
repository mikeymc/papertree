// ABOUTME: Strategy run briefings tab for autonomous portfolios
// ABOUTME: Displays briefing cards with markdown summaries, trades table, and score-enriched holds

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { formatLocal } from '@/utils/formatters'
import {
    Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table"
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
    ChevronDown,
    Filter,
    BarChart3,
    FileText,
    ArrowLeftRight,
    ArrowRight,
    Globe,
    Target,
    MessageSquare
} from 'lucide-react'

const API_BASE = '/api'

export default function BriefingsTab({ portfolioId, refreshKey = 0 }) {
    const [briefings, setBriefings] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!portfolioId) return

        setLoading(true)
        fetch(`${API_BASE}/portfolios/${portfolioId}/briefings`, { credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                setBriefings(data)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [portfolioId, refreshKey])

    if (loading) {
        return (
            <div className="space-y-4">
                {[1, 2].map(i => (
                    <Card key={i}>
                        <CardContent className="pt-6 space-y-3">
                            <Skeleton className="h-4 w-48" />
                            <Skeleton className="h-16 w-full" />
                            <Skeleton className="h-8 w-full" />
                        </CardContent>
                    </Card>
                ))}
            </div>
        )
    }

    if (briefings.length === 0) {
        return (
            <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p>No briefings yet. Briefings are generated after each strategy run.</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <div className="space-y-4">
            {briefings.map(briefing => (
                <BriefingCard key={briefing.id} briefing={briefing} />
            ))}
        </div>
    )
}

function BriefingCard({ briefing }) {
    const date = formatLocal(briefing.generated_at)
    const analysts = briefing.analysts || ['lynch', 'buffett']
    const companyNames = briefing.company_names || {}
    const theses = briefing.character_theses || {}  // {symbol: {character_id: text}}

    const buys = safeParse(briefing.buys_json)
    const sells = safeParse(briefing.sells_json)
    const holds = safeParse(briefing.holds_json)
    const trades = [
        ...sells.map(s => ({ ...s, action: 'SELL' })),
        ...buys.map(b => ({ ...b, action: 'BUY' })),
    ]

    // Fetch decisions for this run to get thesis/deliberation data
    const [decisions, setDecisions] = useState([])
    useEffect(() => {
        if (!briefing.run_id) return
        fetch(`${API_BASE}/strategies/runs/${briefing.run_id}/decisions`, { credentials: 'include' })
            .then(res => res.ok ? res.json() : [])
            .then(data => setDecisions(Array.isArray(data) ? data : []))
            .catch(() => { })
    }, [briefing.run_id])

    // Build a quick lookup map: symbol -> decision record
    const decisionMap = {}
    for (const d of decisions) {
        if (d.symbol) decisionMap[d.symbol] = d
    }

    return (
        <Card>
            <CardHeader className="p-3 sm:p-4 pb-3">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-medium text-muted-foreground">
                        {date}
                    </CardTitle>
                </div>
            </CardHeader>

            <CardContent className="p-3 sm:p-6 pt-0 sm:pt-0 space-y-4">
                {/* Executive Summary (markdown) */}
                {briefing.executive_summary && (
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                a: ({ href, children, ...props }) => {
                                    if (href && href.startsWith('/')) {
                                        return (
                                            <Link to={href} {...props} className="text-primary hover:underline">
                                                {children}
                                            </Link>
                                        )
                                    }
                                    return <a href={href} {...props}>{children}</a>
                                }
                            }}
                        >
                            {briefing.executive_summary}
                        </ReactMarkdown>
                    </div>
                )}

                {/* Stats Pipeline */}
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground bg-muted/50 rounded-md px-3 py-2">
                    <PipelineStat icon={Globe} label="Universe" value={briefing.universe_size} />
                    <ArrowRight className="h-3 w-3 opacity-30 shrink-0" />
                    <PipelineStat icon={Filter} label="Candidates" value={briefing.candidates} />
                    <ArrowRight className="h-3 w-3 opacity-30 shrink-0" />
                    <PipelineStat icon={BarChart3} label="Qualifiers" value={briefing.qualifiers} />
                    <ArrowRight className="h-3 w-3 opacity-30 shrink-0" />
                    <PipelineStat icon={FileText} label="Theses" value={briefing.theses} />
                    <ArrowRight className="h-3 w-3 opacity-30 shrink-0" />
                    <PipelineStat icon={Target} label="Targets" value={briefing.targets} />
                    <ArrowRight className="h-3 w-3 opacity-30 shrink-0" />
                    <PipelineStat icon={ArrowLeftRight} label="Trades" value={briefing.trades} />
                </div>

                {/* Trades Table */}
                {trades.length > 0 && (
                    <TradesTable
                        trades={trades}
                        analysts={analysts}
                        companyNames={companyNames}
                        theses={theses}
                        decisionMap={decisionMap}
                    />
                )}

                {/* Holds */}
                {holds.length > 0 && <HoldsSection holds={holds} />}
            </CardContent>
        </Card>
    )
}

/** Small dialog that renders any markdown text. */
function TextDialog({ open, onClose, title, content }) {
    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-3xl max-h-[85vh] p-0 flex flex-col overflow-hidden">
                <DialogHeader className="p-6 pb-4 border-b">
                    <DialogTitle>{title}</DialogTitle>
                </DialogHeader>
                <ScrollArea className="h-[calc(85vh-100px)] w-full">
                    <div className="p-6 prose prose-sm max-w-none dark:prose-invert">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    )
}

/** A small link-style button that opens a text dialog. */
function ThesisLink({ label, content, title }) {
    const [open, setOpen] = useState(false)
    if (!content) return <span className="text-xs text-muted-foreground">—</span>
    return (
        <>
            <button
                className="text-xs text-primary hover:underline underline-offset-2 cursor-pointer"
                onClick={() => setOpen(true)}
            >
                {label}
            </button>
            <TextDialog open={open} onClose={() => setOpen(false)} title={title} content={content} />
        </>
    )
}

function ScoreBadge({ score, status }) {
    if (score == null) return <span className="text-xs text-muted-foreground">—</span>

    const colorClass = status === 'excellent' ? 'text-emerald-600 dark:text-emerald-400'
        : status === 'good' ? 'text-emerald-600/80 dark:text-emerald-400/80'
            : status === 'fair' ? 'text-yellow-600 dark:text-yellow-400'
                : 'text-red-600 dark:text-red-400'

    return (
        <span className={`text-xs font-medium tabular-nums ${colorClass}`}>
            {score.toFixed(0)}
        </span>
    )
}

function TradesTable({ trades, analysts, companyNames, theses, decisionMap }) {
    const isSingle = analysts.length === 1
    const showLynch = analysts.includes('lynch')
    const showBuffett = analysts.includes('buffett')

    // Column labels
    const lynchLabel = isSingle ? 'Score' : 'Lynch Score'
    const buffettLabel = 'Buffett Score'

    return (
        <div>
            <h4 className="text-sm font-medium mb-2">Trades</h4>
            <div className="w-full overflow-hidden rounded-md border border-border/50">
                <Table className="w-full table-auto">
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[70px]">Action</TableHead>
                            <TableHead className="min-w-[150px]">Symbol</TableHead>
                            <TableHead className="text-right w-[80px]">Shares</TableHead>
                            <TableHead className="text-right w-[90px]">Price</TableHead>
                            <TableHead className="text-right w-[100px]">Value</TableHead>
                            {showLynch && <TableHead className="text-right w-[50px] leading-tight">{lynchLabel}</TableHead>}
                            {showBuffett && <TableHead className="text-right w-[50px] leading-tight">{buffettLabel}</TableHead>}
                            {/* Thesis / deliberation columns */}
                            {isSingle && (
                                <TableHead className="text-center w-[50px]">Thesis</TableHead>
                            )}
                            {!isSingle && showLynch && (
                                <TableHead className="text-center w-[50px] leading-tight">Lynch Thesis</TableHead>
                            )}
                            {!isSingle && showBuffett && (
                                <TableHead className="text-center w-[50px] leading-tight">Buffett Thesis</TableHead>
                            )}
                            {!isSingle && (
                                <TableHead className="text-center w-[50px] leading-tight">Deliberation</TableHead>
                            )}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {trades.map((trade, i) => {
                            const decision = decisionMap[trade.symbol]
                            const companyName = companyNames[trade.symbol]
                            const symbolTheses = theses[trade.symbol] || {}

                            // Individual character theses come from lynch_analyses cache
                            const lynchThesis = symbolTheses['lynch'] || null
                            const buffettThesis = symbolTheses['buffett'] || null
                            // Deliberation for pair strategies = thesis_full on the decision record
                            const deliberation = !isSingle
                                ? (decision?.thesis_full || decision?.decision_reasoning)
                                : null
                            // For single analyst, use their thesis from symbolTheses
                            const singleThesis = isSingle
                                ? (symbolTheses[analysts[0]] || null)
                                : null

                            return (
                                <TableRow key={`${trade.action}-${trade.symbol}-${i}`}>
                                    <TableCell>
                                        <Badge
                                            variant={trade.action === 'BUY' ? 'success' : 'destructive'}
                                            className="text-[10px] px-1.5 py-0"
                                        >
                                            {trade.action}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="py-2">
                                        <div className="flex flex-col min-w-0 pr-2">
                                            <Link
                                                to={`/stock/${trade.symbol}`}
                                                className="font-mono text-sm font-medium text-primary hover:underline"
                                            >
                                                {trade.symbol}
                                            </Link>
                                            {companyName && (
                                                <span className="text-xs text-muted-foreground truncate max-w-[160px]">
                                                    {companyName}
                                                </span>
                                            )}
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-right tabular-nums text-sm">
                                        {trade.shares ?? '—'}
                                    </TableCell>
                                    <TableCell className="text-right tabular-nums text-sm">
                                        {trade.price != null ? `$${trade.price.toFixed(2)}` : '—'}
                                    </TableCell>
                                    <TableCell className="text-right tabular-nums text-sm">
                                        {trade.position_value != null
                                            ? `$${trade.position_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                                            : '—'}
                                    </TableCell>
                                    {showLynch && (
                                        <TableCell className="text-right">
                                            <ScoreBadge score={trade.lynch_score} status={trade.lynch_status} />
                                        </TableCell>
                                    )}
                                    {showBuffett && (
                                        <TableCell className="text-right">
                                            <ScoreBadge score={trade.buffett_score} status={trade.buffett_status} />
                                        </TableCell>
                                    )}
                                    {/* Thesis columns */}
                                    {isSingle && (
                                        <TableCell className="text-center">
                                            <ThesisLink
                                                label="Read"
                                                content={singleThesis}
                                                title={`${trade.symbol} — ${analysts[0] === 'lynch' ? 'Lynch' : 'Buffett'} Thesis`}
                                            />
                                        </TableCell>
                                    )}
                                    {!isSingle && showLynch && (
                                        <TableCell className="text-center">
                                            <ThesisLink
                                                label="Read"
                                                content={lynchThesis}
                                                title={`${trade.symbol} — Lynch's Thesis`}
                                            />
                                        </TableCell>
                                    )}
                                    {!isSingle && showBuffett && (
                                        <TableCell className="text-center">
                                            <ThesisLink
                                                label="Read"
                                                content={buffettThesis}
                                                title={`${trade.symbol} — Buffett's Thesis`}
                                            />
                                        </TableCell>
                                    )}
                                    {!isSingle && (
                                        <TableCell className="text-center">
                                            <ThesisLink
                                                label="Read"
                                                content={deliberation}
                                                title={`${trade.symbol} — Deliberation`}
                                            />
                                        </TableCell>
                                    )}
                                </TableRow>
                            )
                        })}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}

function HoldsSection({ holds }) {
    const [open, setOpen] = useState(false)

    return (
        <Collapsible open={open} onOpenChange={setOpen}>
            <CollapsibleTrigger className="flex items-center gap-2 text-sm font-medium w-full text-left hover:opacity-80 transition-opacity">
                <ChevronDown className={`h-4 w-4 transition-transform ${open ? '' : '-rotate-90'}`} />
                Holds
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                    {holds.length}
                </Badge>
            </CollapsibleTrigger>
            <CollapsibleContent>
                <div className="mt-2 space-y-2 pl-6">
                    {holds.map((item, i) => (
                        <div key={item.symbol || i} className="flex items-center gap-3">
                            <Link
                                to={`/stock/${item.symbol}`}
                                className="font-mono text-sm font-medium text-primary hover:underline shrink-0 w-16"
                            >
                                {item.symbol}
                            </Link>
                            {item.consensus_verdict && (
                                <Badge
                                    variant={item.consensus_verdict === 'BUY' ? 'success'
                                        : item.consensus_verdict === 'AVOID' ? 'destructive'
                                            : 'secondary'}
                                    className="text-[10px] px-1.5 py-0"
                                >
                                    {item.consensus_verdict}
                                </Badge>
                            )}
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                {item.lynch_score != null && (
                                    <span>L: <ScoreBadge score={item.lynch_score} status={item.lynch_status} /></span>
                                )}
                                {item.buffett_score != null && (
                                    <span>B: <ScoreBadge score={item.buffett_score} status={item.buffett_status} /></span>
                                )}
                                {item.position_value != null && (
                                    <span className="text-muted-foreground">
                                        ${item.position_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </CollapsibleContent>
        </Collapsible>
    )
}

function PipelineStat({ icon: Icon, label, value }) {
    return (
        <div className="flex items-center gap-1.5 shrink-0">
            <Icon className="h-3.5 w-3.5 opacity-60" />
            <span className="font-medium tabular-nums">{value ?? 0}</span>
            <span className="hidden lg:inline opacity-60">{label}</span>
        </div>
    )
}

function safeParse(jsonStr) {
    if (!jsonStr) return []
    try {
        return JSON.parse(jsonStr)
    } catch {
        return []
    }
}
