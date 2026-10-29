import { getStore } from "@netlify/blobs";

const KEY = "aravind123";
const TTL = 6 * 3600 * 1000; // ms before question/answer expire

export const config = { path: ["/ask", "/answer", "/reply", "/question"] };

export default async (req) => {
  const url = new URL(req.url);
  if (url.searchParams.get("key") !== KEY) return new Response("bad key", { status: 403 });

  const store = getStore({ name: "qa", consistency: "strong" });
  let slot = (await store.get("slot", { type: "json" })) || { q: "", a: "", t: 0 };
  if (slot.t && Date.now() - slot.t > TTL) slot = { q: "", a: "", t: 0 };

  const path = url.pathname;
  if (path === "/ask" && req.method === "POST") {
    slot = { q: await req.text(), a: "", t: Date.now() };
    await store.setJSON("slot", slot);
    return new Response("question saved");
  }
  if (path === "/reply" && req.method === "POST") {
    slot.a = await req.text();
    await store.setJSON("slot", slot);
    return new Response("Sent! You can close this page.");
  }
  if (path === "/answer") return new Response(slot.a || "no answer yet");
  if (path === "/question") return new Response(slot.q);
  return new Response("not found", { status: 404 });
};
