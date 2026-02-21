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
} from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white text-zinc-900">
      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-zinc-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <img
              src="/icons/bonsai_black.png"
              alt="papertree.ai"
              className="h-8 w-8 object-contain"
            />
            <span className="text-xl font-semibold tracking-tight">papertree.ai</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate('/login')}>
              Log In
            </Button>
            <Button onClick={() => navigate('/login')}>
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
          <h1 className="text-4xl font-bold leading-tight tracking-tight md:text-6xl">
            Stop scrolling through tickers.
            <br />
            <span className="text-zinc-400">Start reading investment theses.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-zinc-600">
            papertree.ai screens thousands of stocks using the same criteria as legendary
            investors like Peter Lynch and Warren Buffett — then writes you a research
            briefing explaining exactly why each stock made the cut.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Button size="lg" className="text-base px-8 py-6" onClick={() => navigate('/login')}>
              Try Free for 14 Days
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button variant="outline" size="lg" className="text-base px-8 py-6" onClick={() => {
              document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
            }}>
              See How It Works
            </Button>
          </div>
          <p className="mt-4 text-sm text-zinc-400">No credit card required</p>
        </div>
      </section>

      {/* Problem / Solution */}
      <section className="border-y border-zinc-200 bg-zinc-50">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="grid gap-16 md:grid-cols-2">
            <div>
              <p className="mb-3 text-sm font-medium uppercase tracking-widest text-zinc-400">
                The problem
              </p>
              <h2 className="text-2xl font-bold md:text-3xl">
                Stock screeners give you lists. Not answers.
              </h2>
              <ul className="mt-6 space-y-4 text-zinc-600">
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-300">&#x2715;</span>
                  Generic screeners dump hundreds of tickers with no context
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-300">&#x2715;</span>
                  ChatGPT hallucinates financial data — P/E ratios, revenue, debt figures
                </li>
                <li className="flex items-start gap-3">
                  <span className="mt-1 text-zinc-300">&#x2715;</span>
                  Researching each stock yourself takes hours per company
                </li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-600">
                The solution
              </p>
              <h2 className="text-2xl font-bold md:text-3xl">
                A research analyst that screens, verifies, and explains.
              </h2>
              <ul className="mt-6 space-y-4 text-zinc-600">
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
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-600">
            How it works
          </p>
          <h2 className="text-2xl font-bold md:text-3xl">
            Six steps. Thousands of stocks. Your shortlist.
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
              desc: 'Scan the full market for companies matching investor-defined criteria — growth rates, P/E ratios, debt levels, and more.',
            },
            {
              icon: Filter,
              step: '2',
              title: 'Quantitative Scoring',
              desc: 'Each stock is scored across dozens of financial metrics using algorithms modeled after Lynch and Buffett\'s published strategies.',
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
              desc: 'An AI analyst reads SEC filings, earnings transcripts, and news to assess qualitative factors no screener can capture.',
            },
            {
              icon: FileText,
              step: '5',
              title: 'Thesis Generation',
              desc: 'For every stock that passes, you get a written investment thesis explaining the bull case, risks, and key metrics.',
            },
            {
              icon: Target,
              step: '6',
              title: 'Your Shortlist',
              desc: 'A curated list of high-conviction ideas with the research already done — ready for your final decision.',
            },
          ].map(({ icon: Icon, step, title, desc }) => (
            <div
              key={step}
              className="rounded-xl border border-zinc-200 bg-white p-6 transition-shadow hover:shadow-md"
            >
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 text-white">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="text-xs font-medium uppercase tracking-widest text-zinc-400">
                  Step {step}
                </span>
              </div>
              <h3 className="text-lg font-semibold">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Legendary Investors */}
      <section className="border-y border-zinc-200 bg-zinc-900 text-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="text-center">
            <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-400">
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

      {/* Differentiators */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-emerald-600">
            Why papertree.ai
          </p>
          <h2 className="text-2xl font-bold md:text-3xl">
            Not another screener. A research process.
          </h2>
        </div>
        <div className="mt-12 grid gap-8 md:grid-cols-3">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
              <Shield className="h-6 w-6 text-emerald-600" />
            </div>
            <h3 className="font-semibold">Real Data, Not Hallucinations</h3>
            <p className="mt-2 text-sm text-zinc-500">
              Every metric comes from verified financial data sources.
              AI generates the thesis — but the numbers are never made up.
            </p>
          </div>
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
              <TrendingUp className="h-6 w-6 text-emerald-600" />
            </div>
            <h3 className="font-semibold">Strategies, Not Just Screens</h3>
            <p className="mt-2 text-sm text-zinc-500">
              Set up an investment strategy once and let it run continuously.
              Get notified when new stocks match your criteria.
            </p>
          </div>
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
              <FileText className="h-6 w-6 text-emerald-600" />
            </div>
            <h3 className="font-semibold">Theses, Not Tickers</h3>
            <p className="mt-2 text-sm text-zinc-500">
              Every result includes a written investment thesis — the bull case,
              key risks, and critical metrics. No more blind ticker lists.
            </p>
          </div>
        </div>
      </section>

      {/* Social Proof Placeholder */}
      <section className="border-y border-zinc-200 bg-zinc-50">
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-widest text-zinc-400">
            Early access
          </p>
          <h2 className="text-2xl font-bold md:text-3xl">
            Built by an investor, for investors.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-zinc-500">
            papertree.ai was born from frustration with tools that give you data
            but not insight. We're a small team obsessed with making stock research
            faster and more rigorous — not replacing your judgment, but sharpening it.
          </p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <h2 className="text-3xl font-bold md:text-4xl">
          Your next investment idea is waiting.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-zinc-500">
          Start your free 14-day trial. No credit card required.
        </p>
        <div className="mt-8">
          <Button size="lg" className="text-base px-8 py-6" onClick={() => navigate('/login')}>
            Get Started Free
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6 text-sm text-zinc-400">
          <div className="flex items-center gap-2">
            <img
              src="/icons/bonsai_black.png"
              alt="papertree.ai"
              className="h-5 w-5 object-contain opacity-40"
            />
            <span>&copy; {new Date().getFullYear()} papertree.ai</span>
          </div>
          <div className="flex items-center gap-6">
            <a href="mailto:info@papertree.ai" className="hover:text-zinc-600">Contact</a>
            <a href="#" className="hover:text-zinc-600">Terms</a>
            <a href="#" className="hover:text-zinc-600">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
