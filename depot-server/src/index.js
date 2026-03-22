export default {
    async fetch(request, env) {
        const url = new URL(request.url);

        // POST /upload - iPhoneからCSVを受け取ってKVに保存
        if (request.method === "POST" && url.pathname === "/upload") {
            const body = await request.text();
            const key = `file_${Date.now()}`;
            await env.HOME_STORE.put(key, body);
            return Response.json({ ok: true, key });
        }

        // GET /files - 保存済みのkey一覧を返す
        if (request.method === "GET" && url.pathname === "/files") {
            const list = await env.HOME_STORE.list();
            return Response.json(list.keys);
        }

        // GET /fetch/:key - 特定のファイルを取得
        if (request.method === "GET" && url.pathname.startsWith("/fetch/")) {
            const key = url.pathname.replace("/fetch/", "");
            const value = await env.HOME_STORE.get(key);
            if (!value) return new Response("Not found", { status: 404 });
            return new Response(value, { headers: { "Content-Type": "text/csv" } });
        }

        return new Response("Not found", { status: 404 });
    },
};
