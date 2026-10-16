"use client";

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useMutation } from "@tanstack/react-query"
import { Sparkles, Loader2, ArrowRight, GraduationCap } from "lucide-react"
import { toast } from "sonner"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import api from "@/lib/api"

const DISALLOWED_PREFIXES = [
  "fake",
  "dummy",
  "temp",
  "disposable",
  "trash",
  "junk",
  "spam",
  "asdf",
  "qwerty",
  "12345",
  "123456",
  "noname",
  "fakeemail",
  "fakeid",
  "invalid",
];

// Role is NOT part of the registration form — always defaults to "faculty" on backend
const registerSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Invalid email address format")
    .refine((val) => val.trim().toLowerCase().endsWith("@skit.ac.in"), {
      message: "Only official @skit.ac.in institutional emails are permitted.",
    })
    .refine(
      (val) => {
        const parts = val.trim().toLowerCase().split("@");
        if (parts.length !== 2 || parts[1] !== "skit.ac.in") return false;
        const local = parts[0];
        if (local.length < 3 || local.length > 64) return false;
        if (!/^[a-zA-Z0-9]+([._-][a-zA-Z0-9]+)*$/.test(local)) return false;
        const normalized = local.replace(/[._-]/g, "");
        if (
          DISALLOWED_PREFIXES.some(
            (p) =>
              normalized === p ||
              normalized.startsWith(p + "1") ||
              normalized.startsWith(p + "email")
          )
        ) {
          return false;
        }
        if (/^\d+$/.test(normalized) && new Set(normalized).size === 1) {
          return false;
        }
        return true;
      },
      {
        message:
          "Please enter your real SKIT institutional ID, not a placeholder or fake email.",
      }
    ),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter()
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)

  const handleGoogleSignUp = () => {
    setIsGoogleLoading(true)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
    window.location.href = `${backendUrl}/api/v1/auth/google/login`
  }

  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", password: "" },
  })

  const registerMutation = useMutation({
    mutationFn: async (values: RegisterFormValues) => {
      // Never send role — backend always assigns "faculty"
      const response = await api.post("/api/v1/auth/register", values)
      return response.data
    },
    onSuccess: () => {
      toast.success("Registration successful! Please login.")
      router.push("/login")
    },
    // eslint-disable-next-line
    onError: (error: any) => {
      toast.error(
        error.response?.data?.detail || "Registration failed. Please try again."
      )
    },
  })

  const onSubmit = (values: RegisterFormValues) => {
    registerMutation.mutate(values)
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background">
      <div className="absolute inset-0 z-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sky-100 via-background to-background dark:from-slate-900" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="z-10 w-full max-w-md px-4"
      >
        <Card className="border-border/50 bg-background/60 backdrop-blur-xl shadow-2xl">
          <CardHeader className="space-y-2 pb-6 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl tracking-tight">Create Account</CardTitle>
            <CardDescription className="text-balance">
              Register for your Faculty Portfolio with your official @skit.ac.in email.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Faculty role info banner */}
            <div className="mb-2 flex items-center gap-3 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3">
              <GraduationCap className="size-4 shrink-0 text-primary" />
              <p className="text-xs text-muted-foreground">
                All new accounts are registered as{" "}
                <span className="font-semibold text-primary">Faculty</span>. Contact
                your administrator to be assigned an elevated role.
              </p>
            </div>

            {/* Google Sign Up Button */}
            <div>
              <Button
                type="button"
                variant="outline"
                onClick={handleGoogleSignUp}
                disabled={isGoogleLoading}
                className="w-full h-11 rounded-xl font-medium border-border/70 bg-card hover:bg-muted/40 transition-all shadow-sm active:scale-[0.99] flex items-center justify-center gap-3"
              >
                {isGoogleLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                ) : (
                  <>
                    <svg className="h-5 w-5 shrink-0" viewBox="0 0 24 24">
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
                    <span className="text-[14px]">Sign up with Google</span>
                  </>
                )}
              </Button>
            </div>

            {/* Or continue with email divider */}
            <div className="relative flex items-center justify-center py-1">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border/60" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-3 text-muted-foreground font-medium">
                  Or register with email
                </span>
              </div>
            </div>

            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Institutional Email Address</Label>
                <Input
                  id="email"
                  placeholder="firstname.lastname@skit.ac.in"
                  className="bg-background/50"
                  {...form.register("email")}
                />
                {form.formState.errors.email && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.email.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className="bg-background/50"
                  {...form.register("password")}
                />
                {form.formState.errors.password && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.password.message}
                  </p>
                )}
              </div>
              <Button
                type="submit"
                className="mt-6 w-full group"
                disabled={registerMutation.isPending}
              >
                {registerMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex justify-center border-t border-border/50 p-4">
            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
              <Button
                variant="link"
                className="h-auto p-0 font-medium"
                onClick={() => router.push("/login")}
              >
                Sign In
              </Button>
            </p>
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  )
}
