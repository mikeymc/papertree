// ABOUTME: Multi-step onboarding wizard for new users
// ABOUTME: Collects expertise level, character preference, theme, and optionally launches a quick-start strategy

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from './theme-provider'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from './ui/dialog'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

const STEPS = {
    WELCOME: 1,
    STRATEGY: 2,
    READY: 3,
}

const TOTAL_STEPS = 3




export function OnboardingWizard({ open, onComplete, onSkip }) {
    const [currentStep, setCurrentStep] = useState(STEPS.WELCOME)
    const [selections, setSelections] = useState({
        expertise: 'practicing', // default
        character: 'lynch', // default
    })
    const [loading, setLoading] = useState(false)
    const [templates, setTemplates] = useState({})
    const [selectedTemplate, setSelectedTemplate] = useState(null)
    const [launchingTemplate, setLaunchingTemplate] = useState(null)

    const navigate = useNavigate()
    const { user, checkAuth } = useAuth()
    const { setTheme } = useTheme()


    // Fetch strategy templates when reaching the strategy step
    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const response = await fetch('/api/strategy-templates')
                const data = await response.json()
                setTemplates(data.templates || {})
            } catch (error) {
                console.error('Failed to fetch templates:', error)
            }
        }

        if (currentStep === STEPS.STRATEGY) {
            fetchTemplates()
        }
    }, [currentStep])

    const handleNext = () => {
        if (currentStep === STEPS.WELCOME) {
            // Save settings then advance to strategy step
            saveSettings().then(() => {
                setCurrentStep(STEPS.STRATEGY)
            })
        } else if (currentStep < STEPS.READY) {
            setCurrentStep(currentStep + 1)
        }
    }

    const handleBack = () => {
        if (currentStep === STEPS.STRATEGY) {
            setCurrentStep(STEPS.WELCOME)
        } else if (currentStep > STEPS.WELCOME) {
            setCurrentStep(currentStep - 1)
        }
    }

    const saveSettings = async () => {
        setLoading(true)
        try {
            // Save expertise level
            await fetch('/api/settings/expertise-level', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ expertise_level: selections.expertise }),
            })

            // Save character preference
            await fetch('/api/settings/character', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ character_id: selections.character }),
            })

            // Update localStorage for character
            localStorage.setItem('activeCharacter', selections.character)
            window.dispatchEvent(new CustomEvent('characterChanged', {
                detail: { character: selections.character }
            }))
        } catch (error) {
            console.error('Failed to save settings:', error)
        } finally {
            setLoading(false)
        }
    }

    const finishOnboarding = async (navigateTo = null) => {
        setLoading(true)
        try {
            // Mark onboarding as complete
            await fetch('/api/user/complete_onboarding', {
                method: 'POST',
                credentials: 'include',
            })

            // Refresh auth state
            await checkAuth()

            if (navigateTo) {
                navigate(navigateTo)
            }

            if (onComplete) {
                onComplete()
            }
        } catch (error) {
            console.error('Failed to complete onboarding:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleComplete = async (goToHelp = false) => {
        await saveSettings()
        await finishOnboarding(goToHelp ? '/help' : null)
    }

    const handleQuickStart = async (templateId) => {
        setLaunchingTemplate(templateId)
        try {
            const response = await fetch('/api/strategies/quick-start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ template_id: templateId }),
            })

            if (!response.ok) {
                throw new Error('Failed to create strategy')
            }

            const data = await response.json()

            // Finish onboarding and navigate to the new portfolio with job tracking
            await finishOnboarding(`/portfolios/${data.portfolio_id}?job=${data.job_id}`)
        } catch (error) {
            console.error('Failed to quick-start strategy:', error)
            setLaunchingTemplate(null)
        }
    }

    const handleSkip = async () => {
        setLoading(true)
        try {
            // Just mark onboarding as complete without changing settings
            await fetch('/api/user/complete_onboarding', {
                method: 'POST',
                credentials: 'include',
            })
            await checkAuth()

            if (onSkip) {
                onSkip()
            }
        } catch (error) {
            console.error('Failed to skip onboarding:', error)
        } finally {
            setLoading(false)
        }
    }

    const updateSelection = (key, value) => {
        setSelections(prev => ({ ...prev, [key]: value }))
    }


    // Get hardcoded template IDs for onboarding
    const getRecommendedTemplates = () => {
        return ['global_titans', 'lynch_tenbagger', 'buffett_fortress']
    }

    return (
        <Dialog open={open} onOpenChange={() => { }}>
            <DialogContent className="sm:max-w-[600px]" hideClose>
                {/* Progress dots */}
                <div className="flex justify-center gap-2 mb-4">
                    {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((step) => (
                        <div
                            key={step}
                            className={`h-2 w-2 rounded-full transition-colors ${step === currentStep
                                ? 'bg-primary'
                                : step < currentStep
                                    ? 'bg-primary/50'
                                    : 'bg-muted'
                                }`}
                        />
                    ))}
                </div>

                {/* Step 1: Welcome Screen */}
                {currentStep === STEPS.WELCOME && (
                    <div className="text-center py-6">
                        <DialogHeader>
                            <DialogTitle className="text-2xl mb-2">Welcome to papertree.ai</DialogTitle>
                            <DialogDescription className="text-base">
                                <p>There's a lot to explore. Let's start by launching your first autonomous investment portfolio.</p>
                            </DialogDescription>
                        </DialogHeader>

                        <div className="mt-8 flex justify-center">
                            <div className="bg-primary/10 p-6 rounded-full w-24 h-24 flex items-center justify-center mb-6 mx-auto">
                                <span className="text-4xl">🚀</span>
                            </div>
                        </div>

                        <div className="mt-8">
                            <Button onClick={handleNext} size="lg" className="w-full sm:w-auto min-w-[200px]">
                                Let's Go
                            </Button>
                            <div className="mt-4">
                                <Button variant="ghost" onClick={handleSkip} size="sm">
                                    Skip setup
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
                {/* Step 4: Strategy Selection */}
                {currentStep === STEPS.STRATEGY && (
                    <>
                        <DialogHeader>
                            <DialogTitle>Choose a strategy</DialogTitle>
                            <DialogDescription>
                                You can always change it later.
                            </DialogDescription>
                        </DialogHeader>

                        <div className="grid gap-3 mt-4 max-h-[400px] overflow-y-auto pr-2">
                            {getRecommendedTemplates().map((templateId) => {
                                const template = templates[templateId]
                                if (!template) return null
                                const isSelected = selectedTemplate === templateId
                                return (
                                    <Card
                                        key={templateId}
                                        className={`cursor-pointer transition-colors ${isSelected ? 'border-primary bg-primary/5 ring-1 ring-primary' : 'hover:border-primary/50'}`}
                                        onClick={() => setSelectedTemplate(templateId)}
                                    >
                                        <CardHeader className="pb-2 p-4">
                                            <div className="flex items-center justify-between">
                                                <CardTitle className="text-base">{template.name}</CardTitle>
                                                {isSelected && (
                                                    <div className="h-4 w-4 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-[10px]">✓</div>
                                                )}
                                            </div>
                                            <CardDescription className="text-xs mt-1">{template.description}</CardDescription>
                                        </CardHeader>
                                    </Card>
                                )
                            })}
                        </div>

                        <div className="flex justify-between mt-6">
                            <Button variant="outline" onClick={handleBack}>
                                Back
                            </Button>
                            <div className="flex gap-2">
                                <Button
                                    variant="ghost"
                                    onClick={() => finishOnboarding()}
                                >
                                    I'll set up my own
                                </Button>
                                <Button
                                    onClick={handleNext}
                                    disabled={!selectedTemplate}
                                >
                                    Next
                                </Button>
                            </div>
                        </div>
                    </>
                )}

                {/* Step 5: Ready to Launch */}
                {currentStep === STEPS.READY && (
                    <>
                        <DialogHeader>
                            <DialogTitle>All set!</DialogTitle>
                            <DialogDescription className="text-base mt-4 space-y-4">
                                <p>Your <b>{templates[selectedTemplate]?.name}</b> portfolio will be managed autonomously using a combination of quantitative analysis and fundamental research.</p>
                                <p>Every day, we will study the market and adjust your holdings to maximize returns. You will receive a daily brief and have access to an audit trail of every decision and transaction we make.</p>
                            </DialogDescription>
                        </DialogHeader>

                        <div className="py-8 flex flex-col items-center">
                            <div className="h-16 w-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
                                <span className="text-2xl">✨</span>
                            </div>
                            <p className="text-center text-muted-foreground max-w-sm">
                                Let's launch your portfolio now.
                            </p>
                            <p className="text-center text-muted-foreground max-w-sm">
                                Ready?
                            </p>

                        </div>

                        <div className="flex justify-between mt-2">
                            <Button variant="outline" onClick={handleBack} disabled={loading}>
                                Back
                            </Button>
                            <Button
                                onClick={() => handleQuickStart(selectedTemplate)}
                                disabled={loading}
                                size="lg"
                                className="px-8"
                            >
                                {loading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                        Launching...
                                    </>
                                ) : (
                                    'Launch Portfolio'
                                )}
                            </Button>
                        </div>
                    </>
                )}
            </DialogContent>
        </Dialog>
    )
}
