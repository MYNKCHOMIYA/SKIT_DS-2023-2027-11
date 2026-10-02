import { Inter } from "next/font/google";
import "./globals.css";

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
    <html lang="en">
      <body className={inter.className}>
        {/* Sprint 2: ThemeProvider and RoleProvider will wrap the children here */}
        <main className="min-h-screen bg-background font-sans antialiased">
          {children}
        </main>
      </body>
    </html>
  );
}
