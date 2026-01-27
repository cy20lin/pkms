async function loadApp(name) {
  const base = `/app/${name}`;

  const html = await fetch(`${base}/app.html`).then(r => r.text());
  document.getElementById("app-root").innerHTML = html;

  document.getElementById("app-style").href = `${base}/app.css`;

  const old = document.getElementById("app-script");
  if (old) old.remove();

  const script = document.createElement("script");
  script.id = "app-script";
  script.src = `${base}/app.js`;
  document.body.appendChild(script);
}

loadApp("search");
