export async function fetchWithAuth(input: RequestInfo, init: RequestInit = {}): Promise<any> {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    const headers = {
      ...(init.headers || {}),
      Authorization: token ? `Bearer ${token}` : "",
    };
  
    const res = await fetch(input, { ...init, headers });
  
    if (res.status === 401) {
      const refresh = await fetch("http://localhost:8000/auth/refresh", {
        method: "POST",
        credentials: "include",
      });
  
      if (refresh.ok) {
        const data = await refresh.json();
        localStorage.setItem("access_token", data.access_token);
  
        const retryRes = await fetch(input, {
          ...init,
          headers: {
            ...headers,
            Authorization: `Bearer ${data.access_token}`,
          },
        });
  
        if (retryRes.ok) return retryRes.json();
        throw await retryRes.json();
      } else {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        throw new Error("Unauthorized");
      }
    }
  
    if (!res.ok) throw await res.json();
    return res.json();
  }
  