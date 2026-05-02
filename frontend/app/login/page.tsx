"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { loginUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (token) {
      router.push("/tasks");
      return;
    }

    setCheckingAuth(false);
  }, [router]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password) {
      setErrorMessage("用户名和密码都不能为空");
      return;
    }

    setLoading(true);
    setErrorMessage("");

    try {
    const result = await loginUser({
      username: trimmedUsername,
      password,
    });


      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("username", trimmedUsername);

      router.push("/tasks");
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("登录失败");
      }
    } finally {
      setLoading(false);
    }
  }

  if (checkingAuth) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-lg text-slate-600">正在检查登录状态...</p>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-xl">
        <div className="mb-8">
          <Link href="/" className="text-sm text-slate-500 hover:text-slate-800">
            ← 返回首页
          </Link>
          <h1 className="mt-4 text-3xl font-bold text-slate-900">登录</h1>
          <p className="mt-2 text-slate-600">
            登录后进入你的任务工作台。
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              用户名
            </label>
            <input
              type="text"
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="alice"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              密码
            </label>
            <input
              type="password"
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              required
            />
          </div>

          {errorMessage ? (
            <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-slate-900 px-4 py-3 font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "登录中..." : "登录"}
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-600">
          还没有账号？
          <Link
            href="/register"
            className="ml-2 font-medium text-slate-900 hover:underline"
          >
            去注册
          </Link>
        </p>
      </div>
    </main>
  );
}
