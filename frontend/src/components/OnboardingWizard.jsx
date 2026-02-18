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
import { RadioGroup, RadioGroupItem } from './ui/radio-group'
import { Label } from './ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

const STEPS = {
    EXPERTISE: 1,
    CHARACTER: 2,
    LAUNCH_STRATEGY: 3,
}

const TOTAL_STEPS = 3

const EXPERTISE_LEVELS = [
    {
        id: 'learning',
        name: 'Learning',
        description: 'I am new to investing and want to build a solid foundation.',
    },
    {
        id: 'practicing',
        name: 'Practicing',
        description: 'I have a working knowledge of investing and want to deepen my understanding.',
    },
    {
        id: 'expert',
        name: 'Expert',
        description: 'I am comfortable with complex finance concepts and investing terminology.',
    },
]



export function OnboardingWizard({ open, onComplete, onSkip }) {
    const [currentStep, setCurrentStep] = useState(STEPS.EXPERTISE)
    const [selections, setSelections] = useState({
        expertise: 'practicing', // default
        character: 'lynch', // default
    })
    const [characters, setCharacters] = useState([])
    const [loading, setLoading] = useState(false)
    const [charactersLoading, setCharactersLoading] = useState(true)
    const [templates, setTemplates] = useState({})
    const [recommendations, setRecommendations] = useState({})
    const [launchingTemplate, setLaunchingTemplate] = useState(null)

    const navigate = useNavigate()
    const { user, checkAuth } = useAuth()
    const { setTheme } = useTheme()

    // Fetch available characters
    useEffect(() => {
        const fetchCharacters = async () => {
            try {
                const response = await fetch('/api/characters')
                const data = await response.json()
                setCharacters(data.characters || [])
            } catch (error) {
                console.error('Failed to fetch characters:', error)
            } finally {
                setCharactersLoading(false)
            }
        }

        if (open) {
            fetchCharacters()
        }
    }, [open])

    // Fetch strategy templates when reaching the launch step
    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const response = await fetch('/api/strategy-templates')
                const data = await response.json()
                setTemplates(data.templates || {})
                setRecommendations(data.character_recommendations || {})
            } catch (error) {
                console.error('Failed to fetch templates:', error)
            }
        }

        if (currentStep === STEPS.LAUNCH_STRATEGY) {
            fetchTemplates()
        }
    }, [currentStep])

    const handleNext = () => {
        if (currentStep === STEPS.CHARACTER) {
            // Save settings then advance to launch step
            saveSettings().then(() => {
                setCurrentStep(STEPS.LAUNCH_STRATEGY)
            })
        } else if (currentStep < STEPS.LAUNCH_STRATEGY) {
            setCurrentStep(currentStep + 1)
        }
    }

    const handleBack = () => {
        if (currentStep > STEPS.EXPERTISE) {
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

    const getCharacterName = (id) => {
        const char = characters.find(c => c.id === id)
        return char ? char.name : id
    }

    const getExpertiseName = (id) => {
        const level = EXPERTISE_LEVELS.find(l => l.id === id)
        return level ? level.name : id
    }

    // Get recommended template IDs for the selected character
    const getRecommendedTemplates = () => {
        const charRecs = recommendations[selections.character] || []
        // Show character-specific recommendations, fall back to first 3 templates
        if (charRecs.length > 0) {
            return charRecs.filter(id => templates[id])
        }
        return Object.keys(templates).slice(0, 3)
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

                {/* Step 1: Expertise Level */}
                {currentStep === STEPS.EXPERTISE && (
                    <>
                        <DialogHeader>
                            <DialogTitle>What is your expertise level?</DialogTitle>
                            <DialogDescription>
                                This helps us tailor the interaction style of written analyses and chat responses.
                            </DialogDescription>
                        </DialogHeader>

                        <RadioGroup
                            value={selections.expertise}
                            onValueChange={(value) => updateSelection('expertise', value)}
                            className="gap-4 mt-4"
                        >
                            {EXPERTISE_LEVELS.map((level) => (
                                <div key={level.id} className="flex items-start gap-3 space-x-0">
                                    <RadioGroupItem
                                        value={level.id}
                                        id={`expertise-${level.id}`}
                                        className="mt-1"
                                    />
                                    <div className="flex flex-col">
                                        <Label htmlFor={`expertise-${level.id}`} className="font-medium cursor-pointer">
                                            {level.name}
                                        </Label>
                                        <span className="text-sm text-muted-foreground">
                                            {level.description}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </RadioGroup>

                        <div className="flex justify-end mt-6">
                            <div className="flex gap-2">
                                <Button variant="ghost" onClick={handleSkip} disabled={loading}>
                                    Skip for now
                                </Button>
                                <Button onClick={handleNext} disabled={loading}>
                                    Next
                                </Button>
                            </div>
                        </div>
                    </>
                )}

                {/* Step 2: Character Selection */}
                {currentStep === STEPS.CHARACTER && (
                    <>
                        <DialogHeader>
                            <DialogTitle>Choose your investment philosophy</DialogTitle>
                            <DialogDescription>
                                This shapes the scoring algorithm, investment thesis, chart analysis, and chat responses.
                            </DialogDescription>
                        </DialogHeader>

                        {charactersLoading ? (
                            <div className="flex justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                            </div>
                        ) : (
                            <RadioGroup
                                value={selections.character}
                                onValueChange={(value) => updateSelection('character', value)}
                                className="gap-4 mt-4"
                            >
                                {characters.map((char) => (
                                    <div key={char.id} className="flex items-start gap-3 space-x-0">
                                        <RadioGroupItem
                                            value={char.id}
                                            id={`char-${char.id}`}
                                            className="mt-1"
                                        />
                                        <div className="flex flex-col">
                                            <Label htmlFor={`char-${char.id}`} className="font-medium cursor-pointer">
                                                {char.name}
                                            </Label>
                                            <span className="text-sm text-muted-foreground">
                                                {char.description}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </RadioGroup>
                        )}

                        <div className="flex justify-between mt-6">
                            <Button variant="outline" onClick={handleBack} disabled={loading}>
                                Back
                            </Button>
                            <div className="flex gap-2">
                                <Button variant="ghost" onClick={handleSkip} disabled={loading}>
                                    Skip for now
                                </Button>
                                <Button onClick={handleNext} disabled={loading || charactersLoading}>
                                    Next
                                </Button>
                            </div>
                        </div>
                    </>
                )}





                {/* Step 5: Launch Strategy */}
                {currentStep === STEPS.LAUNCH_STRATEGY && (
                    <>
                        <DialogHeader>
                            <DialogTitle>Launch your first AI-managed portfolio</DialogTitle>
                            <DialogDescription>
                                Pick a strategy below and we'll start right away.
                            </DialogDescription>
                        </DialogHeader>

                        <div className="grid gap-3 mt-4">
                            {getRecommendedTemplates().map((templateId) => {
                                const template = templates[templateId]
                                if (!template) return null
                                const isLaunching = launchingTemplate === templateId
                                return (
                                    <Card
                                        key={templateId}
                                        className="cursor-pointer hover:border-primary transition-colors"
                                        onClick={() => !launchingTemplate && handleQuickStart(templateId)}
                                    >
                                        <CardHeader className="pb-2">
                                            <div className="flex items-center justify-between">
                                                <CardTitle className="text-base">{template.name}</CardTitle>
                                                <Button
                                                    size="sm"
                                                    disabled={!!launchingTemplate}
                                                    onClick={(e) => {
                                                        e.stopPropagation()
                                                        handleQuickStart(templateId)
                                                    }}
                                                >
                                                    {isLaunching ? (
                                                        <>
                                                            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                                                            Launching...
                                                        </>
                                                    ) : (
                                                        'Launch'
                                                    )}
                                                </Button>
                                            </div>
                                            <CardDescription>{template.description}</CardDescription>
                                        </CardHeader>
                                    </Card>
                                )
                            })}
                        </div>

                        <div className="flex justify-between mt-6">
                            <Button variant="outline" onClick={handleBack} disabled={!!launchingTemplate}>
                                Back
                            </Button>
                            <Button
                                variant="ghost"
                                onClick={() => finishOnboarding()}
                                disabled={!!launchingTemplate}
                            >
                                I'll set up my own
                            </Button>
                        </div>
                    </>
                )}
            </DialogContent>
        </Dialog>
    )
}
