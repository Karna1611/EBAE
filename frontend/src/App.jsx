import { useState, useEffect } from "react";

const API = "http://localhost:8000/api/v1";

// ── DESIGN TOKENS ──
const css = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --navy: #0A1628;
    --navy-2: #112240;
    --navy-3: #1a3a6b;
    --teal: #00C2A8;
    --teal-dim: rgba(0,194,168,0.12);
    --amber: #F5A623;
    --amber-dim: rgba(245,166,35,0.12);
    --red: #E84855;
    --red-dim: rgba(232,72,85,0.12);
    --green: #2DD4AA;
    --green-dim: rgba(45,212,170,0.12);
    --paper: #F7F6F2;
    --paper-2: #EEECEA;
    --text: #0A1628;
    --text-2: #4A5568;
    --text-3: #8A9AB0;
    --border: rgba(10,22,40,0.1);
    --border-2: rgba(10,22,40,0.06);
    --mono: 'DM Mono', monospace;
    --sans: 'DM Sans', sans-serif;
    --radius: 10px;
    --radius-sm: 6px;
  }

  body {
    font-family: var(--sans);
    background: var(--paper);
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
  }

  input, textarea, select {
    font-family: var(--sans);
    font-size: 13px;
    width: 100%;
    padding: 9px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background: white;
    color: var(--text);
    outline: none;
    transition: border-color 0.15s;
  }
  input:focus, textarea:focus, select:focus { border-color: var(--teal); }
  textarea { resize: vertical; }

  button {
    font-family: var(--sans);
    cursor: pointer;
    border: none;
    border-radius: var(--radius-sm);
    transition: all 0.15s;
  }

  .btn-primary {
    background: var(--navy);
    color: white;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn-primary:hover { background: var(--navy-3); }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

  .btn-secondary {
    background: white;
    color: var(--text);
    padding: 8px 16px;
    font-size: 13px;
    border: 1px solid var(--border);
  }
  .btn-secondary:hover { border-color: var(--navy-3); }

  .btn-teal {
    background: var(--teal);
    color: var(--navy);
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn-teal:hover { background: var(--green); }
  .btn-teal:disabled { opacity: 0.4; cursor: not-allowed; }

  .card {
    background: white;
    border: 1px solid var(--border-2);
    border-radius: var(--radius);
    padding: 20px;
  }

  .label-badge {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: 4px;
  }
  .label-PRESENT { background: var(--green-dim); color: #0D7A5F; }
  .label-PARTIAL { background: var(--amber-dim); color: #92580A; }
  .label-ABSENT { background: var(--border-2); color: var(--text-3); }
  .label-CONTRADICTORY { background: var(--red-dim); color: #B91C2C; }

  .status-badge {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: 4px;
  }
  .status-COMPLETE { background: var(--green-dim); color: #0D7A5F; }
  .status-PENDING { background: var(--amber-dim); color: #92580A; }
  .status-PROCESSING { background: var(--teal-dim); color: #0A7A6A; }
  .status-FAILED { background: var(--red-dim); color: #B91C2C; }

  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner {
    width: 16px; height: 16px;
    border: 2px solid var(--border);
    border-top-color: var(--teal);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
  }

  @keyframes fillBar {
    from { width: 0; }
    to { width: var(--target-width); }
  }
  .conf-bar-fill {
    animation: fillBar 0.6s ease-out forwards;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-radius: var(--radius-sm);
    color: var(--text-2);
    font-size: 13px;
    font-weight: 400;
    cursor: pointer;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    transition: all 0.12s;
  }
  .nav-item:hover { background: var(--paper-2); color: var(--text); }
  .nav-item.active { background: var(--navy); color: white; font-weight: 500; }
  .nav-item.active .nav-icon { color: var(--teal); }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-2);
  }

  .page-title { font-size: 20px; font-weight: 600; letter-spacing: -0.02em; }
  .page-subtitle { font-size: 13px; color: var(--text-2); margin-top: 2px; }

  .stat-card {
    background: white;
    border: 1px solid var(--border-2);
    border-radius: var(--radius);
    padding: 16px 20px;
  }
  .stat-value { font-size: 28px; font-weight: 600; font-family: var(--mono); letter-spacing: -0.03em; }
  .stat-label { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-3);
  }
  .empty-state-icon { font-size: 32px; margin-bottom: 12px; opacity: 0.4; }
  .empty-state-text { font-size: 14px; }

  .toast {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--navy);
    color: white;
    padding: 12px 18px;
    border-radius: var(--radius-sm);
    font-size: 13px;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    animation: slideIn 0.2s ease;
  }
  @keyframes slideIn { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
`;

// ── HELPERS ──
async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

function Spinner() {
  return <span className="spinner" />;
}

function Toast({ msg, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3000);
    return () => clearTimeout(t);
  }, []);
  return <div className="toast">✓ {msg}</div>;
}

function LabelBadge({ label }) {
  return <span className={`label-badge label-${label}`}>{label}</span>;
}

function StatusBadge({ status }) {
  return <span className={`status-badge status-${status}`}>{status}</span>;
}

function ConfBar({ value, color = "var(--teal)" }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 5, background: "var(--paper-2)", borderRadius: 3, overflow: "hidden" }}>
        <div
          className="conf-bar-fill"
          style={{ "--target-width": `${pct}%`, height: "100%", background: color, borderRadius: 3 }}
        />
      </div>
      <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--text-3)", minWidth: 30 }}>{pct}%</span>
    </div>
  );
}

// ── NAV ──
const VIEWS = { QUESTIONS: "questions", SUBMIT: "submit", REVIEW: "review", ANALYTICS: "analytics" };

const NAV_ITEMS = [
  { id: VIEWS.QUESTIONS, label: "Questions", icon: "📋", desc: "Manage questions & rubrics" },
  { id: VIEWS.SUBMIT, label: "Student portal", icon: "✏️", desc: "Submit & view answers" },
  { id: VIEWS.REVIEW, label: "Review queue", icon: "🔍", desc: "Human oversight" },
  { id: VIEWS.ANALYTICS, label: "Analytics", icon: "📊", desc: "Performance insights" },
];

function Sidebar({ view, setView }) {
  return (
    <div style={{ width: 220, background: "white", borderRight: "1px solid var(--border-2)", display: "flex", flexDirection: "column", padding: "0 12px", flexShrink: 0 }}>
      <div style={{ padding: "20px 4px 16px" }}>
        <div style={{ fontWeight: 600, fontSize: 16, letterSpacing: "-0.02em" }}>EBAE</div>
        <div style={{ fontSize: 10, color: "var(--text-3)", fontFamily: "var(--mono)", marginTop: 2, letterSpacing: "0.08em" }}>ASSESSMENT ENGINE</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 2, flex: 1 }}>
        {NAV_ITEMS.map(n => (
          <button key={n.id} className={`nav-item ${view === n.id ? "active" : ""}`} onClick={() => setView(n.id)}>
            <span className="nav-icon" style={{ fontSize: 15 }}>{n.icon}</span>
            {n.label}
          </button>
        ))}
      </div>
      <div style={{ padding: "16px 4px", borderTop: "1px solid var(--border-2)", fontSize: 11, color: "var(--text-3)" }}>
        <div style={{ fontFamily: "var(--mono)" }}>v1.0.0 · Phase B</div>
      </div>
    </div>
  );
}

// ── QUESTIONS VIEW ──
function QuestionsView({ toast }) {
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [rubricVersion, setRubricVersion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [genLoading, setGenLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [masterAnswer, setMasterAnswer] = useState(null);
  const [form, setForm] = useState({ subject: "", difficulty: "A_LEVEL", text: "", max_mark: 6 });
  const [maForm, setMaForm] = useState({ content: "" });

  useEffect(() => { loadQuestions(); }, []);

  async function loadQuestions() {
    setLoading(true);
    try { setQuestions(await api("/questions/")); } catch {}
    setLoading(false);
  }

  async function selectQuestion(q) {
    setSelected(q);
    setRubricVersion(null);
    setMasterAnswer(null);
    try {
      const rv = await api(`/rubrics/question/${q.id}/active`);
      setRubricVersion(rv);
    } catch {}
    try {
      const ma = await api(`/questions/${q.id}/master-answer`);
      setMasterAnswer(ma);
    } catch {}
  }

  async function createQuestion() {
    try {
      await api("/questions/", { method: "POST", body: JSON.stringify({ ...form, created_by: "teacher_01" }) });
      toast("Question created");
      setShowForm(false);
      setForm({ subject: "", difficulty: "A_LEVEL", text: "", max_mark: 6 });
      loadQuestions();
    } catch (e) { toast("Error: " + e.message); }
  }

  async function createMasterAnswer() {
    if (!selected) return;
    try {
      await api(`/questions/${selected.id}/master-answer`, {
        method: "POST",
        body: JSON.stringify({ content: maForm.content, created_by: "teacher_01" }),
      });
      toast("Master answer saved");
      const ma = await api(`/questions/${selected.id}/master-answer`);
      setMasterAnswer(ma);
    } catch (e) { toast("Error: " + e.message); }
  }

  async function generateRubrics() {
    if (!selected || !masterAnswer) return;
    setGenLoading(true);
    try {
      const rv = await api("/rubrics/generate", {
        method: "POST",
        body: JSON.stringify({ question_id: selected.id, master_answer_id: masterAnswer.id }),
      });
      setRubricVersion(rv);
      toast("Rubrics generated — review and approve");
    } catch (e) { toast("Error: " + e.message); }
    setGenLoading(false);
  }

  async function approveRubrics() {
    if (!rubricVersion) return;
    try {
      const rv = await api(`/rubrics/versions/${rubricVersion.id}/approve`, {
        method: "POST",
        body: JSON.stringify({ approved_by: "teacher_01" }),
      });
      setRubricVersion(rv);
      toast("Rubrics approved ✓");
    } catch (e) { toast("Error: " + e.message); }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 20, height: "100%" }}>
      {/* Question list */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <span style={{ fontSize: 11, fontWeight: 500, color: "var(--text-3)", textTransform: "uppercase", letterSpacing: "0.08em" }}>Questions ({questions.length})</span>
          <button className="btn-teal" style={{ padding: "5px 10px", fontSize: 11 }} onClick={() => setShowForm(s => !s)}>+ New</button>
        </div>

        {showForm && (
          <div className="card" style={{ marginBottom: 12 }}>
            <div style={{ fontWeight: 500, marginBottom: 12, fontSize: 13 }}>New question</div>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <input placeholder="Subject" value={form.subject} onChange={e => setForm(f => ({ ...f, subject: e.target.value }))} />
              <input type="number" placeholder="Marks" value={form.max_mark} onChange={e => setForm(f => ({ ...f, max_mark: +e.target.value }))} style={{ width: 70 }} />
            </div>
            <select value={form.difficulty} onChange={e => setForm(f => ({ ...f, difficulty: e.target.value }))} style={{ marginBottom: 8 }}>
              {["GCSE","AS_LEVEL","A_LEVEL","UNDERGRADUATE","OTHER"].map(d => <option key={d} value={d}>{d.replace("_"," ")}</option>)}
            </select>
            <textarea placeholder="Question text" value={form.text} onChange={e => setForm(f => ({ ...f, text: e.target.value }))} rows={3} style={{ marginBottom: 8 }} />
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn-primary" style={{ fontSize: 12, padding: "6px 12px" }} onClick={createQuestion}>Create</button>
              <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 12px" }} onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </div>
        )}

        {loading && <div style={{ textAlign: "center", padding: 20 }}><Spinner /></div>}

        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {questions.map(q => (
            <div key={q.id} onClick={() => selectQuestion(q)}
              style={{ padding: "10px 12px", borderRadius: "var(--radius-sm)", cursor: "pointer", border: "1px solid", borderColor: selected?.id === q.id ? "var(--teal)" : "var(--border-2)", background: selected?.id === q.id ? "var(--teal-dim)" : "white", transition: "all 0.12s" }}>
              <div style={{ display: "flex", gap: 6, marginBottom: 4, alignItems: "center" }}>
                <span style={{ fontSize: 10, background: "var(--paper-2)", color: "var(--text-2)", padding: "1px 6px", borderRadius: 3, fontFamily: "var(--mono)" }}>{q.subject}</span>
                <span style={{ fontSize: 10, color: "var(--text-3)", fontFamily: "var(--mono)" }}>{q.max_mark}m</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text)", lineHeight: 1.4, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>{q.text}</div>
            </div>
          ))}
          {!loading && questions.length === 0 && (
            <div className="empty-state"><div className="empty-state-icon">📋</div><div className="empty-state-text">No questions yet</div></div>
          )}
        </div>
      </div>

      {/* Question detail */}
      <div>
        {!selected ? (
          <div className="empty-state" style={{ paddingTop: 100 }}>
            <div className="empty-state-icon">👈</div>
            <div className="empty-state-text">Select a question to manage its rubrics</div>
          </div>
        ) : (
          <>
            <div className="section-header">
              <div>
                <div className="page-title">{selected.subject}</div>
                <div className="page-subtitle">{selected.difficulty.replace("_"," ")} · {selected.max_mark} marks</div>
              </div>
              {rubricVersion?.status === "APPROVED" && <span style={{ fontSize: 11, background: "var(--green-dim)", color: "#0D7A5F", padding: "4px 10px", borderRadius: 4, fontFamily: "var(--mono)", fontWeight: 500 }}>RUBRICS APPROVED</span>}
            </div>

            <div className="card" style={{ marginBottom: 16 }}>
              <p style={{ fontSize: 14, fontWeight: 500, lineHeight: 1.6 }}>{selected.text}</p>
            </div>

            {/* Master answer */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 500, fontSize: 13, marginBottom: 8 }}>Master answer</div>
              {masterAnswer ? (
                <div className="card" style={{ fontSize: 13, color: "var(--text-2)", lineHeight: 1.7 }}>
                  {masterAnswer.content}
                  <div style={{ marginTop: 8, fontSize: 11, color: "var(--text-3)", fontFamily: "var(--mono)" }}>version {masterAnswer.version} · {masterAnswer.is_active ? "active" : "inactive"}</div>
                </div>
              ) : (
                <div className="card">
                  <textarea placeholder="Write the model answer here..." value={maForm.content} onChange={e => setMaForm({ content: e.target.value })} rows={4} style={{ marginBottom: 10 }} />
                  <button className="btn-primary" style={{ fontSize: 12 }} onClick={createMasterAnswer}>Save master answer</button>
                </div>
              )}
            </div>

            {/* Rubrics */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <div style={{ fontWeight: 500, fontSize: 13 }}>
                  Rubrics {rubricVersion ? `(${rubricVersion.rubrics.length})` : ""}
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  {masterAnswer && (
                    <button className="btn-secondary" style={{ fontSize: 12, display: "flex", alignItems: "center", gap: 6 }} onClick={generateRubrics} disabled={genLoading}>
                      {genLoading ? <><Spinner /> Generating…</> : "✨ Generate with AI"}
                    </button>
                  )}
                  {rubricVersion?.status === "DRAFT" && (
                    <button className="btn-teal" style={{ fontSize: 12 }} onClick={approveRubrics}>Approve all</button>
                  )}
                </div>
              </div>

              {rubricVersion ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {rubricVersion.rubrics.map((r, i) => (
                    <div key={r.id} className="card" style={{ padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                          <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--text-3)" }}>R{i + 1}</span>
                          <span style={{ fontWeight: 500, fontSize: 13 }}>{r.concept}</span>
                        </div>
                        <p style={{ fontSize: 12, color: "var(--text-2)", lineHeight: 1.5 }}>{r.description}</p>
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4, flexShrink: 0 }}>
                        <span style={{ fontFamily: "var(--mono)", fontSize: 11, background: "var(--green-dim)", color: "#0D7A5F", padding: "2px 7px", borderRadius: 3 }}>{r.weight}pt</span>
                        <span className={`label-badge label-${r.status === "APPROVED" ? "PRESENT" : "PARTIAL"}`}>{r.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{ padding: "40px 0" }}>
                  <div className="empty-state-icon">🎯</div>
                  <div className="empty-state-text">{masterAnswer ? "Click Generate to create rubrics with AI" : "Add a master answer first"}</div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ── SUBMIT VIEW ──
function SubmitView({ toast }) {
  const [questions, setQuestions] = useState([]);
  const [selectedQ, setSelectedQ] = useState("");
  const [form, setForm] = useState({ student_name: "", student_id: "", answer: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api("/questions/").then(qs => {
      setQuestions(qs);
      if (qs.length > 0) setSelectedQ(qs[0].id);
    }).catch(() => {});
  }, []);

  async function submit() {
    if (!selectedQ || !form.answer.trim() || !form.student_name.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await api(`/questions/${selectedQ}/submit`, {
        method: "POST",
        body: JSON.stringify(form),
      });
      setResult(res);
      toast("Evaluation complete");
    } catch (e) { toast("Error: " + e.message); }
    setLoading(false);
  }

  const q = questions.find(q => q.id === selectedQ);
  const pct = result ? result.percentage : 0;
  const scoreColor = pct >= 75 ? "#0D7A5F" : pct >= 50 ? "#92580A" : "#B91C2C";

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 24 }}>
      <div>
        <div className="section-header">
          <div>
            <div className="page-title">Student portal</div>
            <div className="page-subtitle">Submit an answer for AI-assisted marking</div>
          </div>
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={{ fontSize: 12, color: "var(--text-2)", display: "block", marginBottom: 6 }}>Question</label>
          <select value={selectedQ} onChange={e => { setSelectedQ(e.target.value); setResult(null); }}>
            {questions.map(q => <option key={q.id} value={q.id}>{q.subject} — {q.text.slice(0, 60)}…</option>)}
          </select>
        </div>

        {q && (
          <div className="card" style={{ marginBottom: 16, background: "var(--navy)", color: "white" }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <span style={{ fontSize: 10, background: "rgba(255,255,255,0.1)", padding: "2px 8px", borderRadius: 3, fontFamily: "var(--mono)" }}>{q.subject}</span>
              <span style={{ fontSize: 10, background: "rgba(0,194,168,0.2)", color: "var(--teal)", padding: "2px 8px", borderRadius: 3, fontFamily: "var(--mono)" }}>{q.max_mark} marks</span>
            </div>
            <p style={{ fontSize: 14, fontWeight: 500, lineHeight: 1.6 }}>{q.text}</p>
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-2)", display: "block", marginBottom: 6 }}>Student name</label>
            <input placeholder="Full name" value={form.student_name} onChange={e => setForm(f => ({ ...f, student_name: e.target.value }))} />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-2)", display: "block", marginBottom: 6 }}>Student ID (optional)</label>
            <input placeholder="e.g. STU001" value={form.student_id} onChange={e => setForm(f => ({ ...f, student_id: e.target.value }))} />
          </div>
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={{ fontSize: 12, color: "var(--text-2)", display: "block", marginBottom: 6 }}>Answer</label>
          <textarea placeholder="Write your answer here…" value={form.answer} onChange={e => setForm(f => ({ ...f, answer: e.target.value }))} rows={8} />
        </div>

        <button className="btn-teal" onClick={submit} disabled={loading || !form.answer.trim() || !form.student_name.trim()}>
          {loading ? <><Spinner /> Evaluating…</> : "Submit for marking →"}
        </button>

        {/* Results */}
        {result && (
          <div style={{ marginTop: 28 }}>
            {/* Score hero */}
            <div className="card" style={{ marginBottom: 16, background: "var(--navy)", color: "white", padding: "24px 28px" }}>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 20, marginBottom: 16 }}>
                <div>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 48, fontWeight: 500, lineHeight: 1, color: "var(--teal)" }}>
                    {result.score}
                    <span style={{ fontSize: 20, color: "rgba(255,255,255,0.4)", fontWeight: 400 }}>/{result.max_score}</span>
                  </div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>{result.percentage}%</div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ height: 8, background: "rgba(255,255,255,0.1)", borderRadius: 4, overflow: "hidden" }}>
                    <div style={{ width: `${pct}%`, height: "100%", background: "var(--teal)", borderRadius: 4, transition: "width 0.8s ease" }} />
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 13, lineHeight: 1.7, color: "rgba(255,255,255,0.8)" }}>{result.feedback}</div>
            </div>

            {/* Rubric breakdown */}
            <div style={{ fontWeight: 500, fontSize: 13, marginBottom: 10 }}>Rubric breakdown</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {result.evaluations.map((e, i) => (
                <div key={i} className="card" style={{ padding: "12px 16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: e.reasoning ? 8 : 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <LabelBadge label={e.final_label} />
                      <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--text-3)" }}>{e.score_awarded}pt</span>
                      <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--text-3)" }}>via {e.method}</span>
                    </div>
                    {e.flagged && <span style={{ fontSize: 10, color: "var(--amber)", fontFamily: "var(--mono)" }}>⚑ flagged</span>}
                  </div>
                  {e.reasoning && <p style={{ fontSize: 12, color: "var(--text-2)", lineHeight: 1.5 }}>{e.reasoning}</p>}
                  {e.confidence && <div style={{ marginTop: 6 }}><ConfBar value={e.confidence} color={e.final_label === "PRESENT" ? "var(--teal)" : e.final_label === "PARTIAL" ? "var(--amber)" : "var(--red)"} /></div>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Side panel */}
      <div>
        <div style={{ fontWeight: 500, fontSize: 13, marginBottom: 12, color: "var(--text-2)", textTransform: "uppercase", letterSpacing: "0.08em", fontSize: 11 }}>How it works</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {[
            ["07", "Preprocessing", "Answer cleaned and normalised"],
            ["08-09", "Evidence retrieval", "Relevant passages extracted per rubric"],
            ["10", "NLI classification", "Fast first-pass confidence scoring"],
            ["11", "LLM judge", "Claude evaluates when confidence < 85%"],
            ["14", "Mark allocation", "Weighted score calculated"],
            ["15", "Feedback", "Claude writes personalised feedback"],
          ].map(([step, title, desc]) => (
            <div key={step} style={{ display: "flex", gap: 10, padding: "10px 12px", background: "white", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-2)" }}>
              <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--teal)", fontWeight: 500, minWidth: 28 }}>{step}</span>
              <div>
                <div style={{ fontSize: 12, fontWeight: 500 }}>{title}</div>
                <div style={{ fontSize: 11, color: "var(--text-3)" }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── REVIEW VIEW ──
function ReviewView({ toast }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolving, setResolving] = useState(null);
  const [form, setForm] = useState({ reviewer: "teacher_01", override_label: "PRESENT", reviewer_note: "" });

  useEffect(() => { loadItems(); }, []);

  async function loadItems() {
    setLoading(true);
    try { setItems(await api("/review/")); } catch {}
    setLoading(false);
  }

  async function resolve(id) {
    try {
      await api(`/review/${id}/resolve`, { method: "POST", body: JSON.stringify(form) });
      toast("Review resolved");
      setResolving(null);
      loadItems();
    } catch (e) { toast("Error: " + e.message); }
  }

  const pending = items.filter(i => i.status === "PENDING");
  const resolved = items.filter(i => i.status === "RESOLVED");

  return (
    <div>
      <div className="section-header">
        <div>
          <div className="page-title">Review queue</div>
          <div className="page-subtitle">Human oversight for flagged evaluations</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 24 }}>
        {[["Pending", pending.length, "var(--amber)"], ["Resolved", resolved.length, "var(--teal)"], ["Total", items.length, "var(--text-3)"]].map(([label, n, color]) => (
          <div key={label} className="stat-card">
            <div className="stat-value" style={{ color }}>{n}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>

      {loading && <div style={{ textAlign: "center", padding: 40 }}><Spinner /></div>}

      {!loading && pending.length === 0 && (
        <div className="empty-state"><div className="empty-state-icon">✓</div><div className="empty-state-text">No pending reviews</div></div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {items.map(item => (
          <div key={item.id} className="card" style={{ borderLeft: `3px solid ${item.status === "RESOLVED" ? "var(--teal)" : "var(--amber)"}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
              <div>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6 }}>
                  <StatusBadge status={item.status} />
                  <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--amber)", background: "var(--amber-dim)", padding: "2px 7px", borderRadius: 3 }}>{item.reason.replace(/_/g," ")}</span>
                </div>
                <div style={{ fontSize: 11, fontFamily: "var(--mono)", color: "var(--text-3)" }}>
                  submission: {item.submission_id.slice(0,8)}… · eval: {item.evaluation_id.slice(0,8)}…
                </div>
                {item.status === "RESOLVED" && (
                  <div style={{ marginTop: 6, fontSize: 12, color: "var(--text-2)" }}>
                    Override: <LabelBadge label={item.override_label} /> by {item.reviewer}
                    {item.reviewer_note && <span style={{ color: "var(--text-3)" }}> — "{item.reviewer_note}"</span>}
                  </div>
                )}
              </div>
              {item.status === "PENDING" && (
                <button className="btn-secondary" style={{ fontSize: 12, flexShrink: 0 }} onClick={() => setResolving(resolving === item.id ? null : item.id)}>
                  {resolving === item.id ? "Cancel" : "Resolve"}
                </button>
              )}
            </div>

            {resolving === item.id && (
              <div style={{ marginTop: 14, padding: "14px", background: "var(--paper)", borderRadius: "var(--radius-sm)" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 10 }}>
                  <div>
                    <label style={{ fontSize: 11, color: "var(--text-2)", display: "block", marginBottom: 4 }}>Reviewer</label>
                    <input value={form.reviewer} onChange={e => setForm(f => ({ ...f, reviewer: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: "var(--text-2)", display: "block", marginBottom: 4 }}>Override label</label>
                    <select value={form.override_label} onChange={e => setForm(f => ({ ...f, override_label: e.target.value }))}>
                      {["PRESENT","PARTIAL","ABSENT","CONTRADICTORY"].map(l => <option key={l} value={l}>{l}</option>)}
                    </select>
                  </div>
                </div>
                <textarea placeholder="Reviewer note (optional)" value={form.reviewer_note} onChange={e => setForm(f => ({ ...f, reviewer_note: e.target.value }))} rows={2} style={{ marginBottom: 10 }} />
                <button className="btn-teal" style={{ fontSize: 12 }} onClick={() => resolve(item.id)}>Confirm resolution</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── ANALYTICS VIEW ──
function AnalyticsView() {
  const [questions, setQuestions] = useState([]);
  const [selectedQ, setSelectedQ] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api("/questions/").then(qs => {
      setQuestions(qs);
      if (qs.length > 0) setSelectedQ(qs[0].id);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedQ) return;
    setLoading(true);
    api(`/analytics/question/${selectedQ}`).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, [selectedQ]);

  const rubrics = data ? Object.entries(data.rubric_breakdown) : [];
  const maxCount = rubrics.length > 0 ? Math.max(...rubrics.map(([, v]) => Object.values(v).reduce((a, b) => a + b, 0))) : 1;

  return (
    <div>
      <div className="section-header">
        <div>
          <div className="page-title">Analytics</div>
          <div className="page-subtitle">Performance insights across submissions</div>
        </div>
        <select value={selectedQ} onChange={e => setSelectedQ(e.target.value)} style={{ width: 280 }}>
          {questions.map(q => <option key={q.id} value={q.id}>{q.subject} — {q.text.slice(0, 45)}…</option>)}
        </select>
      </div>

      {loading && <div style={{ textAlign: "center", padding: 60 }}><Spinner /></div>}

      {data && !loading && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
            {[
              ["Total submissions", data.total_submissions, "var(--teal)"],
              ["Average score", `${data.average_score}/${questions.find(q=>q.id===selectedQ)?.max_mark||6}`, "var(--navy)"],
              ["Top score", data.max_score_achieved, "var(--green)"],
              ["LLM escalation", `${data.llm_escalation_rate}%`, "var(--amber)"],
            ].map(([label, value, color]) => (
              <div key={label} className="stat-card">
                <div className="stat-value" style={{ color }}>{value}</div>
                <div className="stat-label">{label}</div>
              </div>
            ))}
          </div>

          <div className="card">
            <div style={{ fontWeight: 500, fontSize: 14, marginBottom: 4 }}>Rubric performance</div>
            <div style={{ fontSize: 12, color: "var(--text-3)", marginBottom: 20 }}>Label distribution per rubric across all submissions</div>

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {rubrics.map(([concept, counts]) => {
                const total = Object.values(counts).reduce((a, b) => a + b, 0);
                const absentRate = total > 0 ? Math.round((counts.ABSENT / total) * 100) : 0;
                return (
                  <div key={concept}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: absentRate > 30 ? 500 : 400, color: absentRate > 30 ? "var(--red)" : "var(--text)" }}>{concept}</span>
                      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        {absentRate > 30 && <span style={{ fontSize: 10, color: "var(--red)", fontFamily: "var(--mono)" }}>⚠ {absentRate}% absent</span>}
                        <span style={{ fontSize: 11, color: "var(--text-3)", fontFamily: "var(--mono)" }}>{total} submissions</span>
                      </div>
                    </div>
                    <div style={{ display: "flex", height: 8, borderRadius: 4, overflow: "hidden", gap: 1 }}>
                      {[["PRESENT","var(--teal)"],["PARTIAL","var(--amber)"],["ABSENT","var(--paper-2)"],["CONTRADICTORY","var(--red)"]].map(([label, color]) => (
                        counts[label] > 0 && <div key={label} style={{ width: `${(counts[label]/total)*100}%`, background: color, transition: "width 0.5s" }} title={`${label}: ${counts[label]}`} />
                      ))}
                    </div>
                    <div style={{ display: "flex", gap: 12, marginTop: 4 }}>
                      {[["PRESENT","var(--teal)"],["PARTIAL","var(--amber)"],["ABSENT","var(--text-3)"],["CONTRADICTORY","var(--red)"]].map(([label, color]) => (
                        counts[label] > 0 && (
                          <span key={label} style={{ fontSize: 10, color, fontFamily: "var(--mono)" }}>{label[0]}: {counts[label]}</span>
                        )
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ marginTop: 20, padding: "12px 16px", background: "var(--paper)", borderRadius: "var(--radius-sm)", fontSize: 12, color: "var(--text-2)", lineHeight: 1.6 }}>
              {rubrics.filter(([, v]) => {
                const total = Object.values(v).reduce((a, b) => a + b, 0);
                return total > 0 && (v.ABSENT / total) > 0.3;
              }).length > 0 ? (
                <>⚠ <strong>Flagged for review:</strong> {rubrics.filter(([, v]) => { const t = Object.values(v).reduce((a,b)=>a+b,0); return t>0 && (v.ABSENT/t)>0.3; }).map(([c]) => c).join(", ")} — high absent rate suggests students are missing this concept in class.</>
              ) : (
                <>✓ No rubrics with critically high absent rates. Average performance looks healthy.</>
              )}
            </div>
          </div>
        </>
      )}

      {!data && !loading && (
        <div className="empty-state"><div className="empty-state-icon">📊</div><div className="empty-state-text">No submissions yet for this question</div></div>
      )}
    </div>
  );
}

// ── APP ──
export default function App() {
  const [view, setView] = useState(VIEWS.SUBMIT);
  const [toastMsg, setToastMsg] = useState(null);

  function toast(msg) { setToastMsg(msg); }

  const views = {
    [VIEWS.QUESTIONS]: <QuestionsView toast={toast} />,
    [VIEWS.SUBMIT]: <SubmitView toast={toast} />,
    [VIEWS.REVIEW]: <ReviewView toast={toast} />,
    [VIEWS.ANALYTICS]: <AnalyticsView />,
  };

  return (
    <>
      <style>{css}</style>
      <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
        <Sidebar view={view} setView={setView} />
        <main style={{ flex: 1, overflow: "auto", padding: "24px 28px" }}>
          {views[view]}
        </main>
      </div>
      {toastMsg && <Toast msg={toastMsg} onClose={() => setToastMsg(null)} />}
    </>
  );
}
