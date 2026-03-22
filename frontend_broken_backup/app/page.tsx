import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-3xl rounded-3xl bg-white p-10 shadow-xl">
        <div className="mb-8">
          <p className="mb-3 inline-block rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
            Phase 2 · Day 3
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            Todo Website Prototype
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            这是你的第一个真正可以在浏览器里操作的 Todo 网站雏形。
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Link
            href="/register"
            className="rounded-2xl border border-slate-200 p-6 transition hover:shadow-md"
          >
            <h2 className="text-2xl font-semibold text-slate-900">注册</h2>
            <p className="mt-2 text-slate-600">
              创建一个新用户账号，作为网站使用入口。
            </p>
          </Link>

          <Link
            href="/login"
            className="rounded-2xl border border-slate-200 p-6 transition hover:shadow-md"
          >
            <h2 className="text-2xl font-semibold text-slate-900">登录</h2>
            <p className="mt-2 text-slate-600">
              登录后进入任务列表页，读取你自己的任务。
            </p>
          </Link>
        </div>
      </div>
    </main>
  );
}
