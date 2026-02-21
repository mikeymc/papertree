// ABOUTME: Public landing page for unauthenticated visitors.
// ABOUTME: Explains papertree.ai's value proposition and drives signups.

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  Search,
  Brain,
  TrendingUp,
  Shield,
  ChevronRight,
  Filter,
  FileText,
  BarChart3,
  Target,
  Zap,
  CheckCircle2,
  ArrowRight,
  BookOpen,
  MessageSquare,
  Calculator,
  Newspaper,
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <img
              src="/icons/bonsai_white.png"
              alt="papertree.ai"
              className="h-8 w-8 object-contain"
            />
            <span className="text-xl font-semibold tracking-tight text-white">papertree.ai</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="text-zinc-300 hover:text-white hover:bg-zinc-800" onClick={() => navigate('/login')}>
              Log In
            </Button>
            <Button className="bg-emerald-600 text-white hover:bg-emerald-700 font-medium" onClick={() => navigate('/login')}>
              Try Free for 14 Days
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 py-24 md:py-32">
        <div className="max-w-3xl">
          <p className="mb-4 text-sm font-medium uppercase tracking-widest text-emerald-600">
            AI-Powered Stock Research
          </p>
          <h1 className="text-4xl font-bold leading-tight tracking-tight md:text-6xl text-white">
            Stop chasing hype.
            <br />
            <span className="text-zinc-500">Start investing systematically.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-zinc-400">
            papertree.ai screens thousands of stocks using the proven criteria of legendary
            investors — delivering deep-dive research theses and managing autonomous paper
            portfolios so you can invest with discipline, not emotion.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Button size="lg" className="text-base px-8 py-6 bg-emerald-600 hover:bg-emerald-700 text-white border-0" onClick={() => navigate('/login')}>
              Try Free for 14 Days
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button variant="outline" size="lg" className="text-base px-8 py-6 border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:text-white" onClick={() => {
              document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
            }}>
              See How It Works
            </Button>
          </div>
          <p className="mt-4 text-sm text-zinc-500">No credit card required</p>
        </div>
      </section>

      {/* Problem / Solution */}
      <section className="border-y border-zinc-800 bg-zinc-900/50">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="grid gap-16 md:grid-cols-2">
            <div>
              <p className="mb-3 text-sm font-medium uppercase tracking-widest text-zinc-500">
                The problem
              </p>
              <h2 className="text-2xl font-bold md:text-3xl text-white">
                Stock screeners give you lists. Not answers.
              </h2>
              <ul className="mt-6 space-y-4 text-zinc-400">
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-600">&#x2715;</span>
                  Generic screeners dump hundreds of tickers with no context
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-600">&#x2715;</span>
                  General-purpose AI tools aren't built for rigorous financial analysis
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-600">&#x2715;</span>
                  Researching each stock yourself takes hours per company
                </li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-500">
                The solution
              </p>
              <h2 className="text-2xl font-bold md:text-3xl text-white">
                A research analyst that screens, verifies, and explains.
              </h2>
              <ul className="mt-6 space-y-4 text-zinc-400">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-emerald-500" />
                  AI screens stocks against proven, time-tested investment criteria
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-emerald-500" />
                  Every number is pulled from real financial data — never hallucinated
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-emerald-500" />
                  You get a written thesis, not just a ticker symbol
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-500">
            How it works
          </p>
          <h2 className="text-2xl font-bold md:text-3xl text-white">
            Six steps. Thousands of stocks. One disciplined portfolio.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-zinc-500">
            papertree.ai runs every stock through a multi-step filtering pipeline
            inspired by how the best investors actually evaluate companies.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              icon: Search,
              step: '1',
              title: 'Discovery',
              desc: 'Scan the full market to define your investable universe based on foundational criteria like market cap or sector.',
            },
            {
              icon: Filter,
              step: '2',
              title: 'Quantitative Scoring',
              desc: 'Every candidate is scored across dozens of financial metrics using algorithms modeled after Lynch and Buffett\'s published strategies.',
            },
            {
              icon: Shield,
              step: '3',
              title: 'Risk Filtering',
              desc: 'Eliminate stocks with red flags — excessive debt, declining earnings, insider selling, or governance concerns.',
            },
            {
              icon: Brain,
              step: '4',
              title: 'AI Analysis',
              desc: 'An AI analyst reads SEC filings, earnings transcripts, and news to write customized bull and bear case theses.',
            },
            {
              icon: Target,
              step: '5',
              title: 'Deliberation',
              desc: 'The AI acts as an investment committee, deliberating over the theses to select the absolute highest-conviction targets.',
            },
            {
              icon: TrendingUp,
              step: '6',
              title: 'Autonomous Management',
              desc: 'The system automatically executes trades, tracks alpha vs the S&P 500, and continuously monitors your portfolio over time.',
            },
          ].map(({ icon: Icon, step, title, desc }) => (
            <div
              key={step}
              className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 transition-shadow hover:shadow-lg hover:shadow-emerald-900/10 hover:border-zinc-700"
            >
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-950 border border-emerald-900 text-emerald-500">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-medium uppercase tracking-widest text-zinc-500">
                  Step {step}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-white">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Research Desk */}
      <section className="border-y border-zinc-800 bg-zinc-900/50">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center">
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-500">
              Beyond the portfolio
            </p>
            <h2 className="text-2xl font-bold md:text-3xl text-white">
              A full research desk at your fingertips.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-zinc-500">
              Dig into any company, any time. papertree.ai gives you the same tools
              the autonomous portfolio uses — available whenever you need them.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: MessageSquare,
                title: 'AI Chat',
                desc: 'Ask questions about any stock. 30+ specialized tools for financials, filings, insider activity, and more.',
              },
              {
                icon: Calculator,
                title: 'DCF Analysis',
                desc: 'Run AI-assisted discounted cash flow models to estimate intrinsic value and margin of safety.',
              },
              {
                icon: Newspaper,
                title: 'Earnings Intelligence',
                desc: 'Read synthesized earnings calls and reports — key takeaways, management tone, and guidance changes.',
              },
              {
                icon: Search,
                title: 'Stock Screener',
                desc: 'Filter the full market by fundamentals, growth metrics, debt levels, and investor-style scoring.',
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div
                key={title}
                className="rounded-xl border border-zinc-800 bg-zinc-900 p-5"
              >
                <Icon className="mb-3 h-5 w-5 text-emerald-500" />
                <h3 className="font-semibold text-white">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-zinc-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Legendary Investors */}
      <section className="border-y border-zinc-800 bg-black text-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center">
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-500">
              Built on proven strategies
            </p>
            <h2 className="text-2xl font-bold md:text-3xl">
              Invest like the legends. Automatically.
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
              Choose from strategy templates based on the published methodologies
              of the greatest investors in history.
            </p>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-2">
            <div className="rounded-xl border border-zinc-700 bg-zinc-800 p-8">
              <div className="mb-4 flex items-center gap-3">
                <BookOpen className="h-6 w-6 text-emerald-400" />
                <h3 className="text-xl font-semibold">Peter Lynch</h3>
              </div>
              <p className="text-sm text-zinc-400">
                "One Up on Wall Street" — Find fast growers, stalwarts, and
                turnarounds using Lynch's PEG ratio, earnings growth, and
                debt-to-equity criteria. The system categorizes every stock into
                Lynch's six company types automatically.
              </p>
              <ul className="mt-6 space-y-2 text-sm text-zinc-300">
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  Fast Grower, Stalwart, and Slow Grower detection
                </li>
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  PEG ratio scoring with earnings growth validation
                </li>
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  Institutional ownership sweet spot targeting
                </li>
              </ul>
            </div>
            <div className="rounded-xl border border-zinc-700 bg-zinc-800 p-8">
              <div className="mb-4 flex items-center gap-3">
                <BarChart3 className="h-6 w-6 text-emerald-400" />
                <h3 className="text-xl font-semibold">Warren Buffett</h3>
              </div>
              <p className="text-sm text-zinc-400">
                "The Intelligent Investor" philosophy — Identify companies with
                durable competitive advantages, consistent earnings, conservative
                debt, and management that allocates capital wisely.
              </p>
              <ul className="mt-6 space-y-2 text-sm text-zinc-300">
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  Economic moat and competitive advantage analysis
                </li>
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  Return on equity and capital efficiency scoring
                </li>
                <li className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-emerald-400" />
                  Margin of safety valuation checks
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section replacing Content */}
      <section className="mx-auto max-w-6xl px-6 py-24">
        <div className="text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-500">
            Pricing
          </p>
          <h2 className="text-2xl font-bold md:text-3xl text-white">
            Simple, transparent pricing.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
            Start finding better investments today. One successful trade pays for years of access.
          </p>
        </div>

        <div className="mt-16 mx-auto max-w-sm">
          <div className="rounded-2xl border border-emerald-800 bg-zinc-900/80 p-8 shadow-xl shadow-emerald-900/20 backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 bg-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg uppercase tracking-wider">
              Most Popular
            </div>
            <h3 className="text-2xl font-semibold text-white">Pro Analyst</h3>
            <div className="mt-4 flex items-baseline text-white">
              <span className="text-5xl font-bold tracking-tight">$39</span>
              <span className="ml-1 text-xl text-zinc-400">/month</span>
            </div>
            <p className="mt-4 text-sm text-zinc-400">
              Full access to the AI analyst, portfolio tracking, and proven templates.
            </p>
            <ul className="mt-8 space-y-4">
              {[
                'Unlimited AI generated theses',
                'Lynch & Buffett strategy templates',
                'Autonomous portfolio tracking',
                'Advanced real-time risk filtering',
                'SEC filing & earnings analysis'
              ].map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-sm text-zinc-300">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                  {feature}
                </li>
              ))}
            </ul>
            <Button className="mt-8 w-full bg-emerald-600 hover:bg-emerald-700 text-white py-6" onClick={() => navigate('/login')}>
              Start 14-Day Free Trial
            </Button>
            <p className="mt-3 text-center text-xs text-zinc-500">Cancel anytime. No questions asked.</p>
          </div>
        </div>
      </section>

      {/* Founder Story */}
      <section className="border-y border-zinc-800 bg-zinc-900/30">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="mx-auto max-w-2xl">
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-zinc-500">
              Built by an investor, for investors
            </p>
            <h2 className="text-2xl font-bold md:text-3xl text-white">
              Retail investing doesn't have to be a rollercoaster.
            </h2>
            <div className="mt-6 space-y-4 text-zinc-400 leading-relaxed">
              <p>
                Too much of retail investing is driven by hype — chasing momentum on
                social media, buying into stories that "feel" right, panic-selling when
                sentiment shifts. It's exhausting, and the results speak for themselves.
              </p>
              <p>
                But it doesn't have to work that way. Investors like Lynch and Buffett
                published exactly how they evaluate companies. The principles are proven
                and freely available. The hard part is applying them rigorously across
                thousands of stocks — that's where discipline breaks down.
              </p>
              <p className="text-zinc-300 font-medium">
                papertree.ai does the rigorous work so you can make decisions based on
                analysis, not emotion.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <h2 className="text-3xl font-bold md:text-4xl text-white">
          Stop guessing. Start investing with conviction.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-zinc-400">
          Start your free 14-day trial. No credit card required.
        </p>
        <div className="mt-8">
          <Button size="lg" className="text-base px-8 py-6 bg-emerald-600 hover:bg-emerald-700 text-white border-0" onClick={() => navigate('/login')}>
            Get Started Free
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 bg-zinc-950">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6 text-sm text-zinc-500">
          <div className="flex items-center gap-2">
            <img
              src="/icons/bonsai_white.png"
              alt="papertree.ai"
              className="h-5 w-5 object-contain opacity-40"
            />
            <span>&copy; {new Date().getFullYear()} papertree.ai</span>
          </div>
          <div className="flex items-center gap-6">
            <a href="mailto:info@papertree.ai" className="hover:text-zinc-300 transition-colors">Contact</a>
            <a href="#" className="hover:text-zinc-300 transition-colors">Terms</a>
            <a href="#" className="hover:text-zinc-300 transition-colors">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
