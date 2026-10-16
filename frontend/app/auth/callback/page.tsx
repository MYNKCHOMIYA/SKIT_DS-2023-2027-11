"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Securing your session with Google...");

  useEffect(() => {
    const token = searchParams.get("token");
    const error = searchParams.get("error");

    if (error) {
      const decodedError = decodeURIComponent(error);
      setStatus("error");
      setMessage(decodedError || "Google authentication failed.");
      toast.error(decodedError || "Google authentication failed.");
      const timer = setTimeout(() => {
        router.replace("/login");
      }, 2500);
      return () => clearTimeout(timer);
    }

    if (token) {
      try {
        localStorage.setItem("token", token);
        setStatus("success");
        setMessage("Authentication successful! Redirecting to dashboard...");
        toast.success("Welcome back! Signed in with Google.");
        const timer = setTimeout(() => {
          router.replace("/");
        }, 800);
        return () => clearTimeout(timer);
      } catch (e) {
        setStatus("error");
        setMessage("Failed to save session token locally.");
        toast.error("Session storage failed.");
        const timer = setTimeout(() => {
          router.replace("/login");
        }, 2500);
        return () => clearTimeout(timer);
      }
    }

    // Neither token nor error provided
    setStatus("error");
    setMessage("Invalid authentication callback. No token found.");
    const timer = setTimeout(() => {
      router.replace("/login");
    }, 2000);
    return () => clearTimeout(timer);
  }, [searchParams, router]);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4">
      {/* Background radial gradient */}
      <div className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sky-100 via-background to-background dark:from-slate-900" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="z-10 w-full max-w-md"
      >
        <Card className="border-border/60 bg-background/80 backdrop-blur-xl shadow-2xl rounded-3xl p-6 text-center">
          <CardContent className="pt-6 space-y-6 flex flex-col items-center">
            {/* Google Icon with pulsing glow */}
            <div className="relative flex items-center justify-center">
              <div className="absolute -inset-2 rounded-full bg-primary/20 blur-xl animate-pulse" />
              <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-card border border-border/80 shadow-md">
                <svg className="h-8 w-8" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
              </div>
            </div>

            <div className="space-y-2">
              <h2 className="text-xl font-bold tracking-tight">
                {status === "loading" && "Authenticating with Google"}
                {status === "success" && "Session Authenticated"}
                {status === "error" && "Authentication Notice"}
              </h2>
              <p className="text-sm text-muted-foreground text-balance max-w-sm">
                {message}
              </p>
            </div>

            <div className="flex items-center justify-center pt-2">
              {status === "loading" && (
                <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin text-primary" />
                  <span>Verifying credentials with server...</span>
                </div>
              )}
              {status === "success" && (
                <div className="flex items-center gap-2 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Redirecting to your portfolio...</span>
                </div>
              )}
              {status === "error" && (
                <div className="flex items-center gap-2 text-xs font-medium text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span>Returning to sign-in page...</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

export default function GoogleAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
