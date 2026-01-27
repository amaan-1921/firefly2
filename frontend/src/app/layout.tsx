// src/app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';
import Providers from '@/components/layout/Providers';

export const metadata: Metadata = {
  title: 'ADAPT - Supply Chain Risk',
  description:
    'ADAPT is a safety-first supply chain risk management platform for proactive risk mitigation.'
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
