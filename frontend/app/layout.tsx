import { Inter, Geist } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";
import { Providers } from "@/components/providers";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Generalized Faculty Portfolio System",
  description: "Centralized dashboard for faculty profiles and achievements",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className={inter.className}>
        <Providers attribute="class" defaultTheme="system" enableSystem>
          <main className="min-h-screen bg-background font-sans antialiased">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
