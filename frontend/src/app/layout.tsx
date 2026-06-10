import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TrustScore — E-Commerce Product Trust Assessor",
  description:
    "AI-powered explainable trust scoring for e-commerce products. Know before you buy.",
  keywords: ["ecommerce", "trust score", "AI", "product analysis", "fake reviews"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="bg-[#09090b] text-zinc-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
