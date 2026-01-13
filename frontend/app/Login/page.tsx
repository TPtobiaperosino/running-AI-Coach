// this will be the front door of the app
// I need to send the user to Cognito, I'm delegating the authentication to Cognito
// The login button just sends the browser to Cognito --> it is a redirect
// If cognito authorises the user and login works, Cognito gives to the browser a code and dends the browser back to the app
// Code is just used at every login OAuth when a new JWT is needed and lasts a few minutes

// Browser goes back to the app with a URL like "http://localhost:3000/callback?code=ABC123" which is the address of the callback page
// The callback page is made of HTML and JS run by the browser when it goes through the corresponding URL
// A URL is associated to a page through Next.js --> I create the callback page associated to the URL with the code so browser when it reads it loads the callback page
// The browser, loads the page and execues the JS inside it. JS finds the code and extracts it.
// Callback will be used to get the JWT, with a library Auth callback will be read, and then code exchanged with the JWT with Cognito

// The JS, after reading the code calls an Amplify Auth function or a manual fetch --> makes http request to Cognito --> exchanges the code with the JWT

// Just for reference --> fetch is a way to ask data to a server without changing page

// Therefore I need to build a login button that does a redirect for the browser towards Cognito. --> window.location.href = "https://your-cognito-domain/login?...";
// I'll use TypeScript + JSX using react withing the Next.js framework

"use client"; // Debug ERROR 1 --> the code below runs in the browser so I need to use Client Component

// I should avoid generating a random string at the beginning because can be predictabl. Doing the conversion from the array is safer.

export default function HomePage() {
  // defining the page; export default makes this component importable as default

  function generateState(): string {
    const array = new Uint8Array(16);
    // creating an array of 16 cells, each cell = 1 byte (binary-safe array)

    crypto.getRandomValues(array);
    // browser crypto API, secure and non-predictable (Math.random is predictable)

    return Array.from(array)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }

  // map() converts values
  // toString(16) converts to hex (e.g. 10 = "a")
  // padStart ensures 2 digits per byte

  function handleLogin() {
    // in React, pages are components (functions)
    const state = generateState();

    sessionStorage.setItem("oauth_state", state);
    // saving state in browser storage (key-value)

    const cognitoDomain =
      process.env.NEXT_PUBLIC_COGNITO_DOMAIN ||
      "https://ai-fitness-coach-tobia.auth.eu-west-2.amazoncognito.com";
    const clientId =
      process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || "4bno9kh90ejdpvj4kqvcjn9c8e";
    // Prefer env; otherwise use current origin (works for localhost + Amplify).
    const runtimeRedirect =
      typeof window !== "undefined"
        ? `${window.location.origin}/callback`
        : "http://localhost:3000/callback";
    const redirectUri = encodeURIComponent(
      process.env.NEXT_PUBLIC_COGNITO_REDIRECT_URI || runtimeRedirect
    ); // must match exactly the callback URL in Cognito allow list
    const scope = encodeURIComponent("openid email profile");
    // 
    const url =
      `${cognitoDomain}/oauth2/authorize` +
      `?response_type=code` +
      `&client_id=${clientId}` +
      `&redirect_uri=${redirectUri}` +
      `&scope=${scope}` +
      `&state=${state}`;

    window.location.href = url;
    // browser redirect to Cognito Hosted UI
  }

    return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(135deg, #0f172a 0%, #111827 50%, #0f172a 100%)", color: "#e2e8f0", fontFamily: "'DM Sans', 'Inter', system-ui, -apple-system, sans-serif", padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 520, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 18, padding: 28, boxShadow: "0 18px 60px rgba(0,0,0,0.4)" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 10, padding: "8px 14px", borderRadius: 999, background: "rgba(124, 58, 237, 0.12)", color: "#a855f7", fontWeight: 700, letterSpacing: 0.3 }}>
          <span role="img" aria-label="sparkles">✨</span> AI Meal Coach
        </div>
        <h1 style={{ margin: "14px 0 8px", fontSize: 30, letterSpacing: -0.4 }}>Welcome back</h1>
        <p style={{ margin: "0 0 20px", color: "#94a3b8" }}>Log in with your account to upload meals and get instant nutrition insights.</p>
        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            border: "none",
            borderRadius: 12,
            padding: "14px 16px",
            background: "linear-gradient(135deg, #7c3aed, #a855f7)",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer",
            boxShadow: "0 14px 40px rgba(124,58,237,0.35)",
            transition: "transform 0.1s ease",
          }}
        >
          Log in
        </button>
      </div>
    </div>
  );
}

//ERROR 1: on Click does not work and gives error because:
// Code runs on:
//1) Server --> remote computer which generates HTML, does not see clicks, browser, does not have browser console
//2) Browser: Chrome e.g., sees clicks, buttons, eruns JS, can do redirect --> clicks can be seen only in the browser
// In Next.js pages run on server, not in the browser (this makes everything faster and better SEO)
// 2 types of component --> (i) Server which is default and (ii) Client which runs in the browser
// !!!! I need to tell to Next.js that I want this component running on the browser (make it client) --> to do so I need to write at the beginning "use client"
