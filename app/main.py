from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.chat import router as chat_router
from app.api.health import router as health_router

app = FastAPI(title="Cortex")

app.include_router(chat_router)
app.include_router(health_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cortex — AI Orchestration Gateway</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0e14;
    color: #e6e6e6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 24px;
  }
  .card { max-width: 640px; width: 100%; }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1a2332;
    color: #4ade80;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 20px;
    letter-spacing: 0.02em;
  }
  .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #4ade80;
  }
  .dot.down { background: #f87171; }
  .dot.pending { background: #6b7280; }
  h1 { font-size: 32px; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.02em; }
  p.tagline { color: #9ca3af; font-size: 16px; line-height: 1.6; margin-bottom: 28px; }
  .features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 24px;
  }
  .feature {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13px;
    color: #d1d5db;
  }
  .feature::before { content: "✓ "; color: #4ade80; font-weight: 700; }
  .status-line {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 28px;
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
  }
  .status-item { display: flex; align-items: center; gap: 6px; }
  .snippet {
    background: #0d1117;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 28px;
    font-family: "SF Mono", Consolas, monospace;
    font-size: 12.5px;
    line-height: 1.7;
    overflow-x: auto;
    color: #9ca3af;
  }
  .snippet .cmd { color: #4ade80; }
  .snippet .str { color: #93c5fd; }
  .links { display: flex; gap: 12px; flex-wrap: wrap; }
  .links a {
    display: inline-block;
    padding: 10px 18px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    transition: opacity 0.15s;
  }
  .links a:hover { opacity: 0.85; }
  .primary { background: #4ade80; color: #0a0e14; }
  .secondary { background: transparent; color: #e6e6e6; border: 1px solid #2d3748; }
</style>
</head>
<body>
  <div class="card">
    <span class="badge"><span class="dot"></span> LIVE</span>
    <h1>Cortex</h1>
    <p class="tagline">
      A resilient, provider-agnostic AI orchestration gateway. Unifies multiple LLM providers behind one interface — with real-time streaming, automatic failover, circuit breaking, caching, and rate limiting.
    </p>
    <div class="features">
      <div class="feature">Multi-provider failover</div>
      <div class="feature">SSE streaming</div>
      <div class="feature">Circuit breaker</div>
      <div class="feature">Redis caching + rate limiting</div>
    </div>

    <div class="status-line" id="status-line">
      <span class="status-item"><span class="dot pending" id="dot-groq"></span> groq</span>
      <span class="status-item"><span class="dot pending" id="dot-gemini"></span> gemini</span>
      <span id="status-text">checking live status…</span>
    </div>

    <div class="snippet">curl -X POST <span class="str">https://cortex-rnhl.onrender.com/chat</span> \\
  -H <span class="str">"Content-Type: application/json"</span> \\
  -d <span class="str">'{"messages": [{"role": "user", "content": "hello"}]}'</span></div>

    <div class="links">
      <a href="/docs" class="primary">API Docs →</a>
      <a href="https://github.com/VinayakTiwari7/cortex" class="secondary">GitHub</a>
    </div>
  </div>

<script>
  fetch('/health/deep')
    .then(r => r.json())
    .then(data => {
      const groqDot = document.getElementById('dot-groq');
      const geminiDot = document.getElementById('dot-gemini');
      const statusText = document.getElementById('status-text');

      groqDot.className = 'dot ' + (data.providers.groq.circuit_open ? 'down' : '');
      geminiDot.className = 'dot ' + (data.providers.gemini.circuit_open ? 'down' : '');
      statusText.textContent = data.status === 'ok' ? 'all systems operational' : 'degraded';
    })
    .catch(() => {
      document.getElementById('status-text').textContent = 'status check unavailable';
    });
</script>
</body>
</html>
"""