import Link from "next/link";
import { Shield, Zap, BarChart3, Eye, ArrowRight, CheckCircle } from "lucide-react";

const FEATURES = [
  {
    icon: Shield,
    title: "5-Layer Trust Analysis",
    desc: "Review authenticity, sentiment quality, listing completeness, seller reliability, and return risk — all in one score.",
  },
  {
    icon: Eye,
    title: "Fully Explainable AI",
    desc: "SHAP-powered explanations show exactly which factors raised or lowered each product's trust score.",
  },
  {
    icon: Zap,
    title: "Real-time Scoring",
    desc: "DistilBERT + XGBoost ensemble delivers sub-second predictions even for large review sets.",
  },
  {
    icon: BarChart3,
    title: "Visual Dashboard",
    desc: "Radar charts, score gauges, and breakdown cards make complex ML outputs instantly readable.",
  },
];

const STATS = [
  { value: "5", label: "ML Modules" },
  { value: "89%", label: "Authenticity Accuracy" },
  { value: "< 1s", label: "Inference Time" },
  { value: "100", label: "Max Trust Score" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Nav */}
      <nav className="border-b border-[#3f3f46] px-6 py-4 flex items-center justify-between sticky top-0 bg-[#09090b]/80 backdrop-blur-md z-50">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Shield size={16} className="text-white" />
          </div>
          <span className="font-semibold text-white tracking-tight">TrustScore</span>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="https://github.com/your-username/ECommerce-Product-Trust-Assessor"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-sm hidden sm:block"
          >
            GitHub
          </a>
          <Link href="/analyzer" className="btn-primary text-sm py-2">
            Try it free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-24 text-center max-w-5xl mx-auto w-full">
        <div className="inline-flex items-center gap-2 bg-indigo-950/50 border border-indigo-800/50 rounded-full px-4 py-1.5 text-indigo-300 text-sm mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Explainable AI · 5 ML Modules · SHAP-Powered
        </div>

        <h1 className="text-5xl sm:text-7xl font-bold text-white leading-none tracking-tight mb-6">
          Can you trust
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">
            this product?
          </span>
        </h1>

        <p className="text-lg text-zinc-400 max-w-2xl mb-10 leading-relaxed">
          Paste a product title, description, and reviews. Our AI analyzes review
          authenticity, seller reliability, sentiment quality, and more — then
          delivers a single, explainable Trust Score.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4">
          <Link href="/analyzer" className="btn-primary flex items-center gap-2 text-base">
            Analyze a product
            <ArrowRight size={16} />
          </Link>
          <a
            href="https://github.com/your-username/ECommerce-Product-Trust-Assessor"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-base"
          >
            View on GitHub →
          </a>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-[#3f3f46] py-12 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8 text-center">
          {STATS.map(({ value, label }) => (
            <div key={label}>
              <div className="text-3xl font-bold text-white">{value}</div>
              <div className="text-sm text-zinc-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 max-w-5xl mx-auto w-full">
        <p className="label text-center mb-4">How it works</p>
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Production-grade ML pipeline
        </h2>
        <div className="grid sm:grid-cols-2 gap-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6 flex gap-4">
              <div className="w-10 h-10 rounded-lg bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center shrink-0">
                <Icon size={18} className="text-indigo-400" />
              </div>
              <div>
                <h3 className="font-semibold text-white mb-1">{title}</h3>
                <p className="text-sm text-zinc-400 leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ML Architecture */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full">
        <p className="label text-center mb-4">Architecture</p>
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          5 specialized scoring engines
        </h2>
        <div className="grid sm:grid-cols-5 gap-3">
          {[
            { n: "01", name: "Review\nAuthenticity", model: "XGBoost", weight: "30%" },
            { n: "02", name: "Sentiment\nQuality", model: "DistilBERT", weight: "25%" },
            { n: "03", name: "Listing\nQuality", model: "NLP Rules", weight: "15%" },
            { n: "04", name: "Seller\nReliability", model: "LightGBM", weight: "20%" },
            { n: "05", name: "Return\nRisk", model: "Ensemble", weight: "10%" },
          ].map(({ n, name, model, weight }) => (
            <div key={n} className="card p-4 text-center flex flex-col gap-2">
              <span className="font-mono text-xs text-indigo-400">{n}</span>
              <span className="text-sm font-medium text-white whitespace-pre-line leading-tight">{name}</span>
              <span className="text-xs text-zinc-500">{model}</span>
              <span className="text-xs font-mono text-indigo-300 bg-indigo-950/40 rounded-md px-2 py-0.5">{weight}</span>
            </div>
          ))}
        </div>
        <div className="mt-4 card p-4 text-center">
          <span className="text-zinc-400 text-sm">↓ Weighted combination ↓</span>
          <div className="text-2xl font-bold text-white mt-1">
            <span className="text-indigo-400">Trust Score</span> · 0–100
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 text-center">
        <div className="max-w-2xl mx-auto card p-10">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to analyze?
          </h2>
          <p className="text-zinc-400 mb-8">
            Paste any product details and get a full trust breakdown in seconds.
          </p>
          <Link href="/analyzer" className="btn-primary inline-flex items-center gap-2">
            Open Product Analyzer
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#3f3f46] px-6 py-8 text-center text-zinc-600 text-sm">
        Built with Next.js 15 · FastAPI · DistilBERT · XGBoost · SHAP
      </footer>
    </div>
  );
}
