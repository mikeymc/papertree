// ABOUTME: Dashboard card showing recent Form 144 filings for watchlist/portfolio stocks
// ABOUTME: Displays insider intent-to-sell notices with name, relationship, shares, and value

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { FileWarning } from 'lucide-react'

export default function InsiderIntent() {
    const navigate = useNavigate()
    const [data, setData] = useState({ filings: [], total_count: 0 })
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true)
                const response = await fetch('/api/dashboard/insider-intent')
                if (response.ok) {
                    const json = await response.json()
                    setData(json.insider_intent || { filings: [], total_count: 0 })
                } else {
                    setError('Failed to load insider intent data')
                }
            } catch (err) {
                console.error('Error fetching insider intent:', err)
                setError('Failed to load insider intent data')
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    const { filings = [], total_count = 0 } = data
    const moreCount = total_count - filings.length

    return (
        <Card>
            <CardHeader className="p-3 sm:p-4 pb-2">
                <CardTitle className="text-base font-medium flex items-center gap-2">
                    <FileWarning className="h-4 w-4" />
                    Insider Intent to Sell
                </CardTitle>
            </CardHeader>
            <CardContent className="p-3 sm:p-6 pt-0 sm:pt-0">
                {loading ? (
                    <Skeleton className="h-24 w-full" />
                ) : error ? (
                    <div className="h-24 flex items-center justify-center text-sm text-muted-foreground border border-dashed rounded-lg bg-muted/20">
                        {error}
                    </div>
                ) : filings.length > 0 ? (
                    <div className="space-y-0">
                        {filings.map(filing => (
                            <FilingRow
                                key={`${filing.accession_number}-${filing.insider_name}`}
                                filing={filing}
                                onClick={() => navigate(`/stock/${filing.symbol}`)}
                            />
                        ))}
                        {moreCount > 0 && (
                            <div className="pt-2 pb-1 text-center border-t border-border mt-1">
                                <span className="text-xs text-muted-foreground italic">
                                    +{moreCount} more filings
                                </span>
                            </div>
                        )}
                    </div>
                ) : (
                    <EmptyState />
                )}
            </CardContent>
        </Card>
    )
}

function FilingRow({ filing, onClick }) {
    const daysSince = filing.filing_date
        ? Math.floor((Date.now() - new Date(filing.filing_date + 'T00:00:00').getTime()) / 86400000)
        : null

    return (
        <button
            onClick={onClick}
            className="w-full grid grid-cols-[42px_1fr_auto] items-center py-1 px-0 rounded hover:bg-accent transition-colors text-left border-b border-border last:border-0 overflow-hidden gap-1.5 sm:gap-2"
        >
            <span className="font-medium text-sm shrink-0">{filing.symbol}</span>
            <div className="min-w-0 flex items-center gap-1.5">
                <span className="text-xs text-muted-foreground truncate">
                    {filing.insider_name}
                </span>
                {filing.relationship && (
                    <Badge variant="outline" className="text-[10px] h-4 py-0 shrink-0">
                        {filing.relationship}
                    </Badge>
                )}
            </div>
            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <span className="text-xs text-muted-foreground whitespace-nowrap text-right">
                    {formatValue(filing.estimated_value, filing.shares_to_sell)}
                </span>
                {daysSince !== null && (
                    <Badge
                        variant={daysSince <= 3 ? 'destructive' : daysSince <= 7 ? 'default' : 'secondary'}
                        className="text-[10px] sm:text-xs h-5 py-0 w-10 sm:w-12 justify-center shrink-0"
                    >
                        {daysSince === 0 ? 'Today' : `${daysSince}d`}
                    </Badge>
                )}
            </div>
        </button>
    )
}

function formatValue(estimatedValue, sharesToSell) {
    if (estimatedValue) {
        if (estimatedValue >= 1_000_000) {
            return `$${(estimatedValue / 1_000_000).toFixed(1)}M`
        }
        if (estimatedValue >= 1_000) {
            return `$${(estimatedValue / 1_000).toFixed(0)}K`
        }
        return `$${estimatedValue.toLocaleString()}`
    }
    if (sharesToSell) {
        return `${sharesToSell.toLocaleString()} shs`
    }
    return ''
}

function EmptyState() {
    return (
        <div className="flex flex-col items-center justify-center py-6 text-center">
            <FileWarning className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
                No recent Form 144 filings for your stocks
            </p>
            <p className="text-xs text-muted-foreground mt-1">
                Form 144 filings appear when insiders intend to sell restricted shares
            </p>
        </div>
    )
}
