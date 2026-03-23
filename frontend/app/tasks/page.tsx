"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import {
  createTask,
  deleteTask,
  getCurrentUser,
  getTasks,
  updateTask,
  type DoneFilter,
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

  const [doneFilter, setDoneFilter] = useState<DoneFilter>("all");
  const [priorityFilter, setPriorityFilter] = useState<"" | PriorityLevel>("");
  const [dueBeforeFilter, setDueBeforeFilter] = useState("");

  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editPriority, setEditPriority] = useState<PriorityLevel>("medium");
  const [editDueDate, setEditDueDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [savingEdit, setSavingEdit] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");

    if (!storedToken) {
      router.push("/login");
      return;
    }

    setToken(storedToken);
    void initializePage(storedToken);
  }, [router]);

  const stats = useMemo(() => {
    const total = tasks.length;
    const done = tasks.filter((task) => task.done).length;
    const pending = tasks.filter((task) => !task.done).length;
    const highPriority = tasks.filter((task) => task.priority === "high").length;

    return {
      total,
      done,
      pending,
      highPriority,
    };
  }, [tasks]);

  async function initializePage(currentToken: string) {
    try {
      setLoading(true);
      setErrorMessage("");
      setSuccessMessage("");

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

  async function refreshTasks(currentToken?: string) {
    const activeToken = currentToken || token;
    if (!activeToken) return;

    try {
      setRefreshing(true);
      setErrorMessage("");
      setSuccessMessage("");

      const taskList = await getTasks(activeToken, {
        done: doneFilter,
        priority: priorityFilter,
        due_before: dueBeforeFilter,
      });

      setTasks(taskList);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("刷新失败");
      }
    } finally {
      setRefreshing(false);
    }
  }

  async function handleCreateTask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!token) return;

    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();

    if (!trimmedTitle) {
      setErrorMessage("任务标题不能为空");
      setSuccessMessage("");
      return;
    }

    setSubmitting(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      await createTask(token, {
        title: trimmedTitle,
        description: trimmedDescription,
        priority,
        due_date: dueDate ? dueDate : null,
      });

      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setSuccessMessage("任务创建成功");

      await refreshTasks(token);
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
      setErrorMessage("");
      setSuccessMessage("");

      await updateTask(token, task.id, {
        done: !task.done,
      });

      setSuccessMessage(task.done ? "任务已标记为未完成" : "任务已标记为完成");
      await refreshTasks(token);
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

    const confirmed = window.confirm("确定要删除这条任务吗？删除后无法恢复。");
    if (!confirmed) {
      return;
    }

    try {
      setErrorMessage("");
      setSuccessMessage("");

      await deleteTask(token, taskId);
      setSuccessMessage("任务删除成功");
      await refreshTasks(token);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("删除任务失败");
      }
    }
  }

  function startEditing(task: Task) {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setEditPriority(task.priority);
    setEditDueDate(task.due_date || "");
    setErrorMessage("");
    setSuccessMessage("");
  }

  function cancelEditing() {
    setEditingTaskId(null);
    setEditTitle("");
    setEditDescription("");
    setEditPriority("medium");
    setEditDueDate("");
  }

  async function handleSaveEdit(taskId: number) {
    if (!token) return;

    const trimmedTitle = editTitle.trim();
    const trimmedDescription = editDescription.trim();

    if (!trimmedTitle) {
      setErrorMessage("编辑后的标题不能为空");
      setSuccessMessage("");
      return;
    }

    try {
      setSavingEdit(true);
      setErrorMessage("");
      setSuccessMessage("");

      await updateTask(token, taskId, {
        title: trimmedTitle,
        description: trimmedDescription,
        priority: editPriority,
        due_date: editDueDate ? editDueDate : null,
      });

      cancelEditing();
      setSuccessMessage("任务修改成功");
      await refreshTasks(token);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("保存修改失败");
      }
    } finally {
      setSavingEdit(false);
    }
  }

  async function handleApplyFilters() {
    await refreshTasks(token);
  }

  async function handleClearFilters() {
    setDoneFilter("all");
    setPriorityFilter("");
    setDueBeforeFilter("");

    if (!token) return;

    try {
      setRefreshing(true);
      setErrorMessage("");
      setSuccessMessage("");

      const taskList = await getTasks(token);
      setTasks(taskList);
      setSuccessMessage("筛选条件已清空");
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("清空筛选失败");
      }
    } finally {
      setRefreshing(false);
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
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-col gap-4 rounded-3xl bg-white p-8 shadow-xl md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">Todo Dashboard</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-900">
              欢迎回来，
              <span className="ml-2">{currentUser?.username}</span>
            </h1>
            <p className="mt-2 text-slate-600">
              今天继续把这个网站打磨得更像一个正式产品。
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => void refreshTasks()}
              className="rounded-2xl bg-slate-100 px-5 py-3 font-medium text-slate-800 transition hover:bg-slate-200"
            >
              {refreshing ? "刷新中..." : "刷新列表"}
            </button>

            <button
              onClick={handleLogout}
              className="rounded-2xl bg-slate-900 px-5 py-3 font-medium text-white transition hover:bg-slate-700"
            >
              退出登录
            </button>
          </div>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-3xl bg-white p-6 shadow-xl">
            <p className="text-sm text-slate-500">总任务数</p>
            <p className="mt-3 text-3xl font-bold text-slate-900">{stats.total}</p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-xl">
            <p className="text-sm text-slate-500">未完成</p>
            <p className="mt-3 text-3xl font-bold text-amber-600">{stats.pending}</p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-xl">
            <p className="text-sm text-slate-500">已完成</p>
            <p className="mt-3 text-3xl font-bold text-green-600">{stats.done}</p>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-xl">
            <p className="text-sm text-slate-500">高优先级</p>
            <p className="mt-3 text-3xl font-bold text-red-600">
              {stats.highPriority}
            </p>
          </div>
        </div>

        {errorMessage ? (
          <div className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMessage}
          </div>
        ) : null}

        {successMessage ? (
          <div className="mb-6 rounded-2xl bg-green-50 px-4 py-3 text-sm text-green-700">
            {successMessage}
          </div>
        ) : null}

        <div className="grid gap-8 lg:grid-cols-[360px_1fr]">
          <section className="space-y-8">
            <div className="rounded-3xl bg-white p-6 shadow-xl">
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

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full rounded-2xl bg-slate-900 px-4 py-3 font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? "创建中..." : "创建任务"}
                </button>
              </form>
            </div>

            <div className="rounded-3xl bg-white p-6 shadow-xl">
              <h2 className="text-2xl font-semibold text-slate-900">筛选任务</h2>
              <p className="mt-2 text-sm text-slate-600">
                通过完成状态、优先级和截止日期过滤你的任务。
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    完成状态
                  </label>
                  <select
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                    value={doneFilter}
                    onChange={(e) => setDoneFilter(e.target.value as DoneFilter)}
                  >
                    <option value="all">all</option>
                    <option value="pending">pending</option>
                    <option value="done">done</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    优先级
                  </label>
                  <select
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                    value={priorityFilter}
                    onChange={(e) =>
                      setPriorityFilter(e.target.value as "" | PriorityLevel)
                    }
                  >
                    <option value="">all</option>
                    <option value="low">low</option>
                    <option value="medium">medium</option>
                    <option value="high">high</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    截止日期早于
                  </label>
                  <input
                    type="date"
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                    value={dueBeforeFilter}
                    onChange={(e) => setDueBeforeFilter(e.target.value)}
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => void handleApplyFilters()}
                    className="flex-1 rounded-2xl bg-slate-900 px-4 py-3 font-medium text-white transition hover:bg-slate-700"
                  >
                    应用筛选
                  </button>

                  <button
                    onClick={() => void handleClearFilters()}
                    className="flex-1 rounded-2xl bg-slate-100 px-4 py-3 font-medium text-slate-800 transition hover:bg-slate-200"
                  >
                    清空筛选
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-3xl bg-white p-6 shadow-xl">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-slate-900">我的任务</h2>
              <p className="mt-2 text-sm text-slate-600">
                这里只显示当前登录用户自己的任务。
              </p>
            </div>

            {tasks.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
                当前没有匹配条件的任务。
              </div>
            ) : (
              <div className="space-y-4">
                {tasks.map((task) => {
                  const isEditing = editingTaskId === task.id;

                  return (
                    <article
                      key={task.id}
                      className="rounded-2xl border border-slate-200 p-5"
                    >
                      {isEditing ? (
                        <div className="space-y-4">
                          <div>
                            <label className="mb-2 block text-sm font-medium text-slate-700">
                              标题
                            </label>
                            <input
                              type="text"
                              className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                              value={editTitle}
                              onChange={(e) => setEditTitle(e.target.value)}
                            />
                          </div>

                          <div>
                            <label className="mb-2 block text-sm font-medium text-slate-700">
                              描述
                            </label>
                            <textarea
                              className="min-h-[100px] w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                              value={editDescription}
                              onChange={(e) => setEditDescription(e.target.value)}
                            />
                          </div>

                          <div className="grid gap-4 md:grid-cols-2">
                            <div>
                              <label className="mb-2 block text-sm font-medium text-slate-700">
                                优先级
                              </label>
                              <select
                                className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
                                value={editPriority}
                                onChange={(e) =>
                                  setEditPriority(e.target.value as PriorityLevel)
                                }
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
                                value={editDueDate}
                                onChange={(e) => setEditDueDate(e.target.value)}
                              />
                            </div>
                          </div>

                          <div className="flex gap-3">
                            <button
                              onClick={() => void handleSaveEdit(task.id)}
                              disabled={savingEdit}
                              className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                              {savingEdit ? "保存中..." : "保存修改"}
                            </button>

                            <button
                              onClick={cancelEditing}
                              disabled={savingEdit}
                              className="rounded-xl bg-slate-100 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                              取消
                            </button>
                          </div>
                        </div>
                      ) : (
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

                          <div className="flex flex-wrap gap-3">
                            <button
                              onClick={() => void handleToggleDone(task)}
                              className="rounded-xl bg-slate-100 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-200"
                            >
                              {task.done ? "标记未完成" : "标记完成"}
                            </button>

                            <button
                              onClick={() => startEditing(task)}
                              className="rounded-xl bg-blue-100 px-4 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-200"
                            >
                              编辑
                            </button>

                            <button
                              onClick={() => void handleDeleteTask(task.id)}
                              className="rounded-xl bg-red-100 px-4 py-2 text-sm font-medium text-red-700 transition hover:bg-red-200"
                            >
                              删除
                            </button>
                          </div>
                        </div>
                      )}
                    </article>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
