import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
    X, ChevronRight, ChevronLeft, Check, Plus, Trash2,
    HelpCircle, AlertCircle, Info, Save, Activity, Bot, TrendingDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { formatLocal } from '@/utils/formatters';

const StrategySettings = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const mode = id ? 'edit' : 'create';

    const [step, setStep] = useState(1); // Keep internal step for highlighting sections if needed, but display all
    const [selectedTemplate, setSelectedTemplate] = useState('');
    const [templates, setTemplates] = useState({});
    const [templatesLoaded, setTemplatesLoaded] = useState(false);

    // Default values
    const defaults = {
        name: '',
        description: '',
        conditions: {
            filters: [],
            require_thesis: true,
            scoring_requirements: [
                { character: 'lynch', min_score: 60 },
                { character: 'buffett', min_score: 60 }
            ],
            addition_scoring_requirements: [
                { character: 'lynch', min_score: 70 },
                { character: 'buffett', min_score: 70 }
            ],
            thesis_verdict_required: ['BUY']
        },
        consensus_mode: 'both_agree',
        consensus_threshold: 70,
        veto_score_threshold: 30,
        exit_conditions: {
            profit_target_pct: '',
            stop_loss_pct: '',
            max_hold_days: '',
            score_degradation: {
                lynch_below: '',
                buffett_below: ''
            }
        },
        portfolio_selection: 'new',
        portfolio_id: 'new',
        new_portfolio_name: '',
        initial_cash: 100000,
        position_sizing: {
            method: 'equal_weight',
            max_position_pct: 10.0,
            max_positions: 50,
            min_position_value: 500,
            fixed_position_pct: '',
            kelly_fraction: ''
        },
        schedule_cron: '0 9 * * 1-5'
    };

    const [formData, setFormData] = useState(defaults);
    const [portfolios, setPortfolios] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(mode === 'edit');

    // Fetch data on mount
    useEffect(() => {
        // Fetch filter templates
        fetch('/api/strategy-templates')
            .then(r => r.json())
            .then(data => {
                setTemplates(data.templates);
                setTemplatesLoaded(true);
            })
            .catch(err => {
                console.error("Failed to load templates", err);
                setTemplatesLoaded(true);
            });

        // Fetch portfolios
        fetch('/api/portfolios')
            .then(r => r.json())
            .then(data => {
                setPortfolios(data.portfolios || []);
            })
            .catch(err => console.error("Failed to fetch portfolios", err));

        // Fetch strategy data if editing
        if (mode === 'edit') {
            fetch(`/api/strategies/${id}`)
                .then(r => r.json())
                .then(data => {
                    setFormData(prev => ({
                        ...defaults,
                        ...data,
                        conditions: { ...defaults.conditions, ...data.conditions },
                        exit_conditions: { ...defaults.exit_conditions, ...data.exit_conditions },
                        position_sizing: { ...defaults.position_sizing, ...data.position_sizing }
                    }));
                })
                .catch(err => {
                    console.error("Failed to fetch strategy", err);
                    setError("Failed to load strategy details");
                })
                .finally(() => setFetching(false));
        }
    }, [id, mode]);

    const handleTemplateSelect = (templateKey) => {
        setSelectedTemplate(templateKey);

        if (templateKey === 'custom') {
            setFormData({
                ...formData,
                conditions: { ...formData.conditions, filters: [] }
            });
        } else {
            const template = templates[templateKey];
            if (template) {
                setFormData({
                    ...formData,
                    conditions: { ...formData.conditions, filters: [...template.filters] }
                });
            }
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        try {
            // Validation
            if (!formData.name.trim()) {
                throw new Error("Strategy name is required");
            }

            const payload = { ...formData };

            // Force new portfolio creation and manual schedule for new strategies
            if (mode !== 'edit') {
                payload.portfolio_id = 'new';
                payload.new_portfolio_name = formData.name;
            }
            payload.schedule_cron = null; // Always manual for now

            // Hard-code thesis verdict requirement if deliberation is enabled
            if (payload.conditions.require_thesis) {
                payload.conditions.thesis_verdict_required = ['BUY'];
            }

            // Clean up exit conditions
            const cleanNumeric = (val) => {
                if (val === '' || val === null || val === undefined) return null;
                const parsed = parseFloat(val);
                return isNaN(parsed) ? null : parsed;
            };

            payload.exit_conditions.profit_target_pct = cleanNumeric(payload.exit_conditions.profit_target_pct);
            payload.exit_conditions.stop_loss_pct = cleanNumeric(payload.exit_conditions.stop_loss_pct);
            payload.exit_conditions.max_hold_days = parseInt(payload.exit_conditions.max_hold_days) || null;

            payload.veto_score_threshold = cleanNumeric(payload.veto_score_threshold);
            payload.consensus_threshold = cleanNumeric(payload.consensus_threshold);

            // Clean up position sizing
            payload.position_sizing.max_position_pct = cleanNumeric(payload.position_sizing.max_position_pct);
            payload.position_sizing.min_position_value = cleanNumeric(payload.position_sizing.min_position_value);
            payload.position_sizing.fixed_position_pct = cleanNumeric(payload.position_sizing.fixed_position_pct);
            payload.position_sizing.kelly_fraction = cleanNumeric(payload.position_sizing.kelly_fraction);
            payload.position_sizing.max_positions = parseInt(payload.position_sizing.max_positions) || null;

            const url = mode === 'edit' ? `/api/strategies/${id}` : '/api/strategies';
            const method = mode === 'edit' ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to save strategy');
            }

            if (mode === 'create' && result.portfolio_id) {
                navigate(`/portfolios/${result.portfolio_id}`);
            } else {
                navigate(-1);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };


    if (fetching) {
        return <div className="p-8 text-center">Loading strategy details...</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-4 sm:p-8 space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        {mode === 'edit' ? 'Edit Strategy Configuration' : 'Create Autonomous Strategy'}
                    </h1>
                    <p className="text-muted-foreground">
                        {mode === 'edit' ? `` : 'Define the rules for your AI-managed portfolio'}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Button onClick={handleSubmit} disabled={loading} className="px-6">
                        {loading ? 'Saving...' : (
                            <><Save className="mr-2 h-4 w-4" /> Save Strategy</>
                        )}
                    </Button>
                </div>
            </div>

            {
                error && (
                    <div className="p-4 bg-destructive/10 border border-destructive/50 rounded-lg flex items-center gap-3 text-destructive">
                        <AlertCircle size={20} />
                        {error}
                    </div>
                )
            }

            <div className="max-w-3xl mx-auto space-y-8">
                {/* 1. Basics */}
                <Card>
                    <CardHeader>
                        <CardTitle>Strategy Basics</CardTitle>
                        <CardDescription>General information about this investment strategy</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Strategy Name</Label>
                                <Input
                                    id="name"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g., Aggressive Tech Growth"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="cash">Initial Cash ($)</Label>
                                <Input
                                    id="cash"
                                    type="number"
                                    value={formData.initial_cash}
                                    onChange={e => setFormData({ ...formData, initial_cash: parseInt(e.target.value) || 100000 })}
                                    disabled={mode === 'edit'}
                                />
                                {mode === 'edit' && <p className="text-[10px] text-muted-foreground italic">Balance cannot be changed after creation</p>}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="description">Description</Label>
                            <Textarea
                                id="description"
                                value={formData.description}
                                onChange={e => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Describe the goal of this strategy..."
                                rows={3}
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* 2. Universe & Filtering */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle>Universe & Filtering</CardTitle>
                            <CardDescription>Define which stocks the agents should evaluate</CardDescription>
                        </div>
                        <div className="w-64">
                            <Select value={selectedTemplate} onValueChange={handleTemplateSelect}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Apply Template" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="custom">Custom (Build Your Own)</SelectItem>
                                    {Object.entries(templates).map(([key, t]) => (
                                        <SelectItem key={key} value={key}>{t.name || key}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-4">
                            {formData.conditions.filters.map((filter, idx) => (
                                <div key={idx} className="flex flex-wrap sm:flex-nowrap gap-3 items-center bg-muted/30 p-3 rounded-lg border border-border">
                                    <Select
                                        value={filter.field}
                                        onValueChange={val => {
                                            const newFilters = [...formData.conditions.filters];
                                            newFilters[idx] = { ...newFilters[idx], field: val };
                                            setFormData({ ...formData, conditions: { ...formData.conditions, filters: newFilters } });
                                        }}
                                    >
                                        <SelectTrigger className="w-full sm:w-48 bg-background">
                                            <SelectValue placeholder="Select field..." />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="price_vs_52wk_high">Price vs 52-Week High (%)</SelectItem>
                                            <SelectItem value="market_cap">Market Cap ($)</SelectItem>
                                            <SelectItem value="pe_ratio">P/E Ratio</SelectItem>
                                            <SelectItem value="peg_ratio">PEG Ratio</SelectItem>
                                            <SelectItem value="dividend_yield">Dividend Yield (%)</SelectItem>
                                            <SelectItem value="debt_to_equity">Debt/Equity</SelectItem>
                                            <SelectItem value="price">Price ($)</SelectItem>
                                            <SelectItem value="sector">Sector</SelectItem>
                                        </SelectContent>
                                    </Select>

                                    <Select
                                        value={filter.operator}
                                        onValueChange={val => {
                                            const newFilters = [...formData.conditions.filters];
                                            newFilters[idx] = { ...newFilters[idx], operator: val };
                                            setFormData({ ...formData, conditions: { ...formData.conditions, filters: newFilters } });
                                        }}
                                    >
                                        <SelectTrigger className="w-24 bg-background">
                                            <SelectValue placeholder="Op" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {filter.field === 'sector' ? (
                                                <>
                                                    <SelectItem value="==">=</SelectItem>
                                                    <SelectItem value="!=">≠</SelectItem>
                                                </>
                                            ) : (
                                                <>
                                                    <SelectItem value="<">&lt;</SelectItem>
                                                    <SelectItem value=">">&gt;</SelectItem>
                                                    <SelectItem value="<=">≤</SelectItem>
                                                    <SelectItem value=">=">≥</SelectItem>
                                                    <SelectItem value="==">=</SelectItem>
                                                    <SelectItem value="!=">≠</SelectItem>
                                                </>
                                            )}
                                        </SelectContent>
                                    </Select>

                                    <Input
                                        className="flex-1 min-w-[120px] bg-background"
                                        placeholder="Value"
                                        type={filter.field === 'sector' ? 'text' : 'number'}
                                        value={filter.value}
                                        onChange={e => {
                                            const newFilters = [...formData.conditions.filters];
                                            newFilters[idx] = { ...newFilters[idx], value: filter.field === 'sector' ? e.target.value : parseFloat(e.target.value) };
                                            setFormData({ ...formData, conditions: { ...formData.conditions, filters: newFilters } });
                                        }}
                                    />

                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="text-destructive hover:bg-destructive/10"
                                        onClick={() => {
                                            const newFilters = formData.conditions.filters.filter((_, i) => i !== idx);
                                            setFormData({ ...formData, conditions: { ...formData.conditions, filters: newFilters } });
                                        }}
                                    >
                                        <Trash2 size={16} />
                                    </Button>
                                </div>
                            ))}

                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                    setFormData({
                                        ...formData,
                                        conditions: {
                                            ...formData.conditions,
                                            filters: [...formData.conditions.filters, { field: 'pe_ratio', operator: '<', value: 25 }]
                                        }
                                    });
                                }}
                                className="w-full border-dashed border-2 hover:border-primary hover:bg-primary/5 h-12"
                            >
                                <Plus className="mr-2 h-4 w-4" /> Add Screening Filter
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* 3. Scoring Thresholds */}
                <Card>
                    <CardHeader>
                        <CardTitle>Scoring Thresholds</CardTitle>
                        <CardDescription>Minimum scores required for agents to consider a stock</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-8">
                            <div className="space-y-4">
                                <Label className="text-xs uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                                    <Activity className="h-4 w-4" /> Initial Evaluation
                                </Label>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Lynch Min Score</Label>
                                            <Badge variant="secondary">{formData.conditions.scoring_requirements.find(r => r.character === 'lynch')?.min_score || 0}</Badge>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            step="5"
                                            value={formData.conditions.scoring_requirements.find(r => r.character === 'lynch')?.min_score || 0}
                                            onChange={e => {
                                                const newReqs = [...formData.conditions.scoring_requirements];
                                                const idx = newReqs.findIndex(r => r.character === 'lynch');
                                                newReqs[idx] = { ...newReqs[idx], min_score: parseInt(e.target.value) };
                                                setFormData({ ...formData, conditions: { ...formData.conditions, scoring_requirements: newReqs } });
                                            }}
                                            className="w-full accent-emerald-500"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Buffett Min Score</Label>
                                            <Badge variant="secondary">{formData.conditions.scoring_requirements.find(r => r.character === 'buffett')?.min_score || 0}</Badge>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            step="5"
                                            value={formData.conditions.scoring_requirements.find(r => r.character === 'buffett')?.min_score || 0}
                                            onChange={e => {
                                                const newReqs = [...formData.conditions.scoring_requirements];
                                                const idx = newReqs.findIndex(r => r.character === 'buffett');
                                                newReqs[idx] = { ...newReqs[idx], min_score: parseInt(e.target.value) };
                                                setFormData({ ...formData, conditions: { ...formData.conditions, scoring_requirements: newReqs } });
                                            }}
                                            className="w-full accent-amber-500"
                                        />
                                    </div>
                                </div>
                            </div>

                            <Separator />

                            <div className="space-y-4">
                                <Label className="text-xs uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                                    <Plus className="h-4 w-4" /> Position Addition
                                </Label>
                                <p className="text-[10px] text-muted-foreground italic">Higher scores required to buy more of an existing holding.</p>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Lynch Add Score</Label>
                                            <Badge variant="outline">{formData.conditions.addition_scoring_requirements.find(r => r.character === 'lynch')?.min_score || 0}</Badge>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            step="5"
                                            value={formData.conditions.addition_scoring_requirements.find(r => r.character === 'lynch')?.min_score || 0}
                                            onChange={e => {
                                                const newReqs = [...formData.conditions.addition_scoring_requirements];
                                                const idx = newReqs.findIndex(r => r.character === 'lynch');
                                                newReqs[idx] = { ...newReqs[idx], min_score: parseInt(e.target.value) };
                                                setFormData({ ...formData, conditions: { ...formData.conditions, addition_scoring_requirements: newReqs } });
                                            }}
                                            className="w-full accent-emerald-500/70"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Buffett Add Score</Label>
                                            <Badge variant="outline">{formData.conditions.addition_scoring_requirements.find(r => r.character === 'buffett')?.min_score || 0}</Badge>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="100"
                                            step="5"
                                            value={formData.conditions.addition_scoring_requirements.find(r => r.character === 'buffett')?.min_score || 0}
                                            onChange={e => {
                                                const newReqs = [...formData.conditions.addition_scoring_requirements];
                                                const idx = newReqs.findIndex(r => r.character === 'buffett');
                                                newReqs[idx] = { ...newReqs[idx], min_score: parseInt(e.target.value) };
                                                setFormData({ ...formData, conditions: { ...formData.conditions, addition_scoring_requirements: newReqs } });
                                            }}
                                            className="w-full accent-amber-500/70"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* 4. AI & Deliberation */}
                <Card className="border-primary/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5 text-primary" />
                            AI Deliberation
                        </CardTitle>
                        <CardDescription>Manage how agents debate and reach consensus</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center justify-between gap-4">
                            <div className="space-y-1">
                                <Label className="text-base">Enable AI Deliberation</Label>
                                <p className="text-xs text-muted-foreground">Agents Lynch & Buffett will debate before every trade.</p>
                            </div>
                            <Switch
                                checked={formData.conditions.require_thesis}
                                onCheckedChange={checked => setFormData({
                                    ...formData,
                                    conditions: { ...formData.conditions, require_thesis: checked }
                                })}
                            />
                        </div>

                        <Separator />

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                            <div className="space-y-2">
                                <Label>Consensus Mode</Label>
                                <Select
                                    value={formData.consensus_mode}
                                    onValueChange={val => setFormData({ ...formData, consensus_mode: val })}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="both_agree">Strict Agreement (Both must buy)</SelectItem>
                                        <SelectItem value="weighted_confidence">Weighted Confidence</SelectItem>
                                        <SelectItem value="veto_power">Veto Power (Either can block)</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {formData.consensus_mode === 'weighted_confidence' && (
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <Label>Consensus Threshold</Label>
                                        <span className="text-sm font-mono text-primary font-bold">{formData.consensus_threshold}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="50"
                                        max="100"
                                        step="5"
                                        value={formData.consensus_threshold}
                                        onChange={e => setFormData({ ...formData, consensus_threshold: parseInt(e.target.value) })}
                                        className="w-full accent-primary"
                                    />
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* 5. Exit Conditions */}
                <Card>
                    <CardHeader>
                        <CardTitle>Exit Conditions</CardTitle>
                        <CardDescription>Rules for automatically selling a position</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-8">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                            <div className="space-y-2">
                                <Label>Profit Target (%)</Label>
                                <Input
                                    type="number"
                                    placeholder="No Limit"
                                    value={formData.exit_conditions.profit_target_pct || ''}
                                    onChange={e => setFormData({
                                        ...formData,
                                        exit_conditions: { ...formData.exit_conditions, profit_target_pct: e.target.value }
                                    })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Stop Loss (%)</Label>
                                <Input
                                    type="number"
                                    placeholder="No Limit"
                                    value={formData.exit_conditions.stop_loss_pct || ''}
                                    onChange={e => setFormData({
                                        ...formData,
                                        exit_conditions: { ...formData.exit_conditions, stop_loss_pct: e.target.value }
                                    })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Max Hold Days</Label>
                                <Input
                                    type="number"
                                    placeholder="Unlimited"
                                    value={formData.exit_conditions.max_hold_days || ''}
                                    onChange={e => setFormData({
                                        ...formData,
                                        exit_conditions: { ...formData.exit_conditions, max_hold_days: e.target.value }
                                    })}
                                />
                            </div>
                        </div>

                        <Separator />

                        <div className="space-y-4">
                            <h4 className="text-sm font-semibold flex items-center gap-2">
                                <TrendingDown className="h-4 w-4 text-destructive" />
                                Score Degradation Triggers
                            </h4>
                            <p className="text-xs text-muted-foreground">Automatically sell if re-evaluated scores fall below these thresholds.</p>
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <Label>Lynch Score Below</Label>
                                        <Badge variant="outline" className="font-mono">{formData.exit_conditions.score_degradation.lynch_below || 'Off'}</Badge>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        step="5"
                                        value={formData.exit_conditions.score_degradation.lynch_below || 0}
                                        onChange={e => setFormData({
                                            ...formData,
                                            exit_conditions: {
                                                ...formData.exit_conditions,
                                                score_degradation: { ...formData.exit_conditions.score_degradation, lynch_below: parseInt(e.target.value) }
                                            }
                                        })}
                                        className="w-full accent-destructive/70"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <Label>Buffett Score Below</Label>
                                        <Badge variant="outline" className="font-mono">{formData.exit_conditions.score_degradation.buffett_below || 'Off'}</Badge>
                                    </div>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        step="5"
                                        value={formData.exit_conditions.score_degradation.buffett_below || 0}
                                        onChange={e => setFormData({
                                            ...formData,
                                            exit_conditions: {
                                                ...formData.exit_conditions,
                                                score_degradation: { ...formData.exit_conditions.score_degradation, buffett_below: parseInt(e.target.value) }
                                            }
                                        })}
                                        className="w-full accent-destructive/70"
                                    />
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* 6. Position Sizing */}
                <Card>
                    <CardHeader>
                        <CardTitle>Position Sizing</CardTitle>
                        <CardDescription>Determine how much to invest in each trade</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Method</Label>
                                    <Select
                                        value={formData.position_sizing.method}
                                        onValueChange={val => setFormData({
                                            ...formData,
                                            position_sizing: { ...formData.position_sizing, method: val }
                                        })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="equal_weight">Equal Weight (Spread cash evenly)</SelectItem>
                                            <SelectItem value="fixed_pct">Fixed % (Fixed slice per trade)</SelectItem>
                                            <SelectItem value="kelly">Kelly Criterion (Risk optimization)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Max Pos %</Label>
                                        <Input
                                            type="number"
                                            value={formData.position_sizing.max_position_pct}
                                            onChange={e => setFormData({
                                                ...formData,
                                                position_sizing: { ...formData.position_sizing, max_position_pct: e.target.value }
                                            })}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Max Positions</Label>
                                        <Input
                                            type="number"
                                            value={formData.position_sizing.max_positions}
                                            onChange={e => setFormData({
                                                ...formData,
                                                position_sizing: { ...formData.position_sizing, max_positions: e.target.value }
                                            })}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {formData.position_sizing.method === 'fixed_pct' && (
                                    <div className="space-y-2 p-3 bg-primary/5 rounded border border-primary/20">
                                        <Label>Fixed Position %</Label>
                                        <Input
                                            type="number"
                                            placeholder="e.g. 5.0"
                                            value={formData.position_sizing.fixed_position_pct}
                                            onChange={e => setFormData({
                                                ...formData,
                                                position_sizing: { ...formData.position_sizing, fixed_position_pct: e.target.value }
                                            })}
                                        />
                                    </div>
                                )}

                                {formData.position_sizing.method === 'kelly' && (
                                    <div className="space-y-2 p-3 bg-primary/5 rounded border border-primary/20">
                                        <Label>Kelly Fraction (1.0 = Full Kelly)</Label>
                                        <Input
                                            type="number"
                                            placeholder="e.g. 0.5"
                                            step="0.1"
                                            value={formData.position_sizing.kelly_fraction}
                                            onChange={e => setFormData({
                                                ...formData,
                                                position_sizing: { ...formData.position_sizing, kelly_fraction: e.target.value }
                                            })}
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

        </div >
    );
};

export default StrategySettings;
