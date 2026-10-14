"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import {
  Sparkles,
  GraduationCap,
  Briefcase,
  Award,
  UserRound,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ExternalLink,
} from "lucide-react"
import { useRole } from "@/components/role-provider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button, buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import api from "@/lib/api"

export default function DashboardPage() {
  const { role, user, profile, isLoading } = useRole()

  const displayName = profile
    ? `${profile.first_name} ${profile.last_name}`
    : user?.email?.split("@")[0] ?? "Faculty Member"

  const { data: education = [] } = useQuery({
    queryKey: ["education-list"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/education/")
        return res.data
      } catch {
        return []
      }
    },
    enabled: !!user,
  })

  const { data: experience = [] } = useQuery({
    queryKey: ["experience-list"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/experience/")
        return res.data
      } catch {
        return []
      }
    },
    enabled: !!user,
  })

  const { data: achievements = [] } = useQuery({
    queryKey: ["achievements-list"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/achievements/")
        return res.data
      } catch {
        return []
      }
    },
    enabled: !!user,
  })

  // Profile completeness score calculation for Sprint 2
  const profileSteps = [
    { name: "Basic Details & Bio", completed: !!profile?.bio },
    { name: "Academic Education", completed: education.length > 0 },
    { name: "Work Experience", completed: experience.length > 0 },
    { name: "Key Achievements", completed: achievements.length > 0 },
  ]
  const completedCount = profileSteps.filter((s) => s.completed).length
  const completenessPercent = Math.round((completedCount / profileSteps.length) * 100)

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      {/* Header section */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
              Welcome back, {displayName}
            </h1>
            <Badge variant="outline" className="text-xs uppercase tracking-wider">
              {role ?? "faculty"}
            </Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Academic portfolio overview and research records for the Generalized Faculty Portfolio System.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge
            variant="secondary"
            className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs text-muted-foreground"
          >
            <Clock className="size-3.5" />
            {new Date().toLocaleDateString("en-US", {
              weekday: "short",
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </Badge>
        </div>
      </div>

      {/* Metrics overview */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="relative overflow-hidden border border-border/60 bg-card/60 backdrop-blur-sm transition-all hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Profile Completeness
            </CardTitle>
            <UserRound className="size-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completenessPercent}%</div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-secondary">
              <div
                className="h-1.5 rounded-full bg-primary transition-all duration-500"
                style={{ width: `${completenessPercent}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-muted-foreground">
              {completedCount} of {profileSteps.length} core sections finished
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border border-border/60 bg-card/60 backdrop-blur-sm transition-all hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Academic Degrees
            </CardTitle>
            <GraduationCap className="size-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{education.length}</div>
            <p className="mt-2 text-xs text-muted-foreground">
              Verified degrees & diplomas
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border border-border/60 bg-card/60 backdrop-blur-sm transition-all hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Experience Records
            </CardTitle>
            <Briefcase className="size-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{experience.length}</div>
            <p className="mt-2 text-xs text-muted-foreground">
              Academic & industry positions
            </p>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border border-border/60 bg-card/60 backdrop-blur-sm transition-all hover:shadow-md">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Recognitions & Awards
            </CardTitle>
            <Award className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{achievements.length}</div>
            <p className="mt-2 text-xs text-muted-foreground">
              Honors, awards and memberships
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main sections */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile checklist */}
        <Card className="lg:col-span-2 border border-border/60 bg-card/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <Sparkles className="size-4 text-primary" />
              Sprint 2: Academic Profile Setup
            </CardTitle>
            <CardDescription>
              Complete the required modules below to ensure accurate reporting and portfolio generation.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="divide-y divide-border/50 rounded-xl border border-border/60 bg-background/50">
              {profileSteps.map((step, idx) => (
                <div key={idx} className="flex items-center justify-between p-3.5">
                  <div className="flex items-center gap-3">
                    {step.completed ? (
                      <CheckCircle2 className="size-5 text-emerald-500" />
                    ) : (
                      <div className="size-5 rounded-full border-2 border-dashed border-muted-foreground/40" />
                    )}
                    <span className="text-sm font-medium">{step.name}</span>
                  </div>
                  <Badge variant={step.completed ? "default" : "secondary"} className="text-xs">
                    {step.completed ? "Completed" : "Action Required"}
                  </Badge>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <Link
                href="/profile"
                className={cn(buttonVariants({ size: "sm" }), "gap-2")}
              >
                Edit Faculty Profile
                <ArrowRight className="size-3.5" />
              </Link>
              <Link
                href="/education"
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  "gap-2"
                )}
              >
                <GraduationCap className="size-3.5" />
                Manage Education
              </Link>
              <Link
                href="/experience"
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  "gap-2"
                )}
              >
                <Briefcase className="size-3.5" />
                Manage Experience
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Institutional info */}
        <Card className="border border-border/60 bg-card/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <ShieldCheck className="size-4 text-primary" />
              Institutional Identity
            </CardTitle>
            <CardDescription>
              Academic department and security credentials.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="rounded-lg border border-border/50 bg-secondary/30 p-3">
              <p className="text-xs text-muted-foreground">Department</p>
              <p className="mt-0.5 font-medium">Computer Science & Engineering (Data Science)</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/30 p-3">
              <p className="text-xs text-muted-foreground">Institution</p>
              <p className="mt-0.5 font-medium">Swami Keshvanand Institute of Technology (SKIT)</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/30 p-3">
              <p className="text-xs text-muted-foreground">System Role</p>
              <p className="mt-0.5 font-medium capitalize">{role ?? "Faculty"}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
