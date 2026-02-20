// ABOUTME: Paper trading portfolios page with portfolio management and trade execution
// ABOUTME: Displays portfolio cards, holdings, transactions, and performance charts

import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import PortfolioCard from '@/components/PortfolioCard'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { Separator } from "@/components/ui/separator"
import {
    Plus,
    Trash2,
    TrendingUp,
    TrendingDown,
    Wallet,
    ArrowLeft,
    DollarSign,
    Activity,
    Clock,
    LineChart,
    AlertCircle,
    CheckCircle2,
    Briefcase,
    ArrowUpRight,
    ArrowDownRight,
    Bot,
    User,
    Play,
    Settings,
    Loader2
} from 'lucide-react'
import { format } from 'date-fns'
import { Line } from 'react-chartjs-2'
import { useAuth } from '@/context/AuthContext'
import BriefingsTab from '@/pages/portfolios/BriefingsTab'
import StrategyRunsTab from '@/pages/portfolios/StrategyRunsTab'
import PortfolioPerformanceChart from '@/components/portfolios/PortfolioPerformanceChart'
import { formatLocal } from '@/utils/formatters'

const LiveSignal = () => (
    <span className="bg-yellow-400 h-2 w-2 rounded-full mr-2 inline-block shadow-sm" />
)

// Format currency with commas and optional decimal places
const formatCurrency = (value, truncate = false) => {
    if (value === null || value === undefined) return '$0'
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: truncate ? 0 : 2,
        maximumFractionDigits: truncate ? 0 : 2
    }).format(value)
}

