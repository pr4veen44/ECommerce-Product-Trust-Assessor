"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Shield, Plus, Trash2, ArrowLeft, Loader2, Info } from "lucide-react";
import { analyzeProduct } from "@/lib/api";
import type { ProductAnalysisRequest, ReviewInput } from "@/types";

const CATEGORIES = [
  "Electronics", "Clothing & Apparel", "Home & Kitchen",
  "Books", "Sports & Outdoors", "Beauty & Personal Care",
  "Toys & Games", "Automotive", "Health & Wellness",
  "Food & Grocery", "Tools & Hardware", "Other",
];

const DEMO_DATA: ProductAnalysisRequest = {
  title: "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones",
  description: `Industry-leading noise canceling with two chips and eight microphones.
The new Integrated Processor V1 with two chips and eight microphones enables more precise noise cancellation than ever before.

Crystal clear hands-free calling with 4 beamforming microphones and advanced noise reduction algorithm.
Auto Noise Canceling Optimizer automatically optimizes noise cancellation based on wearing conditions and environment.

Up to 30-hour battery life with quick charging (3 min charge = 3 hours playback).
Exceptional sound quality with the new 30mm driver unit and LDAC support.

Dimensions: 7.28 x 3.67 x 9.94 inches | Weight: 8.8 oz
Compatible with Alexa, Google Assistant, and Siri
Includes: Headphones, Carrying case, USB-C charging cable, audio cable`,
  category: "Electronics",
  price: 279.99,
  rating: 4.4,
  reviews: [
    { text: "These are absolutely incredible headphones. The noise cancellation is leagues better than my old QC35s. Perfect for office work and flights. Battery lasts all day.", rating: 5, verified: true, helpful_votes: 234 },
    { text: "Sound quality is superb and ANC is best in class. Comfortable for long sessions. Only complaint is the touch controls can be finicky.", rating: 4, verified: true, helpful_votes: 87 },
    { text: "Great headphones but a bit pricey. The case feels premium and they fold flat nicely. LDAC quality is noticeable on Tidal.", rating: 4, verified: true, helpful_votes: 52 },
    { text: "Returned after 2 weeks. The headband cracked under normal use. Build quality disappointing for the price.", rating: 2, verified: true, helpful_votes: 44 },
    { text: "Exceptional noise cancellation. I can't hear my toddler anymore which is both useful and mildly concerning.", rating: 5, verified: true, helpful_votes: 601 },
  ],
  seller: {
    avg_rating: 4.7,
    total_orders: 12500,
    cancellation_rate: 0.02,
    avg_delivery_days: 3.2,
  },
};

