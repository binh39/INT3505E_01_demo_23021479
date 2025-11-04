// Simple auth helper for access/refresh token handling and authorized fetch
(function () {
  const BASE =
    (typeof window !== "undefined" && window.API_URL) ||
    "http://localhost:5000";

  function getUser() {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  }

  function getAccessToken() {
    return localStorage.getItem("access_token");
  }

  function getRefreshToken() {
    return localStorage.getItem("refresh_token");
  }

  function setSession({ access_token, refresh_token, user }) {
    if (access_token) localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
    if (user) localStorage.setItem("user", JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }

  async function refreshAccessToken() {
    const rt = getRefreshToken();
    if (!rt) return null;
    try {
      const res = await fetch(`${BASE}/api/sessions/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: rt }),
      });
      if (!res.ok) return null;
      const data = await res.json();
      const newAccess = data?.data?.access_token;
      if (newAccess) {
        localStorage.setItem("access_token", newAccess);
        return newAccess;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  async function fetchWithAuth(path, options = {}, retry = true) {
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      options.headers || {}
    );
    const at = getAccessToken();
    if (at) headers["Authorization"] = `Bearer ${at}`;

    const res = await fetch(path.startsWith("http") ? path : `${BASE}${path}`, {
      ...options,
      headers,
    });

    if (res.status !== 401) {
      return res;
    }

    // try refresh once
    if (!retry) return res;
    const newAt = await refreshAccessToken();
    if (!newAt) return res;

    const headers2 = Object.assign(
      { "Content-Type": "application/json" },
      options.headers || {}
    );
    headers2["Authorization"] = `Bearer ${newAt}`;
    return fetch(path.startsWith("http") ? path : `${BASE}${path}`, {
      ...options,
      headers: headers2,
    });
  }

  async function logoutAndRedirect() {
    try {
      const at = getAccessToken();
      const rt = getRefreshToken();
      await fetchWithAuth(
        "/api/sessions",
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: rt }),
        },
        false
      );
    } catch (e) {
      // ignore
    } finally {
      clearSession();
      window.location.href = "login.html";
    }
  }

  // expose to global
  window.Auth = {
    getUser,
    getAccessToken,
    getRefreshToken,
    setSession,
    clearSession,
    fetchWithAuth,
    logout: logoutAndRedirect,
    BASE,
  };

  // keep old onclick="logout()" working
  window.logout = logoutAndRedirect;
})();
