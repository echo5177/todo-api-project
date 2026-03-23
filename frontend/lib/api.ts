const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type PriorityLevel = "low" | "medium" | "high";
export type DoneFilter = "all" | "pending" | "done";

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

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export async function registerUser(data: {
  email: string;
  username: string;
  password: string;
}): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return handleResponse<User>(response);
}

export async function loginUser(data: {
  username: string;
  password: string;
}): Promise<TokenResponse> {
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

  return handleResponse<TokenResponse>(response);
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<User>(response);
}

export async function getTasks(
  token: string,
  filters?: {
    done?: DoneFilter;
    priority?: "" | PriorityLevel;
    due_before?: string;
  }
): Promise<Task[]> {
  const query = new URLSearchParams();

  if (filters?.done === "done") {
    query.append("done", "true");
  } else if (filters?.done === "pending") {
    query.append("done", "false");
  }

  if (filters?.priority) {
    query.append("priority", filters.priority);
  }

  if (filters?.due_before) {
    query.append("due_before", filters.due_before);
  }

  const queryString = query.toString();
  const url = queryString
    ? `${API_BASE_URL}/tasks?${queryString}`
    : `${API_BASE_URL}/tasks`;

  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<Task[]>(response);
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

  return handleResponse<Task>(response);
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

  return handleResponse<Task>(response);
}

export async function deleteTask(
  token: string,
  taskId: number
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return handleResponse<{ message: string }>(response);
}

async function handleResponse<T>(response: Response): Promise<T> {
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

  return data as T;
}
