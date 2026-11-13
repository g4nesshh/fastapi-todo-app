const API = "/api";

const listEl = document.getElementById("list");
const emptyEl = document.getElementById("empty");
const titleEl = document.getElementById("title");
const statusEl = document.getElementById("status");

async function request(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.status === 204 ? null : res.json();
}

async function checkHealth() {
  try {
    await request("/health");
    statusEl.textContent = "Server: online";
    statusEl.className = "status ok";
  } catch {
    statusEl.textContent = "Server: offline";
    statusEl.className = "status err";
  }
}

function render(tasks) {
  listEl.innerHTML = "";
  emptyEl.hidden = tasks.length > 0;

  for (const t of tasks) {
    const li = document.createElement("li");
    if (t.done) li.classList.add("done");

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = t.done;
    cb.addEventListener("change", async () => {
      await request(`/tasks/${t.id}`, { method: "PATCH" });
      loadTasks();
    });

    const span = document.createElement("span");
    span.textContent = t.title;

    const del = document.createElement("button");
    del.className = "del";
    del.textContent = "Delete";
    del.addEventListener("click", async () => {
      await request(`/tasks/${t.id}`, { method: "DELETE" });
      loadTasks();
    });

    li.append(cb, span, del);
    listEl.appendChild(li);
  }
}

async function loadTasks() {
  try {
    render(await request("/tasks"));
  } catch (e) {
    console.error(e);
  }
}

async function addTask() {
  const title = titleEl.value.trim();
  if (!title) return;
  await request("/tasks", { method: "POST", body: JSON.stringify({ title }) });
  titleEl.value = "";
  loadTasks();
}

document.getElementById("addBtn").addEventListener("click", addTask);
titleEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") addTask();
});

checkHealth();
loadTasks();
