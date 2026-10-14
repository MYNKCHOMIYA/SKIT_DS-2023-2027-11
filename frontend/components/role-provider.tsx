"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import api from "@/lib/api"
import { useRouter, usePathname } from "next/navigation"
import { Loader2 } from "lucide-react"

export type Role = "admin" | "hod" | "faculty"

interface RoleContextValue {
  role: Role | null
  setRole: (r: Role) => void
  user: any | null
  profile: any | null
  isLoading: boolean
  logout: () => void
}

const RoleContext = createContext<RoleContextValue | null>(null)

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()

  const [token, setToken] = useState<string | null | undefined>(undefined)

  // Read token from localStorage on mount and when pathname changes
  useEffect(() => {
    setToken(localStorage.getItem("token"))
  }, [pathname])

  // Keep token state in sync when user navigates (handles login/logout in other tabs)
  useEffect(() => {
    const sync = () => setToken(localStorage.getItem("token"))
    window.addEventListener("storage", sync)
    return () => window.removeEventListener("storage", sync)
  }, [])

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ["auth-me"],
    queryFn: async () => {
      const res = await api.get("/api/v1/auth/me")
      return res.data
    },
    // Only run once we know the token state (token !== undefined)
    enabled: typeof token === "string",
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["profile-me"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/profile/me")
        return res.data
      } catch (err: any) {
        if (err.response?.status === 404) return null
        throw err
      }
    },
    enabled: !!user && user.role !== "admin",
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  useEffect(() => {
    // Wait until we've read localStorage (token !== undefined)
    if (token === undefined) return

    const isAuthPage =
      pathname?.startsWith("/login") || pathname?.startsWith("/register")
    if (isAuthPage) {
      if (token) {
        router.push("/")
      }
      return
    }

    if (!token) {
      router.push("/login")
    }
  }, [token, pathname, router])

  const logout = () => {
    localStorage.removeItem("token")
    setToken(null)
    router.push("/login")
  }

  const jwtRole = user?.role as Role | undefined
  const role: Role | null = jwtRole ?? null
  const isLoading =
    token === undefined ||
    userLoading ||
    (typeof token === "string" && profileLoading)

  const setRole = (_r: Role) => {}

  if (token === undefined) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <RoleContext.Provider
      value={{ role, setRole, user, profile, isLoading, logout }}
    >
      {children}
    </RoleContext.Provider>
  )
}

export function useRole() {
  const ctx = useContext(RoleContext)
  if (!ctx) throw new Error("useRole must be used within RoleProvider")
  return ctx
}
