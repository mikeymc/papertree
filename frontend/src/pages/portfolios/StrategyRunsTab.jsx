import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function StrategyRunsTab({ strategyId, runsCount }) {
    const navigate = useNavigate()
    const [runs, setRuns] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchRuns = async () => {
            if (!strategyId) return
            try {
                setLoading(true)
                const response = await fetch(`/api/strategies/${strategyId}`)
                if (!response.ok) {
                    throw new Error('Failed to fetch strategy runs')
                }
                const data = await response.json()
                setRuns(data.runs || [])
            } catch (err) {
                console.error(err)
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        fetchRuns()
    }, [strategyId])

    if (loading) {
        return (
            <Card>
                <CardHeader className="p-3 sm:p-4 pb-2">
                    <CardTitle>Strategy Runs {runsCount !== undefined && runsCount !== null ? `(${runsCount})` : ''}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 sm:p-6 pt-0 sm:pt-0">
                    <div className="space-y-4">
                        {[1, 2, 3].map(i => (
                            <Skeleton key={i} className="h-12 w-full" />
                        ))}
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (error) {
        return (
            <Card className="border-destructive/50 bg-destructive/5">
                <CardContent className="py-12 text-center text-destructive">
                    <p>Error loading strategy runs: {error}</p>
                </CardContent>
            </Card>
        )
    }

    const displayCount = runs.length > 0 ? runs.length : runsCount;

    return (
        <Card>
            <CardHeader className="p-3 sm:p-4 pb-2">
                <CardTitle>Strategy Runs {displayCount !== undefined && displayCount !== null ? `(${displayCount})` : ''}</CardTitle>
            </CardHeader>
            <CardContent className="p-3 sm:p-6 pt-0 sm:pt-0">
                {/* Desktop View: Table */}
                <div className="hidden sm:block">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Date</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Screened</TableHead>
                                <TableHead>Scored</TableHead>
                                <TableHead>Trades</TableHead>
                                <TableHead>Decisions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {runs.map((run) => (
                                <TableRow
                                    key={run.id}
                                    className="cursor-pointer hover:bg-muted/50 transition-colors"
                                    onClick={() => {
                                        navigate(`/strategies/${strategyId}/runs/${run.id}`);
                                    }}
                                >
                                    <TableCell className="font-medium">{format(new Date(run.started_at), 'MMM d, yyyy HH:mm')}</TableCell>
                                    <TableCell>
                                        <Badge variant={run.status === 'completed' ? 'success' : 'default'} className="capitalize">
                                            {run.status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>{run.stocks_screened}</TableCell>
                                    <TableCell>{run.stocks_scored}</TableCell>
                                    <TableCell>{run.trades_executed}</TableCell>
                                    <TableCell>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-8 px-2 hover:bg-transparent"
                                        >
                                            View
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>

                {/* Mobile View: 3-column Grid */}
                <div className="block sm:hidden space-y-2">
                    {runs.map((run) => (
                        <div
                            key={run.id}
                            className="grid grid-cols-3 gap-2 py-4 border-b last:border-0 cursor-pointer active:bg-muted/50"
                            onClick={() => {
                                navigate(`/strategies/${strategyId}/runs/${run.id}`);
                            }}
                        >
                            {/* Col 1: Date & Status */}
                            <div className="flex flex-col gap-2">
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight h-3">Date</span>
                                    <span className="text-xs font-medium truncate">{format(new Date(run.started_at), 'MMM d, HH:mm')}</span>
                                </div>
                                <div className="flex flex-col">
                                    <Badge variant={run.status === 'completed' ? 'success' : 'default'} className="capitalize text-[10px] px-1.5 h-5 w-fit">
                                        {run.status}
                                    </Badge>
                                </div>
                            </div>

                            {/* Col 2: Screened & Scored */}
                            <div className="flex flex-col gap-2">
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight h-3">Screened</span>
                                    <span className="text-xs font-medium">{run.stocks_screened}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight h-3">Scored</span>
                                    <span className="text-xs font-medium">{run.stocks_scored}</span>
                                </div>
                            </div>

                            {/* Col 3: Trades & Link */}
                            <div className="flex flex-col gap-2 text-right items-end">
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight h-3">Trades</span>
                                    <span className="text-xs font-medium">{run.trades_executed}</span>
                                </div>
                                <div className="flex flex-col items-end pt-1">
                                    <span className="text-[10px] text-primary font-bold uppercase tracking-wider flex items-center underline decoration-primary/30">
                                        Decisions →
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {runs.length === 0 && (
                    <div className="text-center py-12 text-muted-foreground">
                        No runs recorded yet.
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
