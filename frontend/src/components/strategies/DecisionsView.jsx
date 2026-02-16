import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import ReactMarkdown from 'react-markdown'

const formatEastern = (dateStr) => {
    if (!dateStr) return '—';
    const dateObj = new Date(dateStr.endsWith('Z') ? dateStr : `${dateStr}Z`);
    return dateObj.toLocaleString('en-US', {
        timeZone: 'America/New_York',
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: false
    });
};

export function DecisionsView({ runId, runs, onRunChange }) {
    const [decisions, setDecisions] = useState([])
    const [loading, setLoading] = useState(false)
    const [filter, setFilter] = useState('ALL')

    useEffect(() => {
        if (!runId) return

        const fetchDecisions = async () => {
            setLoading(true)
            try {
                const url = `/api/strategies/runs/${runId}/decisions`;
                const response = await fetch(url)
                if (response.ok) {
                    const data = await response.json()
                    setDecisions(data)
                }
            } catch (error) {
                console.error("Failed to fetch decisions", error)
            } finally {
                setLoading(false)
            }
        }
        fetchDecisions()
    }, [runId])

    const filteredDecisions = decisions.filter(d => {
        if (filter === 'ALL') return true
        if (filter === 'BUY') return d.final_decision === 'BUY'
        if (filter === 'SKIP') return d.final_decision === 'SKIP' || d.final_decision === 'HOLD' || d.final_decision === 'AVOID' || d.final_decision === 'WATCH'
        if (filter === 'SELL') return d.final_decision === 'SELL'
        return true
    })

    const selectedRun = runs.find(r => String(r.id) === String(runId))

    if (!runId && runs.length === 0) {
        return <div className="p-8 text-center text-muted-foreground">No runs available to view decisions.</div>
    }

    if (!runId) {
        return <div className="p-8 text-center text-muted-foreground">Select a run from the history tab to view decisions.</div>
    }

    return (
        <div className="space-y-6">
            {/* Context Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b pb-4">
                <div>
                    <h3 className="font-semibold text-lg">Decisions Log</h3>
                    <p className="text-sm text-muted-foreground">
                        Showing {filteredDecisions.length} decisions for run on {selectedRun ? formatEastern(selectedRun.started_at) : '-'}
                    </p>
                </div>
                <Tabs value={filter} onValueChange={setFilter} className="w-full sm:w-[320px]">
                    <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="ALL" className="text-xs sm:text-sm">All</TabsTrigger>
                        <TabsTrigger value="BUY" className="text-xs sm:text-sm">Buy</TabsTrigger>
                        <TabsTrigger value="SKIP" className="text-xs sm:text-sm">Skip</TabsTrigger>
                        <TabsTrigger value="SELL" className="text-xs sm:text-sm">Sell</TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            {loading ? (
                <div className="space-y-4">
                    <Skeleton className="h-32 w-full" />
                    <Skeleton className="h-32 w-full" />
                </div>
            ) : filteredDecisions.length === 0 ? (
                <div className="text-center p-12 text-muted-foreground border rounded-lg border-dashed">
                    No decisions found for this filter.
                </div>
            ) : (
                <div className="grid gap-4 md:grid-cols-1">
                    {filteredDecisions.map(decision => (
                        <DecisionCard key={decision.id} decision={decision} />
                    ))}
                </div>
            )}
        </div>
    )
}

function DecisionCard({ decision }) {
    const isBuy = decision.final_decision === 'BUY'
    const [showDeliberation, setShowDeliberation] = useState(false)

    // Truncate logic
    const rawReasoning = decision.thesis_full || decision.decision_reasoning || ''
    const isLong = rawReasoning.length > 300

    return (
        <Card className={`border-l-4 ${isBuy ? 'border-l-green-500' : 'border-l-muted'}`}>
            <CardHeader className="p-3 sm:p-4 pb-2">
                <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <Link to={`/stock/${decision.symbol}`}>
                            <Badge variant="outline" className="font-bold hover:bg-accent">{decision.symbol}</Badge>
                        </Link>
                    </div>
                    <Badge variant={isBuy ? 'success' : 'secondary'}>
                        {decision.final_decision}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent className="p-3 sm:p-6 pt-0 sm:pt-0 text-sm">
                <div className="grid grid-cols-2 gap-4 mb-3">
                    <div className="bg-muted/30 p-2 rounded">
                        <span className="font-semibold text-xs block mb-1">LYNCH</span>
                        <div className="flex justify-between">
                            <span>Score: {decision.lynch_score?.toFixed(0)}</span>
                            <span className="text-muted-foreground">{decision.lynch_status}</span>
                        </div>
                    </div>
                    <div className="bg-muted/30 p-2 rounded">
                        <span className="font-semibold text-xs block mb-1">BUFFETT</span>
                        <div className="flex justify-between">
                            <span>Score: {decision.buffett_score?.toFixed(0)}</span>
                            <span className="text-muted-foreground">{decision.buffett_status}</span>
                        </div>
                    </div>
                </div>

                {decision.decision_reasoning && (
                    <div className="bg-muted/50 p-3 rounded-md mb-2 border border-border">
                        <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <MessageSquare className="h-3 w-3" />
                                <span className="font-bold text-[10px] uppercase tracking-wider">Deliberation</span>
                            </div>
                            {isLong && (
                                <Badge
                                    variant="outline"
                                    className={`text-[10px] font-bold px-2 py-0 border-transparent ${decision.consensus_verdict === 'BUY' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
                                        decision.consensus_verdict === 'AVOID' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                                            'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
                                        }`}
                                >
                                    Consensus: {decision.consensus_verdict || decision.final_decision}
                                </Badge>
                            )}
                        </div>

                        {isLong ? (
                            <Button
                                variant="outline"
                                size="sm"
                                className="w-full text-xs h-7 font-bold border-primary/40 text-primary bg-white dark:bg-slate-900 shadow-sm hover:bg-primary hover:text-primary-foreground transition-all"
                                onClick={() => setShowDeliberation(true)}
                            >
                                Review deliberation
                            </Button>
                        ) : (
                            <p className="text-foreground leading-relaxed whitespace-pre-line text-xs">
                                {rawReasoning}
                            </p>
                        )}
                    </div>
                )}

                <Dialog open={showDeliberation} onOpenChange={setShowDeliberation}>
                    <DialogContent className="max-w-3xl max-h-[85vh] p-0 flex flex-col overflow-hidden border-border bg-background shadow-2xl">
                        <DialogHeader className="p-6 pb-4 border-b">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-primary text-primary-foreground">
                                    <MessageSquare size={20} />
                                </div>
                                <div>
                                    <DialogTitle className="text-xl font-bold">Analysis Deliberation: {decision.symbol}</DialogTitle>
                                    <DialogDescription>
                                        Qualitative debate between Lynch and Buffett agents
                                    </DialogDescription>
                                </div>
                            </div>
                        </DialogHeader>
                        <ScrollArea className="h-[calc(85vh-180px)] w-full border-b">
                            <div className="p-8 prose prose-sm max-w-none dark:prose-invert">
                                <ReactMarkdown>{rawReasoning}</ReactMarkdown>
                            </div>
                        </ScrollArea>
                        <DialogFooter className="border-t p-4 px-6 bg-muted/30">
                            <Button variant="outline" size="sm" onClick={() => setShowDeliberation(false)}>
                                Close
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </CardContent>
        </Card>
    )
}
