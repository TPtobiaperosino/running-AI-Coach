// UI = f(state, props)
// rendering is the process react transform state and props in visible UI.
// when state changes UI changes. rendering links these 2 things. React updates only what is changed recalculating logically the entire UI (this is the renderinge )
// useEffect is used to run some code after the page has been showed, it's used to do things outside the rendering.

"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

async function exchangeCodeForJWT(code: string) {
  const tokenEndpoint =
    process.env.NEXT_PUBLIC_COGNITO_DOMAIN?.replace(/\/$/, "")?.concat("/oauth2/token") ||
    "https://ai-fitness-coach-tobia.auth.eu-west-2.amazoncognito.com/oauth2/token";

  const runtimeRedirect =
    typeof window !== "undefined"
      ? `${window.location.origin}/callback`
      : "http://localhost:3000/callback";

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || "4bno9kh90ejdpvj4kqvcjn9c8e",
    code,
    // Must match an allowed callback in Cognito; prefer env, then current origin (works for localhost + Amplify).
    redirect_uri: process.env.NEXT_PUBLIC_COGNITO_REDIRECT_URI || runtimeRedirect,
  });

  const response = await fetch(tokenEndpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!response.ok) {
    const errorText = await response.text(); // get the error text, take everything from the response and convert it to a string
    throw new Error(errorText); // stop the function here and throw an error
  }

  return response.json();
}

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const code = searchParams.get("code");
  const returnedState = searchParams.get("state");

  useEffect(() => {
    const storedState = sessionStorage.getItem("oauth_state");

    if (!code) {
      console.error("Missing authorisation code");
      return;
    }

    if (!returnedState) {
      console.error("State is missing from callback");
      return;
    }

    if (storedState && returnedState !== storedState) {
      console.error("Invalid state");
      return;
    }

    // If storedState is missing (e.g., user refreshed on callback), proceed but log a warning.
    if (!storedState) {
      console.warn("State missing in sessionStorage; proceeding with token exchange.");
    } else {
      sessionStorage.removeItem("oauth_state");
      console.log("State validated successfully");
    }
    console.log("Authorisation code:", code);

    exchangeCodeForJWT(code)
      .then((tokens) => {
        console.log("TOKENS FROM COGNITO:", tokens);

        if (tokens?.id_token) localStorage.setItem("id_token", tokens.id_token);
        if (tokens?.access_token) localStorage.setItem("access_token", tokens.access_token);
        if (tokens?.refresh_token) localStorage.setItem("refresh_token", tokens.refresh_token);

        router.replace("/home");
      })
      .catch((err) => {
        console.error("Token exchange failed:", err);
      });
  }, [code, returnedState, router]);

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(135deg, #0f172a, #111827)", color: "#e2e8f0", fontFamily: "'DM Sans', 'Inter', system-ui, -apple-system, sans-serif", padding: 24 }}>
      <div style={{ maxWidth: 420, width: "100%", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 18, padding: 24, boxShadow: "0 18px 60px rgba(0,0,0,0.4)", textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 10, padding: "8px 14px", borderRadius: 999, background: "rgba(124, 58, 237, 0.12)", color: "#a855f7", fontWeight: 700, letterSpacing: 0.3, marginBottom: 12 }}>
          Authenticating...
        </div>
        <p style={{ margin: 0, color: "#94a3b8" }}>Loading...</p>
      </div>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense fallback={<div>We are loading you profile :)</div>}>
      <CallbackContent />
    </Suspense>
  );
}
