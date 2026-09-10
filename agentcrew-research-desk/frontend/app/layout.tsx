import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentCrew Research Desk",
  description: "A multi-agent research assistant running on local models.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-serif antialiased">{children}</body>
    </html>
  );
}