// Format percentage with sign
const formatPercent = (value) => {
    if (value === null || value === undefined) return '0.00%'
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)}%`
}

// Format date for display
const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

export default function Portfolios() {
    const { user } = useAuth()
    const { id } = useParams()
    const navigate = useNavigate()
    const [portfolios, setPortfolios] = useState([])
    const [selectedPortfolio, setSelectedPortfolio] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Create portfolio dialog state
    const [createDialogOpen, setCreateDialogOpen] = useState(false)
    const [creationStep, setCreationStep] = useState('choice') // 'choice' or 'form'
    const [newPortfolioName, setNewPortfolioName] = useState('')
    const [newPortfolioInitialCash, setNewPortfolioInitialCash] = useState('100000')
    const [creating, setCreating] = useState(false)

    // Reset step when dialog closes
    useEffect(() => {
        if (!createDialogOpen) {
            setCreationStep('choice')
            setNewPortfolioName('')
            setNewPortfolioInitialCash('100000')
        }
    }, [createDialogOpen])

    useEffect(() => {
        fetchPortfolios()
    }, [])

    // Handle deep linking to specific portfolio
    useEffect(() => {
        if (id) {
            fetchPortfolioById(id)
        } else {
            setSelectedPortfolio(null)
        }
    }, [id])

    const fetchPortfolioById = async (portfolioId) => {
        try {
            setLoading(true)
            const response = await fetch(`/api/portfolios/${portfolioId}`)
            if (response.ok) {
                const data = await response.json()
                setSelectedPortfolio(data)
            } else {
                console.error('Failed to fetch specific portfolio')
            }
        } catch (err) {
            console.error('Error fetching specific portfolio:', err)
        } finally {
            setLoading(false)
        }
    }

    const fetchPortfolios = async () => {
        try {
            setLoading(true)
            const response = await fetch('/api/portfolios')
            if (response.ok) {
                const data = await response.json()
                setPortfolios(data.portfolios || [])
            } else if (response.status === 401) {
                setError('Please log in to view portfolios')
            } else {
                throw new Error('Failed to fetch portfolios')
            }
        } catch (err) {
            console.error('Error fetching portfolios:', err)
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const createPortfolio = async () => {
        if (!newPortfolioName.trim()) return

        setCreating(true)
        try {
            const response = await fetch('/api/portfolios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: newPortfolioName.trim(),
                    initial_cash: parseFloat(newPortfolioInitialCash) || 100000
                })
            })

            if (response.ok) {
                const portfolio = await response.json()
                setPortfolios([portfolio, ...portfolios])
                setCreateDialogOpen(false)
                setNewPortfolioName('')
                setNewPortfolioInitialCash('100000')
            } else {
                throw new Error('Failed to create portfolio')
            }
        } catch (err) {
            console.error('Error creating portfolio:', err)
        } finally {
            setCreating(false)
        }
    }

    const deletePortfolio = async (portfolioId) => {
        if (!confirm('Delete this portfolio and all its transactions? This cannot be undone.')) return

        try {
            const response = await fetch(`/api/portfolios/${portfolioId}`, {
                method: 'DELETE'
            })

            if (response.ok) {
                setPortfolios(portfolios.filter(p => p.id !== portfolioId))
                if (selectedPortfolio?.id === portfolioId) {
                    navigate('/portfolios')
                }
            } else {
                throw new Error('Failed to delete portfolio')
            }
        } catch (err) {
            console.error('Error deleting portfolio:', err)
        }
    }

    const selectPortfolio = (portfolio) => {
        navigate(`/portfolios/${portfolio.id}`)
    }

    const refreshSelectedPortfolio = async () => {
        if (!selectedPortfolio) return
        await selectPortfolio(selectedPortfolio)
    }

    if (loading && portfolios.length === 0) {
        return (
            <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto">
                <div className="mb-8">
                    <Skeleton className="h-9 w-48" />
                </div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {[1, 2, 3].map(i => (
                        <Skeleton key={i} className="h-40 rounded-xl" />
                    ))}
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto">
                <Card className="border-destructive/50 bg-destructive/5">
                    <CardContent className="py-12 text-center">
                        <AlertCircle className="h-12 w-12 mx-auto mb-4 text-destructive opacity-50" />
                        <p className="text-destructive">{error}</p>
                    </CardContent>
                </Card>
            </div>
        )
    }

    // Show portfolio detail view
    if (selectedPortfolio) {
        return (
            <PortfolioDetail
                portfolio={selectedPortfolio}
                onBack={() => navigate('/portfolios')}
                onRefresh={refreshSelectedPortfolio}
                onDelete={() => deletePortfolio(selectedPortfolio.id)}
            />
        )
    }

    // Portfolio list view
    return (
        <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 sm:mb-8 min-w-0">
                <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="h-4 w-4 mr-2" />
                            New Portfolio
                        </Button>
                    </DialogTrigger>
                    <DialogContent className={creationStep === 'choice' ? 'sm:max-w-[600px]' : 'sm:max-w-[425px]'}>
                        <DialogHeader>
                            <DialogTitle>
                                {creationStep === 'choice' ? 'Create New Portfolio' : 'Self-Directed Portfolio'}
                            </DialogTitle>
                            <DialogDescription>
                                {creationStep === 'choice'
                                    ? 'Choose how you want to manage your new paper trading portfolio.'
                                    : 'Start a new paper trading portfolio with virtual cash.'
                                }
                            </DialogDescription>
                        </DialogHeader>

                        {creationStep === 'choice' ? (
                            <div className="grid grid-cols-2 gap-4 py-6">
                                <Card
                                    className="cursor-pointer hover:border-primary transition-colors border-2 border-muted"
                                    onClick={() => navigate('/strategies/new?marketplace=true')}
                                >
                                    <CardContent className="pt-6 flex flex-col items-center text-center">
                                        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                                            <Bot className="h-6 w-6 text-primary" />
                                        </div>
                                        <h3 className="font-bold mb-1">Autonomous</h3>
                                        <p className="text-sm text-muted-foreground">
                                            Managed by an AI strategy agent that trades automatically based on your rules.
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card
                                    className="cursor-pointer hover:border-primary transition-colors border-2 border-muted"
                                    onClick={() => setCreationStep('form')}
                                >
                                    <CardContent className="pt-6 flex flex-col items-center text-center">
                                        <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                                            <User className="h-6 w-6 text-muted-foreground" />
                                        </div>
                                        <h3 className="font-bold mb-1">Self-Directed</h3>
                                        <p className="text-sm text-muted-foreground">
                                            Manual paper trading. You choose which stocks to buy and sell yourself.
                                        </p>
                                    </CardContent>
                                </Card>
                            </div>
                        ) : (
                            <>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="name">Portfolio Name</Label>
                                        <Input
                                            id="name"
                                            placeholder="e.g., Tech Growth, Value Picks"
                                            value={newPortfolioName}
                                            onChange={(e) => setNewPortfolioName(e.target.value)}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="cash">Initial Cash</Label>
                                        <div className="relative">
                                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                                            <Input
                                                id="cash"
                                                type="number"
                                                className="pl-7"
                                                value={newPortfolioInitialCash}
                                                onChange={(e) => setNewPortfolioInitialCash(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setCreationStep('choice')}>
                                        Back
                                    </Button>
                                    <Button onClick={createPortfolio} disabled={creating || !newPortfolioName.trim()}>
                                        {creating ? 'Creating...' : 'Create Portfolio'}
                                    </Button>
                                </DialogFooter>
                            </>
                        )}
                    </DialogContent>
                </Dialog>
            </div>

            {portfolios.length === 0 ? (
                <Card className="border-dashed">
                    <CardContent className="py-16 text-center">
                        <Briefcase className="h-16 w-16 mx-auto mb-4 text-muted-foreground/30" />
                        <h3 className="text-lg font-medium mb-2">No portfolios yet</h3>
                        <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                            Create your first paper trading portfolio to start practicing investment strategies.
                        </p>
                        <Button onClick={() => setCreateDialogOpen(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Create Your First Portfolio
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 w-full min-w-0">
                    {portfolios.map(portfolio => (
                        <div key={portfolio.id} className="min-w-0 w-full">
                            <PortfolioCard
                                portfolio={portfolio}
                                onClick={() => selectPortfolio(portfolio)}
                                onDelete={() => deletePortfolio(portfolio.id)}
                            />
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}



function PortfolioDetail({ portfolio, onBack, onRefresh, onDelete }) {
    const navigate = useNavigate()
    const [searchParams, setSearchParams] = useSearchParams()
    const [activeTab, setActiveTab] = useState(portfolio.strategy_id ? 'briefings' : 'holdings')
    const [transactions, setTransactions] = useState([])
    const [valueHistory, setValueHistory] = useState([])
    const [loadingTransactions, setLoadingTransactions] = useState(false)
    const [loadingHistory, setLoadingHistory] = useState(false)
    const [runningJob, setRunningJob] = useState(null)
    const [briefingsRefreshKey, setBriefingsRefreshKey] = useState(0)

    // Poll job status when arriving from quick-start
    useEffect(() => {
        const jobId = searchParams.get('job')
        if (!jobId) return

        setRunningJob({ id: jobId, status: 'pending', progress: 0 })

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/jobs/${jobId}`)
                if (!response.ok) return
                const job = await response.json()
                setRunningJob({ id: jobId, status: job.status, progress_pct: job.progress_pct || 0, progress_message: job.progress_message || null })

                if (job.status === 'completed' || job.status === 'failed') {
                    clearInterval(pollInterval)
                    // Clear the job param from URL
                    searchParams.delete('job')
                    setSearchParams(searchParams, { replace: true })
                    if (job.status === 'completed') {
                        setActiveTab('briefings')
                        setBriefingsRefreshKey(k => k + 1)
                        onRefresh()
                    }
                }
            } catch (err) {
                console.error('Error polling job status:', err)
            }
        }, 3000)

        return () => clearInterval(pollInterval)
    }, [searchParams.get('job')])

    const totalValue = portfolio.total_value || 0
    const initialCash = portfolio.initial_cash || 100000
    const gainLoss = portfolio.gain_loss || 0
    const gainLossPercent = portfolio.gain_loss_percent || 0
    const cash = portfolio.cash || 0
    const holdingsValue = portfolio.holdings_value || 0
    const holdings = portfolio.holdings || {}
    const isPositive = gainLoss >= 0

    useEffect(() => {
        fetchValueHistory()
    }, [portfolio.id])

    useEffect(() => {
        if (activeTab === 'transactions') {
            fetchTransactions()
        }
    }, [activeTab, portfolio.id])

    const fetchTransactions = async () => {
        setLoadingTransactions(true)
        try {
            const response = await fetch(`/api/portfolios/${portfolio.id}/transactions`)
            if (response.ok) {
                const data = await response.json()
                setTransactions(data.transactions || [])
            }
        } catch (err) {
            console.error('Error fetching transactions:', err)
        } finally {
            setLoadingTransactions(false)
        }
    }

    const fetchValueHistory = async () => {
        setLoadingHistory(true)
        try {
            const response = await fetch(`/api/portfolios/${portfolio.id}/value-history`)
            if (response.ok) {
                const data = await response.json()
                setValueHistory(data.snapshots || [])
            }
        } catch (err) {
            console.error('Error fetching value history:', err)
        } finally {
            setLoadingHistory(false)
        }
    }

    return (
        <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold tracking-tight">{portfolio.name}</h1>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            Created {formatLocal(portfolio.created_at)}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {portfolio.strategy_id ? (
                        <>
                            <Badge variant="outline" className="border-primary/30 text-primary font-medium flex items-center gap-1 h-9 px-2 sm:px-3 shrink-0">
                                <Bot className="h-4 w-4" />
                                <span className="text-xs sm:text-sm">Autonomous</span>
                            </Badge>
                            <Badge variant={portfolio.strategy_enabled ? "success" : "destructive"} className="flex items-center h-9 px-2 sm:px-3 shrink-0">
                                {portfolio.strategy_enabled && <LiveSignal />}
                                <span className="text-xs sm:text-sm font-medium">{portfolio.strategy_enabled ? 'Active' : 'Paused'}</span>
                            </Badge>
                        </>
                    ) : (
                        <Badge variant="outline" className="text-muted-foreground font-medium flex items-center gap-1 h-9 px-2 sm:px-3 shrink-0">
                            <User className="h-4 w-4" />
                            <span className="text-xs sm:text-sm">Self-Directed</span>
                        </Badge>
                    )}
                    {portfolio.strategy_id && (
                        <Button
                            variant="outline"
                            size="sm"
                            className="h-9 px-2 sm:px-3 shrink-0"
                            onClick={() => navigate(`/strategies/${portfolio.strategy_id}/edit`)}
                        >
                            <span className="hidden sm:inline text-xs sm:text-sm font-medium">Strategy Detail</span>
                            <span className="inline sm:hidden text-xs">Strategy</span>
                        </Button>
                    )}
                    <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive h-9 w-9 shrink-0" onClick={onDelete}>
                        <Trash2 className="h-5 w-5" />
                    </Button>
                </div>
            </div>

            {/* Strategy run in progress banner */}
            {runningJob && runningJob.status !== 'completed' && (
                <Card className="mb-6 border-primary/30 bg-primary/5">
                    <CardContent className="py-4">
                        <div className="flex items-center gap-3">
                            {runningJob.status === 'failed' ? (
                                <>
                                    <AlertCircle className="h-5 w-5 text-destructive" />
                                    <div>
                                        <p className="font-medium text-destructive">Strategy run failed</p>
                                        <p className="text-sm text-muted-foreground">You can retry from the strategy settings.</p>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                                    <div>
                                        <p className="font-medium">Your strategy is running...</p>
                                        <p className="text-sm text-muted-foreground">
                                            {runningJob.progress_message || 'Screening stocks and building your briefing. This may take a few minutes.'}
                                        </p>
                                    </div>
                                </>
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Summary Cards */}
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-3 mb-6 w-full">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                            <DollarSign className="h-4 w-4" />
                            Total Value
                        </div>
                        <p className="text-2xl font-bold">{formatCurrency(totalValue, true)}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                            <Wallet className="h-4 w-4" />
                            Cash
                        </div>
                        <p className="text-2xl font-bold">{formatCurrency(cash, true)}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                            <Activity className="h-4 w-4" />
                            Holdings
                        </div>
                        <p className="text-2xl font-bold">{formatCurrency(holdingsValue, true)}</p>
                    </CardContent>
                </Card>
            </div>

            {/* Performance Chart - Highlighted */}
            <PortfolioPerformanceChart
                snapshots={valueHistory}
                loading={loadingHistory}
                liveTotalValue={totalValue}
                liveAlpha={portfolio.latest_alpha || 0}
                liveGainLoss={gainLoss}
                liveGainLossPercent={gainLossPercent}
            />

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <div className="mb-4">
                    <TabsList className="w-full sm:w-auto flex sm:inline-flex justify-between sm:justify-start h-10 bg-muted/50 p-1">
                        {portfolio.strategy_id && <TabsTrigger value="briefings" className="px-1.5 sm:px-4 text-sm">Briefs</TabsTrigger>}
                        {portfolio.strategy_id && <TabsTrigger value="runs" className="px-1.5 sm:px-4 text-sm">Runs</TabsTrigger>}
                        <TabsTrigger value="holdings" className="px-1.5 sm:px-4 text-sm">Holdings</TabsTrigger>
                        {!portfolio.strategy_id && <TabsTrigger value="trade" className="px-1.5 sm:px-4 text-sm">Trade</TabsTrigger>}
                        <TabsTrigger value="transactions" className="px-1.5 sm:px-4 text-sm">Transactions</TabsTrigger>
                    </TabsList>
                </div>

                {portfolio.strategy_id && (
                    <TabsContent value="briefings">
                        <BriefingsTab portfolioId={portfolio.id} refreshKey={briefingsRefreshKey} />
                    </TabsContent>
                )}

                {portfolio.strategy_id && (
                    <TabsContent value="runs">
                        <StrategyRunsTab strategyId={portfolio.strategy_id} runsCount={portfolio.strategy_runs_count} />
                    </TabsContent>
                )}

                <TabsContent value="holdings">
                    <HoldingsTab portfolio={portfolio} />
                </TabsContent>

                {!portfolio.strategy_id && (
                    <TabsContent value="trade">
                        <TradeTab
                            portfolioId={portfolio.id}
                            cash={cash}
                            holdings={holdings}
                            onTradeComplete={onRefresh}
                        />
                    </TabsContent>
                )}

                <TabsContent value="transactions">
                    <TransactionsTab
                        transactions={transactions}
                        loading={loadingTransactions}
                    />
                </TabsContent>
            </Tabs>
        </div>
    )
}

function HoldingsTab({ portfolio }) {
    // Check if we have detailed holdings data
    const holdingsDetailed = portfolio?.holdings_detailed || []

    if (holdingsDetailed.length === 0) {
        return (
            <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p>No holdings yet. Start trading to build your portfolio.</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Symbol</TableHead>
                        <TableHead className="text-right">Shares</TableHead>
                        <TableHead className="text-right">Purchase Price</TableHead>
                        <TableHead className="text-right">Current Price</TableHead>
                        <TableHead className="text-right">Total Cost</TableHead>
                        <TableHead className="text-right">Current Value</TableHead>
                        <TableHead className="text-right">Gain/Loss</TableHead>
                        <TableHead className="text-right">Yield %</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {holdingsDetailed.map((holding) => {
                        const isPositive = holding.gain_loss >= 0
                        return (
                            <TableRow key={holding.symbol}>
                                <TableCell className="font-medium">
                                    <Link to={`/stock/${holding.symbol}`} className="hover:underline text-primary">
                                        {holding.symbol}
                                    </Link>
                                </TableCell>
                                <TableCell className="text-right">{holding.quantity}</TableCell>
                                <TableCell className="text-right">{formatCurrency(holding.avg_purchase_price)}</TableCell>
                                <TableCell className="text-right">{formatCurrency(holding.current_price)}</TableCell>
                                <TableCell className="text-right">{formatCurrency(holding.total_cost)}</TableCell>
                                <TableCell className="text-right">{formatCurrency(holding.current_value)}</TableCell>
                                <TableCell className={`text-right font-medium ${isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
                                    {formatCurrency(holding.gain_loss)}
                                </TableCell>
                                <TableCell className={`text-right font-medium ${isPositive ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
                                    {formatPercent(holding.gain_loss_percent)}
                                </TableCell>
                            </TableRow>
                        )
                    })}
                </TableBody>
            </Table>
        </Card>
    )
}

function TradeTab({ portfolioId, cash, holdings, onTradeComplete }) {
    const [symbol, setSymbol] = useState('')
    const [quantity, setQuantity] = useState('')
    const [transactionType, setTransactionType] = useState('BUY')
    const [note, setNote] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [result, setResult] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!symbol.trim() || !quantity) return

        setSubmitting(true)
        setResult(null)

        try {
            const response = await fetch(`/api/portfolios/${portfolioId}/trade`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: symbol.toUpperCase().trim(),
                    transaction_type: transactionType,
                    quantity: parseInt(quantity),
                    note: note.trim() || undefined
                })
            })

            const data = await response.json()

            if (data.success) {
                setResult({ type: 'success', message: `Successfully ${transactionType === 'BUY' ? 'bought' : 'sold'} ${quantity} shares of ${symbol.toUpperCase()} at ${formatCurrency(data.price_per_share)}` })
                setSymbol('')
                setQuantity('')
                setNote('')
                onTradeComplete()
            } else {
                setResult({ type: 'error', message: data.error || 'Trade failed' })
            }
        } catch (err) {
            setResult({ type: 'error', message: 'Failed to execute trade' })
        } finally {
            setSubmitting(false)
        }
    }

    const maxSellQuantity = holdings?.[symbol.toUpperCase()] || 0

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg">Execute Trade</CardTitle>
                <CardDescription>
                    Available cash: {formatCurrency(cash)}
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-3">
                        <div className="space-y-2">
                            <Label htmlFor="symbol">Symbol</Label>
                            <Input
                                id="symbol"
                                placeholder="e.g., AAPL"
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                className="uppercase"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="type">Action</Label>
                            <Select value={transactionType} onValueChange={setTransactionType}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="BUY">
                                        <span className="flex items-center gap-2">
                                            <ArrowUpRight className="h-4 w-4 text-emerald-500" />
                                            Buy
                                        </span>
                                    </SelectItem>
                                    <SelectItem value="SELL">
                                        <span className="flex items-center gap-2">
                                            <ArrowDownRight className="h-4 w-4 text-red-500" />
                                            Sell
                                        </span>
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="quantity">Shares</Label>
                            <Input
                                id="quantity"
                                type="number"
                                min="1"
                                placeholder="Number of shares"
                                value={quantity}
                                onChange={(e) => setQuantity(e.target.value)}
                            />
                            {transactionType === 'SELL' && symbol && maxSellQuantity > 0 && (
                                <p className="text-xs text-muted-foreground">
                                    You own {maxSellQuantity} shares
                                </p>
                            )}
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="note">Note (optional)</Label>
                        <Input
                            id="note"
                            placeholder="e.g., Bought on earnings dip"
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                        />
                    </div>

                    {result && (
                        <div className={`flex items-center gap-2 p-3 rounded-lg ${result.type === 'success'
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                            : 'bg-red-500/10 text-red-600 dark:text-red-400'
                            }`}>
                            {result.type === 'success' ? (
                                <CheckCircle2 className="h-4 w-4" />
                            ) : (
                                <AlertCircle className="h-4 w-4" />
                            )}
                            <span className="text-sm">{result.message}</span>
                        </div>
                    )}

                    <Button
                        type="submit"
                        disabled={submitting || !symbol.trim() || !quantity}
                        className={transactionType === 'BUY'
                            ? 'bg-emerald-600 hover:bg-emerald-700'
                            : 'bg-red-600 hover:bg-red-700'
                        }
                    >
                        {submitting ? 'Processing...' : `${transactionType === 'BUY' ? 'Buy' : 'Sell'} ${symbol.toUpperCase() || 'Stock'}`}
                    </Button>
                </form>
            </CardContent>
        </Card>
    )
}

