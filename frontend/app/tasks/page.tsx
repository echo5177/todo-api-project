"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  createTask,
  deleteTask,
  getCurrentUser,
  getTasks,
  updateTask,
  type PriorityLevel,
  type Task,
  type User,
} from "@/lib/api";

export default function TasksPage() {
  const router = useRouter();

  const [token, setToken] = useState("");
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<PriorityLevel>("medium");
  const [dueDate, setDueDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");

    if (!storedToken) {
      router.push("/login");
      return;
    }

    setToken(storedToken);
    void initializePage(storedToken);
  }, [router]);

  async function initializePage(currentToken: string) {
    try {
      setLoading(true);
      setErrorMessage("");

      const [user, taskList] = await Promise.all([
        getCurrentUser(currentToken),
        getTasks(currentToken),
      ]);

      setCurrentUser(user);
      setTasks(taskList);
    } catch (error) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("username");

      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("加载失败");
      }

      router.push("/login");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!token) return;

    setSubmitting(true);
    setErrorMessage("");

    try {
      const newTask = await createTask(token, {
        title,
        description,
        priority,
        due_date: dueDate ? dueDate : null,
      });

      setTasks((prev) => [newTask, ...prev]);
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("创建任务失败");
      }
    } finally {
      setSubmitting(false);
    }
  }

  async function handleToggleDone(task: Task) {
    if (!token) return;

    try {
      const updatedTask = await updateTask(token, task.id, {
        done: !task.done,
      });

      setTasks((prev) =>
        prev.map((item) => (item.id === task.id ? updatedTask : item))
      );
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("更新任务失败");
      }
    }
  }

  async function handleDeleteTask(taskId: number) {
    if (!token) return;

    try {
      await deleteTask(token, taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("删除任务失败");
      }
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-lg text-slate-600">页面加载中...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 flex flex-col gap-4 rounded-3xl bg-white p-8 shadow-xl md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">Todo Dashboard</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-900">
              欢迎回来，
              <span className="ml-2">{currentUser?.username}</span>
            </h1>
            <p className="mt-2 text-slate-600">
              你现在看到的是当前登录用户自己的任务列表。
            </p>
          </div>

          <button
            onClick={handleLogout}
            className="rounded-2xl bg-slate-900 px-5 py-3 font-medium text-white transition hover:bg-slate-700"
          >
            退出登录
          </button>
        </div>

        <div className="grid gap-8 lg:grid-cols-[380px_1fr]">
          <section className="rounded-3xl bg-white p-6 shadow-xl">
            <h2 className="text-2xl font-semibold text-slate-900">新建任务</h2>
            <p className="mt-2 text-sm text-slate-600">
              在这里创建一条属于当前用户的新任务。
            </p>

            <form className="mt-6 space-y-4" onSubmit={handleCreateTask}>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  标题
                </label>
                <input
                  type="text"
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="例如：Finish homework"
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  描述
                </label>
                <textarea
                  className="min-h-[120px] w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="写一点任务说明"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  优先级
                </label>
                <select
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as PriorityLevel)}
                >
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  截止日期
                </label>
                <input
                  type="date"
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>

              {errorMessage ? (
                <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
                  {errorMessage}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-2xl bg-slate-900 px-4 py-3 font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? "创建中..." : "创建任务"}
              </button>
            </form>
          </section>

          <section className="rounded-3xl bg-white p-6 shadow-xl">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-slate-900">我的任务</h2>
              <p className="mt-2 text-sm text-slate-600">
                这里只会显示当前登录用户自己的任务。
              </p>
            </div>

            {tasks.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
                目前还没有任务，先在左边创建一条吧。
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => (
                  <article
                    key={task.id}
                    className="rounded-2xl border border-slate-200 p-5"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div className="flex-1">
                        <div className="mb-3 flex flex-wrap items-center gap-2">
                          <span
                            className={`rounded-full px-3 py-1 text-xs font-medium ${
                              task.done
                                ? "bg-green-100 text-green-700"
                                : "bg-amber-100 text-amber-700"
                            }`}
                          >
                            {task.done ? "done" : "pending"}
                          </span>

                          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                            {task.priority}
                          </span>

                          {task.due_date ? (
                            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                              due: {task.due_date}
                            </span>
                          ) : null}
                        </div>

                        <h3 className="text-xl font-semibold text-slate-900">
                          {task.title}
                        </h3>

                        <p className="mt-2 whitespace-pre-wrap text-slate-600">
                          {task.description || "No description"}
                        </p>
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => handleToggleDone(task)}
                          className="rounded-xl bg-slate-100 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-200"
                        >
                          {task.done ? "标记未完成" : "标记完成"}
                        </button>

                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="rounded-xl bg-red-100 px-4 py-2 text-sm font-medium text-red-700 transition hover:bg-red-200"
                        >
                          删除
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
