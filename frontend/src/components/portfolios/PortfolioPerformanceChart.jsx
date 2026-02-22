import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Separator } from "@/components/ui/separator"
import { LineChart } from 'lucide-react'
import { Line } from 'react-chartjs-2'
import { format } from 'date-fns'

// Chart.js registration is usually done globally in the app, 
// but we assume it's already done since it's used in Portfolios.jsx

const formatCurrency = (value, truncate = false) => {
    if (value === null || value === undefined) return '$0'
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: truncate ? 0 : 2,
        maximumFractionDigits: truncate ? 0 : 2
    }).format(value)
}

const formatPercent = (value) => {
    if (value === null || value === undefined) return '0.00%'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
}

const PERIODS = [
    { label: '1W', days: 7 },
    { label: '1M', days: 30 },
    { label: '3M', days: 90 },
    { label: '6M', days: 180 },
    { label: 'YTD', days: null, ytd: true },
    { label: '1Y', days: 365 },
    { label: 'ALL', days: null },
]

function filterSnapshotsByPeriod(snapshots, period) {
    if (!period || period.label === 'ALL') return snapshots
    const now = new Date()
    let cutoff
    if (period.ytd) {
        cutoff = new Date(now.getFullYear(), 0, 1)
    } else {
        cutoff = new Date(now.getTime() - period.days * 24 * 60 * 60 * 1000)
    }
    return snapshots.filter(s => new Date(s.snapshot_at) >= cutoff)
}

export default function PortfolioPerformanceChart({
    snapshots,
    loading,
    liveTotalValue,
    liveAlpha,
    liveGainLoss,
    liveGainLossPercent
}) {
    const [period, setPeriod] = useState(PERIODS[PERIODS.length - 1]) // ALL

    const filteredSnapshots = useMemo(() => {
        return filterSnapshotsByPeriod(snapshots, period)
    }, [snapshots, period])

    // Aggregate intraday snapshots to one point per trading day (last snapshot of each day)
    // If period is 1W, show all intraday snapshots for better resolution
    const daily = useMemo(() => {
        if (!filteredSnapshots || filteredSnapshots.length === 0) return []
        if (period.label === '1W') return filteredSnapshots;

        const dailyMap = {};
        for (const s of filteredSnapshots) {
            const day = new Date(s.snapshot_at).toISOString().slice(0, 10);
            if (day && day !== 'Invalid') dailyMap[day] = s;
        }
        return Object.keys(dailyMap).sort().map(day => dailyMap[day]);
    }, [filteredSnapshots, period.label]);

    // Prepare chart data from daily-aggregated points
    const chartData = useMemo(() => {
        return {
            labels: daily.map(s => {
                const date = new Date(s.snapshot_at);
                return period.label === '1W'
                    ? format(date, 'MMM d, h:mm a')
                    : format(date, 'MMM d');
            }),
            datasets: [
                {
                    label: 'Portfolio Return',
                    data: daily.map(s => s.portfolio_return_pct),
                    borderColor: 'rgb(34, 197, 94)', // Green
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: true,
                    tension: 0.2,
                    pointRadius: daily.length > 30 ? 0 : 3,
                    pointHoverRadius: 5,
                },
                {
                    label: 'S&P 500',
                    data: daily.map(s => s.spy_return_pct),
                    borderColor: 'rgb(148, 163, 184)', // Slate
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                }
            ]
        }
    }, [daily, period.label]);

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(2) + '%';
                        }
                        return label;
                    }
                }
            },
        },
        scales: {
            x: {
                ticks: {
                    maxTicksLimit: 10,
                    maxRotation: 0,
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Return (%)'
                },
                ticks: {
                    callback: function (value) {
                        return value.toFixed(1) + '%';
                    }
                }
            }
        }
    }

    const latest = daily[daily.length - 1] || snapshots[snapshots.length - 1] || {};
    const currentReturn = liveGainLossPercent !== undefined ? liveGainLossPercent : (latest.portfolio_return_pct || 0);
    const alpha = liveAlpha !== undefined ? liveAlpha : (latest.alpha || 0);
    const currentSpyReturn = currentReturn - alpha;
    const displayTotalValue = liveTotalValue !== undefined ? liveTotalValue : (latest.total_value || 0);

    if (loading) {
        return (
            <Card className="mb-6">
                <CardContent className="py-8">
                    <Skeleton className="h-64 w-full" />
                </CardContent>
            </Card>
        )
    }

    if (!snapshots || snapshots.length === 0) {
        return (
            <Card className="mb-6">
                <CardContent className="py-12 text-center text-muted-foreground">
                    <LineChart className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p>No performance data yet.</p>
                    <p className="text-sm mt-1">Portfolio snapshots are taken every 15 minutes during market hours.</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card className="mb-6">
            <CardHeader className="pb-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <CardTitle className="text-lg">Performance vs Benchmark</CardTitle>
                        <CardDescription>
                            Comparing returns against S&P 500 (SPY)
                        </CardDescription>
                    </div>
                    {/* Period selector */}
                    <div className="flex gap-1 flex-wrap">
                        {PERIODS.map(p => (
                            <button
                                key={p.label}
                                onClick={() => setPeriod(p)}
                                className={`px-2 py-1 text-xs rounded font-medium transition-colors ${period.label === p.label
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                                    }`}
                            >
                                {p.label}
                            </button>
                        ))}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] sm:h-[350px] w-full mb-6">
                    <Line data={chartData} options={chartOptions} />
                </div>

                <Separator className="my-4" />

                {/* Stats summary */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                        <p className="text-xs text-muted-foreground">Portfolio Return</p>
                        <p className={`text-lg font-bold ${currentReturn >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                            {formatPercent(currentReturn)}
                        </p>
                        {liveGainLoss !== undefined && (
                            <p className={`text-xs ${currentReturn >= 0 ? 'text-emerald-500/80' : 'text-red-500/80'}`}>
                                {formatCurrency(liveGainLoss, true)}
                            </p>
                        )}
                    </div>
                    <div>
                        <p className="text-xs text-muted-foreground">SPY Return</p>
                        <p className="text-lg font-bold text-slate-400">{formatPercent(currentSpyReturn)}</p>
                    </div>
                    <div>
                        <p className="text-xs text-muted-foreground">Alpha vs SPY</p>
                        <p className={`text-lg font-bold ${alpha >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                            {formatPercent(alpha)}
                        </p>
                    </div>
                    <div>
                        <p className="text-xs text-muted-foreground">Current Value</p>
                        <p className="text-lg font-bold">{formatCurrency(displayTotalValue, true)}</p>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