export default function AnalyzerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<ProductAnalysisRequest>({
    title: "",
    description: "",
    category: "",
    price: undefined,
    rating: undefined,
    reviews: [{ text: "", rating: undefined, verified: false }],
    seller: undefined,
  });

  const [showSeller, setShowSeller] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const payload: ProductAnalysisRequest = {
        ...form,
        reviews: form.reviews.filter((r) => r.text.trim().length > 0),
      };

      const result = await analyzeProduct(payload);

      // Store result in sessionStorage for results page
      sessionStorage.setItem("trust_result", JSON.stringify(result));
      sessionStorage.setItem("trust_request", JSON.stringify(payload));
      router.push("/results");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Analysis failed. Is the backend running?";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const loadDemo = () => setForm(DEMO_DATA);

  const addReview = () =>
    setForm((f) => ({
      ...f,
      reviews: [...f.reviews, { text: "", rating: undefined, verified: false }],
    }));

  const removeReview = (i: number) =>
    setForm((f) => ({ ...f, reviews: f.reviews.filter((_, idx) => idx !== i) }));

  const updateReview = (i: number, patch: Partial<ReviewInput>) =>
    setForm((f) => ({
      ...f,
      reviews: f.reviews.map((r, idx) => (idx === i ? { ...r, ...patch } : r)),
    }));

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="border-b border-[#3f3f46] px-6 py-4 flex items-center gap-4 sticky top-0 bg-[#09090b]/80 backdrop-blur-md z-50">
        <Link href="/" className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-100 transition-colors">
          <ArrowLeft size={16} />
          <span className="text-sm">Back</span>
        </Link>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-indigo-600 flex items-center justify-center">
            <Shield size={14} className="text-white" />
          </div>
          <span className="font-semibold text-white text-sm">Product Analyzer</span>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-6 py-12">
        <div className="mb-8 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-white">Analyze Product Trust</h1>
            <p className="text-zinc-400 text-sm mt-1">
              Fill in the product details below to generate a Trust Score.
            </p>
          </div>
          <button
            type="button"
            onClick={loadDemo}
            className="btn-ghost text-sm border border-[#3f3f46] px-4 py-2 rounded-lg"
          >
            Load demo
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Product basics */}
          <div className="card p-6 space-y-5">
            <h2 className="font-semibold text-white text-sm">Product Information</h2>

            <div>
              <label className="label block mb-2">Product Title *</label>
              <input
                required
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="e.g. Sony WH-1000XM5 Wireless Headphones"
                className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="label block mb-2">Description *</label>
              <textarea
                required
                rows={5}
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Paste the full product description..."
                className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              <div>
                <label className="label block mb-2">Category</label>
                <select
                  value={form.category ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                  className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-3 py-2.5 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select…</option>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="label block mb-2">Price ($)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.price ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, price: parseFloat(e.target.value) || undefined }))}
                  placeholder="0.00"
                  className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="label block mb-2">Avg Rating</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  step="0.1"
                  value={form.rating ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, rating: parseFloat(e.target.value) || undefined }))}
                  placeholder="1–5"
                  className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Reviews */}
          <div className="card p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-white text-sm">
                Customer Reviews
                <span className="ml-2 text-zinc-500 font-normal text-xs">({form.reviews.length})</span>
              </h2>
              <button type="button" onClick={addReview} className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                <Plus size={14} />
                Add review
              </button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {form.reviews.map((review, i) => (
                <div key={i} className="bg-[#27272a] rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs text-zinc-500">Review #{i + 1}</span>
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-1.5 text-xs text-zinc-400 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={review.verified ?? false}
                          onChange={(e) => updateReview(i, { verified: e.target.checked })}
                          className="rounded border-zinc-600 bg-zinc-800 text-indigo-500"
                        />
                        Verified
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="5"
                        step="1"
                        value={review.rating ?? ""}
                        onChange={(e) => updateReview(i, { rating: parseFloat(e.target.value) || undefined })}
                        placeholder="★"
                        className="w-14 bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-100 text-center focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      />
                      {form.reviews.length > 1 && (
                        <button type="button" onClick={() => removeReview(i)} className="text-zinc-600 hover:text-red-400 transition-colors">
                          <Trash2 size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                  <textarea
                    rows={2}
                    value={review.text}
                    onChange={(e) => updateReview(i, { text: e.target.value })}
                    placeholder="Paste review text…"
                    className="w-full bg-zinc-800/50 border border-zinc-700 rounded-md px-3 py-2 text-xs text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Seller (optional) */}
          <div className="card overflow-hidden">
            <button
              type="button"
              onClick={() => setShowSeller((v) => !v)}
              className="w-full flex items-center justify-between px-6 py-4 text-sm font-semibold text-white hover:bg-zinc-800/30 transition-colors"
            >
              <span className="flex items-center gap-2">
                Seller Information
                <span className="text-zinc-500 font-normal text-xs">(optional)</span>
              </span>
              <span className="text-zinc-500">{showSeller ? "−" : "+"}</span>
            </button>

            {showSeller && (
              <div className="px-6 pb-6 grid grid-cols-2 gap-4 border-t border-[#3f3f46]">
                {[
                  { key: "avg_rating", label: "Avg Rating", placeholder: "4.5", step: "0.1", min: "0", max: "5" },
                  { key: "total_orders", label: "Total Orders", placeholder: "1000", step: "1", min: "0" },
                  { key: "cancellation_rate", label: "Cancellation Rate", placeholder: "0.02", step: "0.01", min: "0", max: "1" },
                  { key: "avg_delivery_days", label: "Avg Delivery Days", placeholder: "5", step: "0.5", min: "0" },
                ].map(({ key, label, placeholder, step, min, max }) => (
                  <div key={key} className="mt-4">
                    <label className="label block mb-2">{label}</label>
                    <input
                      type="number"
                      step={step}
                      min={min}
                      max={max}
                      placeholder={placeholder}
                      value={(form.seller as Record<string, unknown>)?.[key] as string ?? ""}
                      onChange={(e) =>
                        setForm((f) => ({
                          ...f,
                          seller: { ...f.seller, [key]: parseFloat(e.target.value) || undefined },
                        }))
                      }
                      className="w-full bg-[#27272a] border border-[#3f3f46] rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-start gap-3 bg-red-950/40 border border-red-800/50 rounded-lg px-4 py-3 text-sm text-red-300">
              <Info size={16} className="mt-0.5 shrink-0" />
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 text-base py-3.5">
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Analyzing…
              </>
            ) : (
              <>
                <Shield size={18} />
                Generate Trust Score
              </>
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
