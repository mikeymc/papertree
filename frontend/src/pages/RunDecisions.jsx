import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DecisionsView } from '@/components/strategies/DecisionsView'
import { Skeleton } from '@/components/ui/skeleton'

export default function RunDecisions() {
    const { id, runId } = useParams()
    const navigate = useNavigate()
    const [strategy, setStrategy] = useState(null)
    const [runs, setRuns] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStrategy = async () => {
            try {
                const response = await fetch(`/api/strategies/${id}`)
                if (response.ok) {
                    const data = await response.json()
                    setStrategy(data.strategy)
                    setRuns(data.runs)
                }
            } catch (error) {
                console.error("Failed to fetch strategy", error)
            } finally {
                setLoading(false)
            }
        }
        fetchStrategy()
    }, [id])

    if (loading) {
        return (
            <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto space-y-6">
                <Skeleton className="h-10 w-48" />
                <Skeleton className="h-64 w-full" />
            </div>
        )
    }

    return (
        <div className="container px-2 sm:px-4 py-4 sm:py-8 max-w-5xl mx-auto space-y-6">
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="h-8 px-2">
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    Back
                </Button>
                <div>
                    <h1 className="text-xl font-bold tracking-tight">{strategy?.name}</h1>
                    <p className="text-sm text-muted-foreground">Run Analysis</p>
                </div>
            </div>

            <DecisionsView runId={runId} runs={runs} onRunChange={() => { }} />
        </div>
    )
}
