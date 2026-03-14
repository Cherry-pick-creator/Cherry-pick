import { ApiErrorBody } from "./types";

const API_BASE = "https://cherry-pick-production.up.railway.app/api/v1";

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function fetchJson<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let body: ApiErrorBody;
    try {
      body = await res.json();
    } catch {
      throw new ApiError("UNKNOWN", `HTTP ${res.status}`, res.status);
    }
    throw new ApiError(body.error, body.message, res.status);
  }

  return res.json();
}

export async function fetchFormData<T>(
  path: string,
  formData: FormData,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    let body: ApiErrorBody;
    try {
      body = await res.json();
    } catch {
      throw new ApiError("UNKNOWN", `HTTP ${res.status}`, res.status);
    }
    throw new ApiError(body.error, body.message, res.status);
  }

  return res.json();
}
