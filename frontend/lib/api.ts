const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type PriorityLevel = "low" | "medium" | "high";

export type Task = {
  id: number;
  title: string;
  description: string;
  done: boolean;
  priority: PriorityLevel;
  due_date: string | null;
  owner_id: number | null;
};

export type User = {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
};

export async function registerUser(data: {
  email: string;
  username: string;
  password: string;
}) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return handleResponse(response);
}

export async function loginUser(data: {
  username: string;
  password: string;
}) {
  const formData = new URLSearchParams();
  formData.append("username", data.username);
  formData.append("password", data.password);

  const response = await fetch(`${API_BASE_URL}/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  return handleResponse(response);
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(response);
}

export async function getTasks(token: string): Promise<Task[]> {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(response);
}

export async function createTask(
  token: string,
  data: {
    title: string;
    description: string;
    priority: PriorityLevel;
    due_date: string | null;
  }
): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(response);
}

export async function updateTask(
  token: string,
  taskId: number,
  data: Partial<{
    title: string;
    description: string;
    done: boolean;
    priority: PriorityLevel;
    due_date: string | null;
  }>
): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleResponse(response);
}

export async function deleteTask(token: string, taskId: number) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse(response);
}

async function handleResponse(response: Response) {
  const contentType = response.headers.get("content-type");

  let data: unknown = null;
  if (contentType && contentType.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof (data as { detail: unknown }).detail === "string"
        ? (data as { detail: string }).detail
        : "Request failed";

    throw new Error(detail);
  }

  return data;
}