function TransactionsTab({ transactions, loading }) {
    if (loading) {
        return (
            <Card>
                <CardContent className="py-8">
                    <div className="space-y-3">
                        {[1, 2, 3].map(i => (
                            <Skeleton key={i} className="h-12 w-full" />
                        ))}
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (transactions.length === 0) {
        return (
            <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-20" />
                    <p>No transactions yet.</p>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Symbol</TableHead>
                        <TableHead className="text-right">Shares</TableHead>
                        <TableHead className="text-right">Price</TableHead>
                        <TableHead className="text-right">Total</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {transactions.map(tx => (
                        <TableRow key={tx.id}>
                            <TableCell className="text-muted-foreground text-sm">
                                {formatLocal(tx.executed_at)}
                            </TableCell>
                            <TableCell>
                                <Badge
                                    variant="outline"
                                    className={tx.transaction_type === 'BUY'
                                        ? 'border-emerald-500/50 text-emerald-600 dark:text-emerald-400'
                                        : 'border-red-500/50 text-red-600 dark:text-red-400'
                                    }
                                >
                                    {tx.transaction_type}
                                </Badge>
                            </TableCell>
                            <TableCell className="font-medium">{tx.symbol}</TableCell>
                            <TableCell className="text-right">{tx.quantity}</TableCell>
                            <TableCell className="text-right">{formatCurrency(tx.price_per_share)}</TableCell>
                            <TableCell className="text-right font-medium">
                                {formatCurrency(tx.total_value)}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Card>
    )
}

