// ── Sidebar toggle (mobile) ───────────────────────────────────────────────
function toggleSidebar() {
  const aside = document.querySelector('aside');
  const backdrop = document.getElementById('sidebar-backdrop');
  const open = aside.classList.toggle('open');
  backdrop.classList.toggle('show', open);
  setTimeout(() => window.dispatchEvent(new Event('resize')), 270);
}

// ── Sidebar collapse (desktop) ────────────────────────────────────────────
const TABS_NEED_SIDEBAR = new Set(['fig3','fig2b','fig4','fig_sf','fig_feed']);
const TABS_AUTO_COLLAPSE = new Set(['fig1','fig2a']);
let sidebarManualOverride = false;

function setSidebarCollapsed(collapsed) {
  const aside = document.querySelector('aside');
  const btn = document.getElementById('collapse-btn');
  aside.classList.toggle('collapsed', collapsed);
  btn.classList.toggle('is-collapsed', collapsed);
  btn.textContent = collapsed ? '▶' : '◀';
  setTimeout(() => window.dispatchEvent(new Event('resize')), 220);
}

function toggleSidebarCollapse() {
  const aside = document.querySelector('aside');
  const collapsed = !aside.classList.contains('collapsed');
  setSidebarCollapsed(collapsed);
  sidebarManualOverride = true;
}

// ═══════════════════════════════════════════════════════════════════════════
// CONTACT PAGE — Edit this section to update team info.
// photo: path to image file (e.g. '/contact/junsang.jpg'), or null for initials.
// ═══════════════════════════════════════════════════════════════════════════
const TEAM_DATA = [
  {
    name: 'Junsang Park',
    sid:  '2023-16582',
    email: 'justinp5454@gmail.com',
    role: 'Lead Developer',
    photo: null,
    initials: 'JP',
    gradient: 'linear-gradient(135deg, #1878a8 0%, #0f2744 100%)',
    bio: [
      'Undergraduate Student',
      'Department of Chemical and Biological Engineering',
      'Department of Computer Science and Engineering',
      'Seoul National University',
    ],
    links: [
      { label: 'LinkedIn', href: 'https://www.linkedin.com/in/junsang-park', external: true },
      { label: '⟨/⟩ GitHub', href: 'https://github.com/justinp54', external: true },
    ],
  },
  {
    name: 'Seong Lee',
    sid:  '2020-11063',
    email: 'andylee1208@snu.ac.kr',
    role: 'Developer',
    photo: null,
    initials: 'SL',
    gradient: 'linear-gradient(135deg, #5abade 0%, #1878a8 100%)',
    bio: [
      'Undergraduate Student',
      'Department of Chemical and Biological Engineering',
      'Seoul National University',
    ],
    links: [
      { label: 'CV', href: '/cv/seong-lee-cv.pdf', external: true },
      { label: 'LinkedIn', href: 'https://www.linkedin.com/in/seonglee-snu', external: true },
    ],
  },
];

function renderContactPane() {
  const el = document.getElementById('plot-contact');
  if (!el) return;
  const rows = TEAM_DATA.map(p => {
    const ext = l => (l.external || l.href.startsWith('http')) ? 'target="_blank" rel="noopener"' : '';
    const avatar = p.photo
      ? `<img class="team-photo" src="${p.photo}" alt="${p.name}"
            onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
         <div class="team-photo-fallback" style="background:${p.gradient};display:none">${p.initials}</div>`
      : `<div class="team-photo-fallback" style="background:${p.gradient}">${p.initials}</div>`;
    const links = p.links.map(l =>
      `<a class="team-link" href="${l.href}" ${ext(l)}>${l.label}</a>`).join('');
    return `
      <div class="team-row">
        <div class="team-avatar-wrap">${avatar}</div>
        <div class="team-info">
          <div class="team-name">${p.name}${p.role ? `<span class="team-role">${p.role}</span>` : ''}</div>
          <div class="team-meta">${p.email ? `<a class="team-email" href="mailto:${p.email}">${p.email}</a>` : p.sid}</div>
          ${p.bio ? `<div class="team-bio">${Array.isArray(p.bio) ? p.bio.map((line, i) => i === 0 ? `<span class="team-bio-role">${line}</span>` : line).join('<br>') : p.bio}</div>` : ''}
        </div>
        <div class="team-actions">${links}</div>
      </div>`;
  }).join('');
  el.innerHTML = `
    <div class="contact-content">
      <div class="contact-header">
        <img src="/images/snu_ui.png" alt="Seoul National University" class="contact-emblem">
        <div class="contact-kicker">SNU CBE · CBPL-kit</div>
        <h1 class="contact-title">Made by</h1>
        <p class="contact-sub"><a href="https://cbe.snu.ac.kr/cbeEng/main/main.do" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;text-underline-offset:2px">Department of Chemical and Biological Engineering</a>, Seoul National University,<br>
          Seoul 08826, Republic of Korea<br>
          Developed in Spring 2026</p>
        <p class="contact-tagline">Built CBPL-kit to make LLE data analysis more accessible for lab students.</p>
      </div>
      <div class="team-rows">${rows}</div>
      <div class="contact-submit">
        <div class="contact-submit-text">
          <div class="contact-submit-title">Contribute a System</div>
          <div class="contact-submit-desc">Have a new LLE system? Submit a YAML file and we'll review it for inclusion in CBPL-kit.</div>
        </div>
        <a class="contact-submit-btn"
           href="https://github.com/justinp54/CBPL-kit/issues/new?title=New+System+Submission&labels=system"
           target="_blank" rel="noopener">Submit via GitHub →</a>
      </div>
      <div class="contact-footer">
        <a href="https://github.com/justinp54/CBPL-kit" target="_blank" rel="noopener" class="contact-gh-link">⟨/⟩ View on GitHub</a>
        &nbsp;·&nbsp; cbpl-kit.vercel.app
      </div>
    </div>`;
}

// ── State ─────────────────────────────────────────────────────────────────
const FIELDS = ['V_R0','V_E1','V_RN','flow_solvent','flow_feed'];
let pyodide   = null;
let pyReady   = false;
let cache     = {};
let rendered  = {};
let activeTab = 'guide';
let computing = false;
let _lbls = { solute:{name:'Propionic Acid', abbr:'PA'}, carrier:{name:'n-Bromopropane', abbr:'BP'}, solvent:{name:'Water', abbr:'W'} };

function syncDil(id, src) {
  const num = document.getElementById('dil-' + id);
  const sld = document.getElementById('s-dil-' + id);
  if (src === 'num') sld.value = num.value;
  else num.value = sld.value;
}

// ── Progress bar helper ────────────────────────────────────────────────────
function setProgress(pct, label) {
  document.getElementById('progress-bar').style.transform = `scaleX(${pct / 100})`;
  document.getElementById('progress-label').textContent = label;
}

// ── Pyodide initialisation ─────────────────────────────────────────────────
async function initPyodide() {
  try {
    setProgress(5, 'Loading Python runtime (Pyodide)…');
    pyodide = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/' });

    setProgress(30, 'Installing numpy, scipy & pyyaml…');
    await pyodide.loadPackage(['numpy', 'scipy', 'pyyaml']);

    setProgress(55, 'Installing plotly…');
    await pyodide.loadPackage('micropip');
    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install('plotly')
    `);

    setProgress(75, 'Fetching experiment modules…');
    const moduleFiles = [
      'exp06/config.py',
      'exp06/ternary.py',
      'exp06/equilibrium.py',
      'exp06/conjugate.py',
      'exp06/hunter_nash.py',
      'exp06/lever_rule.py',
      'exp06/plot_util.py',
      'exp06/correlation.py',
    ];

    pyodide.runPython(`
      import os, sys
      os.makedirs('/cbpl/systems', exist_ok=True)
      if '/cbpl' not in sys.path: sys.path.insert(0, '/cbpl')
    `);

    // Fetch default system YAML and write to Pyodide FS (needed by config.py)
    const sysResp = await fetch('/systems/nbp_pa_water.yaml');
    if (!sysResp.ok) throw new Error(`Failed to fetch system YAML: ${sysResp.status}`);
    pyodide.FS.writeFile('/cbpl/systems/nbp_pa_water.yaml', await sysResp.text());

    const _v = Date.now();
    for (const path of moduleFiles) {
      const resp = await fetch('/' + path + '?v=' + _v, {cache: 'no-store'});
      if (!resp.ok) throw new Error(`Failed to fetch ${path}: ${resp.status}`);
      const code = await resp.text();
      pyodide.FS.writeFile('/cbpl/' + path.split('/').pop(), code);
    }

    setProgress(90, 'Importing modules…');
    await pyodide.runPythonAsync(`
      import config
      from ternary import comp_to_xy, xy_to_comp
      from equilibrium import EquilibriumSystem
      from conjugate import ConjugateCurve
      from hunter_nash import HunterNashSolver
      from lever_rule import find_M_and_P, mixing_point, find_E1_prime
      import plot_util

      # Build equilibrium system once (literature data — never changes)
      _system    = EquilibriumSystem()
      _conjugate = ConjugateCurve(_system)
    `);

    setProgress(100, 'Ready!');
    pyReady = true;

    // Auto-render system figures (no titration data needed)
    await renderSystemFigs();

    // Hide init overlay; only show empty state on extraction tabs
    setTimeout(() => {
      document.getElementById('init-overlay').classList.add('hide');
      if (!['guide','system','fig1','fig2a','contact'].includes(activeTab) && Object.keys(cache).length === 0) {
        document.getElementById('empty').style.display = 'flex';
      }
    }, 400);

    // Enable UI
    const btn = document.getElementById('calc-btn');
    btn.disabled = false;
    document.getElementById('calc-icon').textContent = '⚗';
    document.getElementById('calc-label').textContent = 'Calculate';
    FIELDS.forEach(f => {
      document.getElementById(f).disabled = false;
      document.getElementById('s-' + f).disabled = false;
    });

  } catch (err) {
    setProgress(100, '⚠ ' + err.message);
    document.getElementById('progress-bar').style.background = '#dc2626';
    console.error(err);
  }
}

// ── Auto-render system figures (Equilibrium + Conjugate) ──────────────────
async function renderSystemFigs() {
  try {
    const json = await pyodide.runPythonAsync(`
import json
_sf = {}
_sf['fig1']  = plot_util.fig_ternary_equilibrium(_system).to_json()
_sf['fig2a'] = plot_util.fig_conjugate_curve(_system, _conjugate).to_json()

# Extract tie line full compositions from pre-computed tie_coords
from ternary import xy_to_comp as _xyc
_tl_comps = []
_clamp = lambda v: round(max(0.0, v), 2)
for (_ptL, _ptR) in _system.tie_coords:
    _cL = _xyc(*_ptL)
    _cR = _xyc(*_ptR)
    _tl_comps.append({'left': [_clamp(_cL[0]), _clamp(_cL[1]), _clamp(_cL[2])],
                      'right': [_clamp(_cR[0]), _clamp(_cR[1]), _clamp(_cR[2])]})
_sf['tie_comps'] = _tl_comps

from correlation import compute_correlations
_corr = compute_correlations(_system)
_sf['fig_corr_ot']      = plot_util.fig_correlation(_corr['ot'],      'ot').to_json()
_sf['fig_corr_hand']    = plot_util.fig_correlation(_corr['hand'],    'hand').to_json()
_sf['fig_corr_bachman'] = plot_util.fig_correlation(_corr['bachman'], 'bachman').to_json()
_sf['fig_selectivity']  = plot_util.fig_selectivity(_corr['selectivity']).to_json()
_sf['corr_stats']       = _corr
_sf['sel_stats']        = _corr['selectivity']

from correlation import compute_plait_loglog as _compute_plait
_plait_data = _compute_plait(_system)
_sf['fig_plait']   = plot_util.fig_plait_loglog(_plait_data).to_json()
_sf['plait_stats'] = _plait_data['plait_comp']

_pp = _xyc(*_conjugate.pt_plait)
_sf['conj_plait'] = {'carrier': round(max(0.0, _pp[1]), 2), 'solute': round(max(0.0, _pp[0]), 2), 'solvent': round(max(0.0, _pp[2]), 2)}

json.dumps(_sf)
`);
    const figs = JSON.parse(json);
    for (const [k, v] of Object.entries(figs)) {
      if (k === 'tie_comps') continue;
      if (k === 'corr_stats') continue;
      if (k === 'sel_stats') continue;
      if (k === 'plait_stats') continue;
      if (k === 'conj_plait') continue;
      cache[k] = JSON.parse(v);
      rendered[k] = false;
    }
    if (activeTab === 'fig1' || activeTab === 'fig2a') {
      document.getElementById('empty').style.display = 'none';
      renderFig(activeTab);
    }
    if (figs.tie_comps) populateTieLineTable(figs.tie_comps);
    if (figs.corr_stats) populateCorrelationPanel(figs.corr_stats);
    if (figs.sel_stats) populateSelectivityPanel(figs.sel_stats);
    if (figs.plait_stats !== undefined) populatePlaitPanel(figs.plait_stats, figs.conj_plait);
    // Re-render panel charts with correct width after DOM paints
    requestAnimationFrame(() => {
      if (activeTab === 'fig1') { _renderCorrChart(_corrActive); _renderSelectivityChart(); }
      else if (activeTab === 'fig2a') { _renderPlaitChart(); _addLoglogPlaitToTernary(); }
    });
  } catch (e) { console.error('System fig render:', e); }
}

function populateTieLineTable(comps) {
  const thead = document.querySelector('#tieline-table thead');
  const tbody = document.querySelector('#tieline-table tbody');
  // Column order matches paper: carrier(w1x), solute(w2x), solvent(w3x) per phase
  // left[]  = solvent-rich: [0]=solute(w23), [1]=carrier(w13), [2]=solvent(w33)
  // right[] = carrier-rich: [0]=solute(w21), [1]=carrier(w11), [2]=solvent(w31)
  const ca = _lbls.carrier.abbr, so = _lbls.solute.abbr, sv = _lbls.solvent.abbr;
  const th = (abbr, sub) => `<th>${abbr}<span class="col-sub">${sub}</span></th>`;
  thead.innerHTML = `
    <tr>
      <th>#</th>
      <th colspan="3">Solvent-rich phase</th>
      <th colspan="3">Carrier-rich phase</th>
      <th>D₁</th><th>D₂</th><th>S</th>
    </tr>
    <tr>
      <th></th>
      ${th(ca,'100w₁₃')}${th(so,'100w₂₃')}${th(sv,'100w₃₃')}
      ${th(ca,'100w₁₁')}${th(so,'100w₂₁')}${th(sv,'100w₃₁')}
      <th></th><th></th><th></th>
    </tr>`;
  const eps = 1e-9;
  tbody.innerHTML = comps.map((t, i) => {
    const d1 = Math.max(eps, t.left[1]) / Math.max(eps, t.right[1]);   // w13/w11
    const d2 = Math.max(eps, t.left[0]) / Math.max(eps, t.right[0]);   // w23/w21
    const sv = d2 / d1;
    return `<tr>
      <td>${i+1}</td>
      <td>${t.left[1]}</td><td>${t.left[0]}</td><td>${t.left[2]}</td>
      <td>${t.right[1]}</td><td>${t.right[0]}</td><td>${t.right[2]}</td>
      <td>${d1.toFixed(3)}</td><td>${d2.toFixed(3)}</td><td>${sv.toFixed(3)}</td>
    </tr>`;
  }).join('');
  document.getElementById('panel-fig1').classList.add('has-data');
}

// ── Correlation panel ──────────────────────────────────────────────────────
let _corrStats = null;
let _corrActive = 'ot';

function populateCorrelationPanel(stats) {
  _corrStats = stats;
  _renderCorrChart(_corrActive);
  _updateCorrStats(_corrActive);
}

function switchCorrTab(model) {
  _corrActive = model;
  document.querySelectorAll('.corr-tab').forEach(b => {
    const sel = b.dataset.model === model;
    b.classList.toggle('active', sel);
    b.setAttribute('aria-selected', sel);
  });
  _renderCorrChart(model);
  _updateCorrStats(model);
}

function _renderCorrChart(model) {
  const key = 'fig_corr_' + model;
  const el = document.getElementById('corr-chart');
  if (!el || !cache[key]) return;
  const w = el.offsetWidth || 350;
  const layout = { ...cache[key].layout, width: w, autosize: false };
  Plotly.react(el, cache[key].data, layout, { displayModeBar: false });
}

const _CORR_FORMULA = {
  ot:      { label: 'Othmer-Tobias', latex: '\\ln\\dfrac{1-w_{11}}{w_{11}} = a + b\\cdot\\ln\\dfrac{1-w_{33}}{w_{33}}' },
  hand:    { label: 'Hand',          latex: '\\ln\\dfrac{w_{21}}{w_{11}} = a + b\\cdot\\ln\\dfrac{w_{23}}{w_{33}}' },
  bachman: { label: 'Bachman',       latex: 'w_{11} = a + b\\cdot\\dfrac{w_{11}}{w_{33}}' },
};

const _SEL_LATEX = 'D_1 = \\dfrac{w_{13}}{w_{11}},\\quad D_2 = \\dfrac{w_{23}}{w_{21}},\\quad S = \\dfrac{D_2}{D_1}';

function _katex(latex, display = true) {
  if (window.katex) return katex.renderToString(latex, { displayMode: display, throwOnError: false });
  return `<code>${latex}</code>`;
}

function _updateCorrStats(model) {
  const el = document.getElementById('corr-stats');
  if (!el || !_corrStats) return;
  const d = _corrStats[model];
  const f = _CORR_FORMULA[model];
  el.innerHTML = `
    <div class="fml-label">${f.label} Model</div>
    <div class="fml-eq">${_katex(f.latex)}</div>
    <div class="fml-params">a = ${d.a} &nbsp;&nbsp; b = ${d.b} &nbsp;&nbsp; <span class="fml-r2">R² = ${d.r2}</span></div>`;
}

// ── Selectivity panel ─────────────────────────────────────────────────────
let _selStats = null;
let _plaitStats = null;
let _conjPlaitStats = null;

function populateSelectivityPanel(stats) {
  _selStats = stats;
  _renderSelectivityChart();
  const el = document.getElementById('selectivity-stats');
  if (el) el.innerHTML = `
    <div class="fml-label">Separation Factor</div>
    <div class="fml-eq">${_katex(_SEL_LATEX)}</div>`;
}

function _renderSelectivityChart() {
  const el = document.getElementById('selectivity-chart');
  if (!el || !cache['fig_selectivity']) return;
  const w = el.offsetWidth || 350;
  const layout = { ...cache['fig_selectivity'].layout, width: w, autosize: false };
  Plotly.react(el, cache['fig_selectivity'].data, layout, { displayModeBar: false });
}

// ── Plait point panel ─────────────────────────────────────────────────────
function _renderPlaitChart() {
  const el = document.getElementById('plait-chart');
  if (!el || !cache['fig_plait']) return;
  const w = el.offsetWidth || 350;
  const layout = { ...cache['fig_plait'].layout, width: w, height: w, autosize: false };
  Plotly.react(el, cache['fig_plait'].data, layout, { displayModeBar: false });
}

let _plaitOverlayAdded = false;

function _addLoglogPlaitToTernary() {
  const el = document.getElementById('chart-fig2a');
  if (!el || !_plaitStats || _plaitOverlayAdded || !rendered['fig2a']) return;
  const x = _plaitStats.carrier + 0.5 * _plaitStats.solute;
  const y = Math.sqrt(3) / 2 * _plaitStats.solute;
  Plotly.addTraces(el, {
    type: 'scatter', x: [x], y: [y],
    mode: 'markers',
    marker: { symbol: 'star', color: '#dc2626', size: 14,
              line: { color: 'white', width: 0.5 } },
    name: 'Plait pt. (Treybal)',
    showlegend: true,
    hovertemplate:
      `<b>Plait pt. (Treybal)</b><br>${_lbls.carrier.abbr}: ${_plaitStats.carrier}%  ${_lbls.solute.abbr}: ${_plaitStats.solute}%  ${_lbls.solvent.abbr}: ${_plaitStats.solvent}%<extra></extra>`,
  });
  _plaitOverlayAdded = true;
}

function populatePlaitPanel(treybalStats, conjStats) {
  _plaitStats = treybalStats;
  _conjPlaitStats = conjStats || null;
  _renderPlaitChart();
  const el = document.getElementById('plait-stats');
  if (!el) return;
  document.getElementById('panel-fig2a')?.classList.add('has-data');

  const c = _lbls.carrier.abbr, s = _lbls.solute.abbr, sv = _lbls.solvent.abbr;
  const tdH = `style="text-align:right;padding:3px 5px 5px;font-size:9.5px;font-weight:600;color:#1878a8"`;
  const tdN = `style="text-align:left;padding:3px 5px 5px;font-size:9.5px;font-weight:600;color:#1878a8"`;
  const td  = `style="text-align:right;padding:3px 4px;font-family:'JetBrains Mono',monospace;font-size:10px;font-variant-numeric:tabular-nums;border-bottom:1px solid #f0f1f3"`;
  const tdL = `style="text-align:left;padding:3px 4px;font-family:'IBM Plex Sans',sans-serif;font-weight:600;font-size:10.5px;color:var(--text);border-bottom:1px solid #f0f1f3;white-space:nowrap"`;

  const treybalRow = treybalStats
    ? `<tr><td ${tdL}><span style="color:#dc2626;margin-right:5px">★</span>Treybal</td><td ${td}>${treybalStats.carrier}</td><td ${td}>${treybalStats.solute}</td><td ${td}>${treybalStats.solvent}</td></tr>`
    : `<tr><td colspan="4" style="text-align:center;padding:4px;color:var(--muted);font-size:10px">Treybal: not found in range</td></tr>`;

  const conjRow = conjStats
    ? `<tr><td ${tdL}><span style="color:darkorange;margin-right:5px">★</span>Conj. Curve</td><td ${td}>${conjStats.carrier}</td><td ${td}>${conjStats.solute}</td><td ${td}>${conjStats.solvent}</td></tr>`
    : '';

  el.innerHTML = `
    <div class="fml-label">Plait Point Comparison</div>
    <table style="width:100%;border-collapse:collapse;margin-top:6px">
      <thead><tr style="border-bottom:1.5px solid var(--border)">
        <th ${tdN}>Method</th>
        <th ${tdH}>${c}%</th>
        <th ${tdH}>${s}%</th>
        <th ${tdH}>${sv}%</th>
      </tr></thead>
      <tbody>${treybalRow}${conjRow}</tbody>
    </table>`;
}

// ── Input sync ─────────────────────────────────────────────────────────────
FIELDS.forEach(f => {
  const num = document.getElementById(f);
  const sld = document.getElementById('s-' + f);
  num.disabled = true;
  sld.disabled = true;

  sld.addEventListener('input', () => { num.value = sld.value; });
  num.addEventListener('input', () => { sld.value = num.value; });
  num.addEventListener('change', () => {
    let v = parseFloat(num.value);
    const lo = parseFloat(num.min), hi = parseFloat(num.max);
    if (isNaN(v)) v = parseFloat(num.defaultValue);
    v = Math.max(lo, Math.min(hi, v));
    num.value = v; sld.value = v;
  });
});

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && pyReady && !computing) calculate();
});

['R0','E1','Rn'].forEach(id => {
  document.getElementById('dil-' + id).addEventListener('input', () => syncDil(id, 'num'));
  document.getElementById('s-dil-' + id).addEventListener('input', () => syncDil(id, 'slider'));
});

// ── Core Python computation ────────────────────────────────────────────────
const PY_COMPUTE = `
import json
from config import RHO_BP, RHO_PA, RHO_W, MW_PA, FLOW_SOLVENT_ML_MIN, FLOW_FEED_ML_MIN

def _c(v, dil): return 0.05 * v * float(dil)
def _r(v):      return round(float(v), 2)
def _comp(t):   return {'wpa': _r(t[0]), 'wbp': _r(t[1]), 'ww': _r(t[2])}

# Use cached system & conjugate
system    = _system
conjugate = _conjugate

c_R0 = _c(config.V_R0, _dil_R0)
c_E1 = _c(config.V_E1, _dil_E1)
c_Rn = _c(config.V_RN, _dil_Rn)

denom  = c_R0 * MW_PA + RHO_BP * (1000.0 - c_R0 * MW_PA / RHO_PA)
wpa_R0 = c_R0 * MW_PA / denom * 100.0
wbp_R0 = 100.0 - wpa_R0
pt_R0  = comp_to_xy(wbp_R0, wpa_R0)

pt_E1, comp_E1, _ = system.find_curve_point_by_concentration(c_E1, left=True)
pt_Rn, comp_Rn, _ = system.find_curve_point_by_concentration(c_Rn, left=False)
pt_En1 = (0.0, 0.0)

pt_M, pt_P = find_M_and_P(pt_E1, pt_Rn, pt_En1, pt_R0)

solver = HunterNashSolver(system, conjugate, pt_P, pt_E1, pt_Rn)
steps, N_theory = solver.solve()

mass_En1   = config.FLOW_SOLVENT_ML_MIN * RHO_W
vol_per_g  = wpa_R0/100/RHO_PA + wbp_R0/100/RHO_BP
mass_R0_gm = config.FLOW_FEED_ML_MIN / vol_per_g

pt_Mp_exp  = mixing_point(pt_R0, pt_En1, mass_R0_gm, mass_En1)
pt_E1p_exp = find_E1_prime(pt_Rn, pt_Mp_exp, system.spline)
pp         = xy_to_comp(*conjugate.pt_plait)

def _build(key):
    if key == 'fig1':   return plot_util.fig_ternary_equilibrium(system).to_json()
    if key == 'fig2a':  return plot_util.fig_conjugate_curve(system, conjugate).to_json()
    if key == 'fig2b':  return plot_util.fig_interpolated_tie_lines(system, conjugate, steps, N_theory).to_json()
    if key == 'fig3':   return plot_util.fig_hunter_nash(system, steps, N_theory, pt_R0, pt_Rn, pt_E1, pt_En1, pt_P).to_json()
    if key == 'fig4':   return plot_util.fig_lever_rule(system, pt_R0, pt_Rn, pt_E1, pt_En1, pt_M, pt_Mp_exp, pt_E1p_exp, title='Lever Rule — Experimental Flow Ratio').to_json()
    if key == 'fig_sf': return plot_util.fig_lever_rule_interactive(system, pt_R0, pt_Rn, pt_E1, pt_En1, pt_M, n_steps=30).to_json()
    if key == 'fig_feed': return plot_util.fig_lever_rule_interactive_feed(system, pt_Rn, pt_E1, pt_En1, mass_R0=mass_R0_gm, mass_En1=mass_En1, pt_R0_actual=pt_R0, n_steps=30).to_json()
    return ''

# Save state for real-time explorer sliders
import builtins as _b
_b._ept_R0    = pt_R0
_b._ept_Rn    = pt_Rn
_b._ept_E1    = pt_E1
_b._ept_En1   = pt_En1
_b._ept_M     = pt_M
_b._emass_R0  = mass_R0_gm
_b._emass_En1 = mass_En1
_b._esystem   = system
_b._econjugate = conjugate
_b._eready    = True

_req_keys = [k for k in list(_requested_keys) if k not in ('fig_sf', 'fig_feed')]
_figs = {k: _build(k) for k in _req_keys}

json.dumps({
    'N_theory': N_theory,
    'plait_point': _comp(pp),
    'stream_points': {
        'R0':  {'wpa': _r(wpa_R0), 'wbp': _r(wbp_R0), 'ww': 0.0},
        'E1':  _comp(comp_E1),
        'Rn':  _comp(comp_Rn),
        'En1': {'wpa': 0.0, 'wbp': 0.0, 'ww': 100.0},
    },
    'mass_flows': {'solvent_g_min': _r(mass_En1), 'feed_g_min': _r(mass_R0_gm)},
    'stages': [{'index': s.index, 'E': _comp(s.comp_E), 'R': _comp(s.comp_R)} for s in steps],
    'figures': _figs,
})
`;

// ── Real-time explorer Python snippets ────────────────────────────────────
const PY_SF = `
import json, builtins as _b
frac   = float(_sf_frac)
pt_Mp  = mixing_point(_b._ept_R0, _b._ept_En1, mass_A=1-frac, mass_B=frac)
pt_E1p = find_E1_prime(_b._ept_Rn, pt_Mp, _b._esystem.spline)
plot_util.fig_lever_rule(
    _b._esystem, _b._ept_R0, _b._ept_Rn, _b._ept_E1, _b._ept_En1,
    _b._ept_M, pt_Mp, pt_E1p,
    title=f"S:F  Solvent {frac*100:.0f}% : Feed {(1-frac)*100:.0f}%"
).to_json()
`;

const PY_FEED = `
import json, math, builtins as _b
wpa    = float(_feed_wpa)
wbp    = 100.0 - wpa
pt_R0h = (wbp + 0.5*wpa, math.sqrt(3)/2 * wpa)
pt_Mh, _ = find_M_and_P(_b._ept_E1, _b._ept_Rn, _b._ept_En1, pt_R0h)
pt_Mph = mixing_point(pt_R0h, _b._ept_En1, mass_A=_b._emass_R0, mass_B=_b._emass_En1)
pt_E1ph = find_E1_prime(_b._ept_Rn, pt_Mph, _b._esystem.spline)
plot_util.fig_lever_rule(
    _b._esystem, pt_R0h, _b._ept_Rn, _b._ept_E1, _b._ept_En1,
    pt_Mh, pt_Mph, pt_E1ph,
    title=f"Feed  PA {wpa:.1f} wt%",
    pt_R0_actual=_b._ept_R0
).to_json()
`;

let explorerReady = false;

async function computeExplorer(type) {
  if (!explorerReady) return;
  const el = document.getElementById('plot-fig_' + type);
  try {
    let figJson;
    if (type === 'sf') {
      pyodide.globals.set('_sf_frac', parseFloat(document.getElementById('sf-slider').value));
      figJson = await pyodide.runPythonAsync(PY_SF);
    } else {
      pyodide.globals.set('_feed_wpa', parseFloat(document.getElementById('feed-slider').value));
      figJson = await pyodide.runPythonAsync(PY_FEED);
    }
    const fig = JSON.parse(figJson);
    Plotly.react(el, fig.data, patchedLayout(fig.layout), PLOTLY_CFG);
  } catch (e) { console.error(e); }
}

// ── Explorer control sync (slider ↔ number input) ─────────────────────────
function updateSfLabels(frac) {
  document.getElementById('sf-slider').value  = frac;
  document.getElementById('sf-num').value     = (frac * 100).toFixed(0);
  document.getElementById('sf-feed-label').textContent = `Feed ${((1-frac)*100).toFixed(0)}%`;
}

function updateFeedLabels(wpa) {
  document.getElementById('feed-slider').value = wpa;
  document.getElementById('feed-num').value    = parseFloat(wpa).toFixed(1);
}

// S:F slider
document.getElementById('sf-slider').addEventListener('input', function() {
  updateSfLabels(parseFloat(this.value));
  computeExplorer('sf');
});

// S:F number input — clamp and sync
document.getElementById('sf-num').addEventListener('change', function() {
  let v = parseFloat(this.value);
  if (isNaN(v)) v = 70;
  v = Math.max(40, Math.min(97, v));
  updateSfLabels(v / 100);
  computeExplorer('sf');
});
document.getElementById('sf-num').addEventListener('input', function() {
  const v = parseFloat(this.value);
  if (!isNaN(v) && v >= 40 && v <= 97) {
    document.getElementById('sf-slider').value = v / 100;
    document.getElementById('sf-feed-label').textContent = `Feed ${(100-v).toFixed(0)}%`;
    computeExplorer('sf');
  }
});

// Feed slider
document.getElementById('feed-slider').addEventListener('input', function() {
  updateFeedLabels(parseFloat(this.value));
  computeExplorer('feed');
});

// Feed number input
document.getElementById('feed-num').addEventListener('change', function() {
  let v = parseFloat(this.value);
  if (isNaN(v)) v = 33;
  v = Math.max(10, Math.min(55, v));
  updateFeedLabels(v);
  computeExplorer('feed');
});
document.getElementById('feed-num').addEventListener('input', function() {
  const v = parseFloat(this.value);
  if (!isNaN(v) && v >= 10 && v <= 55) {
    document.getElementById('feed-slider').value = v;
    computeExplorer('feed');
  }
});

// ── Calculate ──────────────────────────────────────────────────────────────
async function calculate(requestedKeys) {
  if (!pyReady || computing) return;
  computing = true;

  document.getElementById('loading').classList.add('show');
  document.getElementById('empty').style.display = 'none';
  document.getElementById('error-box').classList.remove('show');

  // Which figures to compute
  const toFetch = requestedKeys || getDefaultKeys();
  const sf_frame   = getExplorerFrame('fig_sf');
  const feed_frame = getExplorerFrame('fig_feed');

  try {
    // Set config in Python
    FIELDS.forEach(f => {
      pyodide.globals.set('_' + f, parseFloat(document.getElementById(f).value));
    });
    await pyodide.runPythonAsync(`
      config.V_R0               = _V_R0
      config.V_E1               = _V_E1
      config.V_RN               = _V_RN
      config.FLOW_SOLVENT_ML_MIN = _flow_solvent
      config.FLOW_FEED_ML_MIN    = _flow_feed
    `);

    pyodide.globals.set('_dil_R0', parseInt(document.getElementById('dil-R0').value));
    pyodide.globals.set('_dil_E1', parseInt(document.getElementById('dil-E1').value));
    pyodide.globals.set('_dil_Rn', parseInt(document.getElementById('dil-Rn').value));
    pyodide.globals.set('_requested_keys', toFetch);
    const json = await pyodide.runPythonAsync(PY_COMPUTE);
    const data = JSON.parse(json);

    // Update cache
    for (const [k, v] of Object.entries(data.figures)) {
      cache[k] = JSON.parse(v);
      rendered[k] = false;
      if (k === 'fig2a') _plaitOverlayAdded = false;
    }

    renderFig(activeTab);
    showResults(data);
    explorerReady = true;

    // If currently on an explorer tab, recompute it with new inputs
    if (activeTab === 'fig_sf')   computeExplorer('sf');
    if (activeTab === 'fig_feed') computeExplorer('feed');

  } catch (err) {
    const box = document.getElementById('error-box');
    box.textContent = 'Calculation failed: check your input values. (' + err.message + ')';
    box.classList.add('show');
    document.getElementById('empty').style.display = 'flex';
    console.error(err);
  } finally {
    document.getElementById('loading').classList.remove('show');
    computing = false;
  }
}

function getDefaultKeys() {
  const keys = ['fig3'];
  if (cache['fig_sf']   || activeTab === 'fig_sf')   keys.push('fig_sf');
  if (cache['fig_feed'] || activeTab === 'fig_feed') keys.push('fig_feed');
  if (cache['fig1']  || activeTab === 'fig1')  keys.push('fig1');
  if (cache['fig2a'] || activeTab === 'fig2a') keys.push('fig2a');
  if (cache['fig2b'] || activeTab === 'fig2b') keys.push('fig2b');
  if (cache['fig4']  || activeTab === 'fig4')  keys.push('fig4');
  return keys;
}

// ── Plotly render ──────────────────────────────────────────────────────────
// Add breathing room so bottom of ternary diagram isn't clipped
function patchedLayout(layout) {
  const patched = { ...layout };
  const narrow = window.innerWidth < 768;
  if (patched.ternary) {
    // Always strip Python-fixed dimensions so Plotly sizes to its container at any viewport.
    delete patched.width;
    delete patched.height;
    patched.autosize = true;
    if (narrow) {
      patched.margin = { l: 8, r: 15, t: 30, b: 55 };
      // Shrink chart title font so it doesn't overflow
      if (patched.title) {
        const base = typeof patched.title === 'object' ? patched.title : { text: patched.title };
        patched.title = { ...base, font: { size: 10 } };
      }
      patched.legend = {
        x: 0.5, y: -0.04, xanchor: 'center', yanchor: 'top',
        orientation: 'h',
        bgcolor: 'rgba(255,255,255,0.9)',
        bordercolor: '#e2e8f0', borderwidth: 1,
        font: { size: 9 },
      };
      // axis mapping: aaxis=solute(PA), baxis=solvent(W), caxis=carrier(BP)
      const abbr = n => `${n} (wt%)`;
      patched.ternary = {
        ...patched.ternary,
        domain: { x: [0.04, 0.88], y: [0.14, 0.97] },
        aaxis: { ...patched.ternary.aaxis, title: { text: abbr(_lbls?.solute?.abbr  ?? 'Solute'),  font: { size: 9 } }, tickfont: { size: 8 } },
        baxis: { ...patched.ternary.baxis, title: { text: abbr(_lbls?.solvent?.abbr ?? 'Solvent'), font: { size: 9 } }, tickfont: { size: 8 } },
        caxis: { ...patched.ternary.caxis, title: { text: abbr(_lbls?.carrier?.abbr ?? 'Carrier'), font: { size: 9 } }, tickfont: { size: 8 } },
      };
    } else {
      patched.margin = { l: 40, r: 130, t: 40, b: 10 };
      patched.legend = {
        x: 1.02, y: 1, xanchor: 'left', yanchor: 'top',
        bgcolor: 'rgba(255,255,255,0.95)',
        bordercolor: '#e2e8f0', borderwidth: 1,
        font: { size: 11 },
      };
      patched.ternary = {
        ...patched.ternary,
        domain: { x: [0.10, 0.95], y: [0.23, 0.92] },
      };
    }
  } else {
    // Cartesian: strip Python-fixed dimensions same as ternary.
    delete patched.width;
    delete patched.height;
    patched.autosize = true;
    patched.margin = { l: 20, r: 20, t: 50, b: 40, ...(layout.margin || {}) };
  }
  return patched;
}

const PLOTLY_CFG = { responsive: true, scrollZoom: true };

function renderFig(key) {
  if (!cache[key] || rendered[key]) return;
  const el = document.getElementById('chart-' + key) || document.getElementById('plot-' + key);
  if (!el) return;
  document.getElementById('empty').style.display = 'none';
  const fig = cache[key];
  Plotly.newPlot(el, fig.data, patchedLayout(fig.layout), PLOTLY_CFG);
  if (fig.frames?.length) Plotly.addFrames(el, fig.frames);
  rendered[key] = true;
  requestAnimationFrame(() => Plotly.Plots.resize(el));
}

// ── Tab switching ──────────────────────────────────────────────────────────
function switchTab(key) {
  document.getElementById('plot-' + activeTab).classList.remove('active');
  document.getElementById('tab-'  + activeTab).classList.remove('active');
  document.getElementById('tab-'  + activeTab).setAttribute('aria-selected', 'false');
  activeTab = key;
  document.getElementById('plot-' + key).classList.add('active');
  document.getElementById('tab-'  + key).classList.add('active');
  document.getElementById('tab-'  + key).setAttribute('aria-selected', 'true');

  closeDataDrawer();
  _setDataTrigger(key === 'fig1' || key === 'fig2a',
    key === 'fig1' ? 'panel-fig1' : 'panel-fig2a');

  // Re-render all chart tabs on every tab switch so Plotly sizes to the current container.
  if (['fig1', 'fig2a', 'fig2b', 'fig3', 'fig4'].includes(key) && cache[key]) {
    requestAnimationFrame(() => {
      const _el = document.getElementById('chart-' + key) || document.getElementById('plot-' + key);
      if (_el?.data) Plotly.react(_el, cache[key].data, patchedLayout(cache[key].layout), PLOTLY_CFG);
    });
  }

  if (key === 'contact' || key === 'guide' || key === 'system') {
    document.getElementById('empty').style.display = 'none';
  }

  if (!sidebarManualOverride && window.innerWidth >= 1200) {
    const hasData = Object.keys(cache).length > 0;
    if (TABS_AUTO_COLLAPSE.has(key)) {
      setSidebarCollapsed(true);
    } else if (TABS_NEED_SIDEBAR.has(key)) {
      setSidebarCollapsed(false);
    } else if (hasData) {
      setSidebarCollapsed(true);
    }
  }
  sidebarManualOverride = false;

  const bar      = document.getElementById('explorer-bar');
  const sfBar    = document.getElementById('sf-bar');
  const feedBar  = document.getElementById('feed-bar');

  if (key === 'fig_sf') {
    bar.style.display     = 'flex';
    sfBar.style.display   = 'flex';
    feedBar.style.display = 'none';
    document.getElementById('plot-fig_sf').style.paddingTop = '52px';
    computeExplorer('sf');
  } else if (key === 'fig_feed') {
    bar.style.display     = 'flex';
    sfBar.style.display   = 'none';
    feedBar.style.display = 'flex';
    document.getElementById('plot-fig_feed').style.paddingTop = '52px';
    computeExplorer('feed');
  } else {
    bar.style.display = 'none';
    document.getElementById('plot-fig_sf').style.paddingTop   = '0';
    document.getElementById('plot-fig_feed').style.paddingTop = '0';
    if (key === 'guide')  { document.getElementById('empty').style.display = 'none'; loadGuide(); return; }
    if (key === 'system') { document.getElementById('empty').style.display = 'none'; loadSystemTab(); return; }
    if (cache[key]) {
      document.getElementById('empty').style.display = 'none';
      renderFig(key);
      if (key === 'fig1') requestAnimationFrame(() => { _renderCorrChart(_corrActive); _renderSelectivityChart(); });
      if (key === 'fig2a') requestAnimationFrame(() => { _renderPlaitChart(); _addLoglogPlaitToTernary(); });
    } else if (pyReady && cache['fig3']) {
      calculate([key]);
    } else if (pyReady && !TABS_AUTO_COLLAPSE.has(key)) {
      document.getElementById('empty').style.display = 'flex';
    }
  }
}

// ── Explorer slider helpers ────────────────────────────────────────────────
function getExplorerFrame(key) {
  try { return document.getElementById('plot-' + key)._fullLayout?.sliders?.[0]?.active ?? 0; }
  catch { return 0; }
}

function restoreExplorerFrame(key, frameIdx) {
  if (frameIdx <= 0 || !cache[key]?.frames?.[frameIdx]) return;
  setTimeout(() => {
    Plotly.animate(
      document.getElementById('plot-' + key),
      [cache[key].frames[frameIdx].name],
      { frame: { duration: 0, redraw: true }, mode: 'immediate' }
    ).catch(() => {});
  }, 80);
}

// ── Results panel ──────────────────────────────────────────────────────────
function updateTableHeaders() {
  const s = _lbls.solute.abbr, c = _lbls.carrier.abbr, sv = _lbls.solvent.abbr;
  document.getElementById('stream-thead').innerHTML =
    `<tr><th>Stream</th><th>${s}%</th><th>${c}%</th><th>${sv}%</th></tr>`;
  document.getElementById('stages-thead').innerHTML =
    `<tr><th>#</th><th></th><th>${s}%</th><th>${c}%</th><th>${sv}%</th></tr>`;
}
updateTableHeaders();

function showResults(data) {
  document.getElementById('n-val').textContent   = data.N_theory.toFixed(1);
  document.getElementById('badge-n').textContent = 'N=' + data.N_theory.toFixed(1);
  document.getElementById('n-sub').textContent   = '';

  const streams = [
    {name:'R₀',   cls:'R', d:data.stream_points.R0 },
    {name:'E₁',   cls:'E', d:data.stream_points.E1 },
    {name:'Rₙ',   cls:'R', d:data.stream_points.Rn },
    {name:'Eₙ₊₁', cls:'E', d:data.stream_points.En1},
  ];
  document.getElementById('stream-tbody').innerHTML = streams.map(s =>
    `<tr><td><span class="dot dot-${s.cls}"></span>${s.name}</td><td>${s.d.wpa}</td><td>${s.d.wbp}</td><td>${s.d.ww}</td></tr>`
  ).join('');

  document.getElementById('stages-tbody').innerHTML = data.stages.flatMap(s => [
    `<tr><td>${s.index}</td><td style="color:#f87171">E</td><td>${s.E.wpa}</td><td>${s.E.wbp}</td><td>${s.E.ww}</td></tr>`,
    `<tr><td></td><td style="color:#5abade">R</td><td>${s.R.wpa}</td><td>${s.R.wbp}</td><td>${s.R.ww}</td></tr>`,
  ]).join('');

  document.getElementById('flows-text').innerHTML =
    `<strong>Solvent</strong> ${data.mass_flows.solvent_g_min} g/min<br>` +
    `<strong>Feed &nbsp;&nbsp;&nbsp;</strong> ${data.mass_flows.feed_g_min} g/min`;

  document.getElementById('results-panel').classList.add('show');
}

function toggleStages() {
  const el  = document.getElementById('stages-detail');
  const btn = document.getElementById('stage-toggle');
  el.classList.toggle('show');
  btn.textContent = (el.classList.contains('show') ? '▼' : '▶') + ' Stage breakdown';
}

// ── System configuration ───────────────────────────────────────────────────
let defaultSystemYaml = '';
let systemTabLoaded   = false;
let systemList        = [];
let currentSystemFile = 'nbp_pa_water.yaml';

async function loadSystemTab() {
  if (systemTabLoaded) return;
  systemTabLoaded = true;
  try {
    const listResp = await fetch('/systems/index.json');
    if (listResp.ok) {
      systemList = await listResp.json();
      const sel = document.getElementById('sys-select');
      sel.innerHTML = systemList.map(s =>
        `<option value="${s.file}"${s.file === currentSystemFile ? ' selected' : ''}>${s.name} (${s.abbr})</option>`
      ).join('');
    }
  } catch (e) { console.error('System list:', e); }
  try {
    const resp = await fetch('/systems/' + currentSystemFile);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    defaultSystemYaml = await resp.text();
    document.getElementById('sys-yaml').value = defaultSystemYaml;
    populateFormFromYaml(defaultSystemYaml);
  } catch (e) {
    setSysMsg('Failed to load system YAML: ' + e.message, 'error');
  }
}

async function loadSystemFromSelect() {
  const sel = document.getElementById('sys-select');
  const file = sel.value;
  if (!file) return;
  try {
    const resp = await fetch('/systems/' + file);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const yaml = await resp.text();
    currentSystemFile = file;
    defaultSystemYaml = yaml;
    document.getElementById('sys-yaml').value = yaml;
    populateFormFromYaml(yaml);
    document.getElementById('sys-download').href = '/systems/' + file;
    document.getElementById('sys-download').download = file;
    setSysMsg('', '');
    applySystem();
  } catch (e) {
    setSysMsg('Failed to load: ' + e.message, 'error');
  }
}

function resetSystem() {
  document.getElementById('sys-yaml').value = defaultSystemYaml;
  populateFormFromYaml(defaultSystemYaml);
  setSysMsg('', '');
}

function populateFormFromYaml(yamlText) {
  try {
    const d = jsyaml.load(yamlText);
    const c = d.components || {};
    document.getElementById('sf-solvent-name').value = c.solvent?.name || '';
    document.getElementById('sf-solvent-abbr').value = c.solvent?.abbr || '';
    document.getElementById('sf-solute-name').value  = c.solute?.name || '';
    document.getElementById('sf-solute-abbr').value  = c.solute?.abbr || '';
    document.getElementById('sf-carrier-name').value = c.carrier?.name || '';
    document.getElementById('sf-carrier-abbr').value = c.carrier?.abbr || '';
    const p = d.properties || {};
    document.getElementById('sf-rho-solvent').value = p.rho_solvent || '';
    document.getElementById('sf-rho-solute').value  = p.rho_solute || '';
    document.getElementById('sf-rho-carrier').value = p.rho_carrier || '';
    document.getElementById('sf-mw-solute').value   = p.mw_solute || '';
    const eqTbody = document.getElementById('sf-equil-tbody');
    eqTbody.innerHTML = (d.equilibrium_data || []).map((row, i) =>
      `<tr><td>${i+1}</td>${row.map(v => `<td><input value="${v}" type="number" step="0.01" /></td>`).join('')}</tr>`
    ).join('');
    const tieTbody = document.getElementById('sf-tie-tbody');
    tieTbody.innerHTML = (d.tie_lines || []).map((row, i) =>
      `<tr><td>${i+1}</td>${row.map(v => `<td><input value="${v}" type="number" step="0.01" /></td>`).join('')}</tr>`
    ).join('');
  } catch (e) { console.error('Form populate:', e); }
}

function validateForm() {
  const errors = [];
  ['sf-solvent-name','sf-solute-name','sf-carrier-name'].forEach(id => {
    if (!document.getElementById(id).value.trim()) errors.push('Component name is empty.');
  });
  ['sf-rho-solvent','sf-rho-solute','sf-rho-carrier','sf-mw-solute'].forEach(id => {
    if (isNaN(parseFloat(document.getElementById(id).value))) errors.push(`Property "${id.replace('sf-','')}" is empty or invalid.`);
  });
  [...document.getElementById('sf-equil-tbody').rows].forEach((r, i) => {
    [...r.querySelectorAll('input')].forEach((inp, j) => {
      if (inp.value === '' || isNaN(parseFloat(inp.value)))
        errors.push(`Equilibrium row ${i+1}, column ${j+1}: empty or invalid value.`);
    });
  });
  [...document.getElementById('sf-tie-tbody').rows].forEach((r, i) => {
    [...r.querySelectorAll('input')].forEach((inp, j) => {
      if (inp.value === '' || isNaN(parseFloat(inp.value)))
        errors.push(`Tie line row ${i+1}, column ${j+1}: empty or invalid value.`);
    });
  });
  const eqRows = [...document.getElementById('sf-equil-tbody').rows];
  if (eqRows.length >= 2 && errors.length === 0) {
    const carrierVals = eqRows.map(r => parseFloat(r.querySelectorAll('input')[0].value));
    for (let i = 1; i < carrierVals.length; i++) {
      if (carrierVals[i] < carrierVals[i-1]) {
        errors.push('SORT:Equilibrium data is not sorted by increasing carrier%. Click "Sort" to fix.');
        break;
      }
    }
  }
  return errors;
}

function sortEquilData() {
  const tbody = document.getElementById('sf-equil-tbody');
  const rows = [...tbody.rows].map(r => {
    const inputs = r.querySelectorAll('input');
    return [parseFloat(inputs[0].value), parseFloat(inputs[1].value), parseFloat(inputs[2].value)];
  });
  rows.sort((a, b) => a[0] - b[0]);
  tbody.innerHTML = rows.map((row, i) =>
    `<tr><td>${i+1}</td>${row.map(v => `<td><input value="${v}" type="number" step="0.01" /></td>`).join('')}</tr>`
  ).join('');
  setSysMsg('Equilibrium data sorted by carrier%.', 'success');
}

function collectFormToYaml() {
  const obj = {
    name: document.getElementById('sf-solute-name').value + ' system',
    components: {
      solvent: { name: document.getElementById('sf-solvent-name').value, abbr: document.getElementById('sf-solvent-abbr').value },
      solute:  { name: document.getElementById('sf-solute-name').value,  abbr: document.getElementById('sf-solute-abbr').value },
      carrier: { name: document.getElementById('sf-carrier-name').value, abbr: document.getElementById('sf-carrier-abbr').value },
    },
    properties: {
      rho_solvent: parseFloat(document.getElementById('sf-rho-solvent').value),
      rho_solute:  parseFloat(document.getElementById('sf-rho-solute').value),
      rho_carrier: parseFloat(document.getElementById('sf-rho-carrier').value),
      mw_solute:   parseFloat(document.getElementById('sf-mw-solute').value),
    },
    equilibrium_data: [...document.getElementById('sf-equil-tbody').rows].map(r =>
      [...r.querySelectorAll('input')].map(inp => parseFloat(inp.value))
    ),
    tie_lines: [...document.getElementById('sf-tie-tbody').rows].map(r =>
      [...r.querySelectorAll('input')].map(inp => parseFloat(inp.value))
    ),
  };
  return jsyaml.dump(obj, { flowLevel: 2 });
}

function addEquilRow() {
  const tbody = document.getElementById('sf-equil-tbody');
  const n = tbody.rows.length + 1;
  tbody.insertAdjacentHTML('beforeend', `<tr><td>${n}</td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td></tr>`);
}
function removeEquilRow() {
  const tbody = document.getElementById('sf-equil-tbody');
  if (tbody.rows.length > 0) tbody.deleteRow(-1);
}
function addTieRow() {
  const tbody = document.getElementById('sf-tie-tbody');
  const n = tbody.rows.length + 1;
  tbody.insertAdjacentHTML('beforeend', `<tr><td>${n}</td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td></tr>`);
}
function removeTieRow() {
  const tbody = document.getElementById('sf-tie-tbody');
  if (tbody.rows.length > 0) tbody.deleteRow(-1);
}

function setSysMsg(text, type) {
  const el = document.getElementById('sys-msg');
  el.textContent = text;
  el.className   = 'sys-msg' + (type ? ' ' + type : '');
}

async function applySystem() {
  if (!pyReady) { setSysMsg('Still loading. Please wait for initialization to finish.', 'error'); return; }

  const advancedOpen = document.getElementById('sys-advanced').open;
  let yamlText;
  if (advancedOpen) {
    yamlText = document.getElementById('sys-yaml').value.trim();
  } else {
    const formErrors = validateForm();
    if (formErrors.length > 0) {
      const sortErr = formErrors.find(e => e.startsWith('SORT:'));
      if (sortErr) {
        const msg = document.getElementById('sys-msg');
        msg.className = 'sys-msg error';
        msg.innerHTML = sortErr.slice(5) + ' <button class="sys-row-btn" onclick="sortEquilData()" style="margin-left:6px">Sort</button>';
        return;
      }
      setSysMsg(formErrors[0], 'error');
      return;
    }
    yamlText = collectFormToYaml();
    document.getElementById('sys-yaml').value = yamlText;
  }
  setSysMsg('', '');

  let sysData;
  try {
    sysData = jsyaml.load(yamlText);
  } catch (e) {
    setSysMsg('YAML parse error: ' + e.message, 'error'); return;
  }

  if (!sysData?.equilibrium_data || !sysData?.tie_lines || !sysData?.properties) {
    setSysMsg('Missing required fields: equilibrium_data, tie_lines, or properties.', 'error'); return;
  }

  const p = sysData.properties;
  if ([p.rho_solvent, p.rho_solute, p.rho_carrier, p.mw_solute].some(v => !v)) {
    setSysMsg('properties must include rho_solvent, rho_solute, rho_carrier, mw_solute.', 'error'); return;
  }

  const eqData = sysData.equilibrium_data;
  if (eqData.length >= 2) {
    for (let i = 1; i < eqData.length; i++) {
      if (eqData[i][0] < eqData[i-1][0]) {
        setSysMsg('Equilibrium data is not sorted by increasing carrier%. Please sort before applying.', 'error');
        return;
      }
    }
  }

  setSysMsg('Building system…', '');
  try {
    pyodide.globals.set('_sys_equil',  pyodide.toPy(sysData.equilibrium_data));
    pyodide.globals.set('_sys_ties',   pyodide.toPy(sysData.tie_lines));
    pyodide.globals.set('_sys_rho_s',  p.rho_solvent);
    pyodide.globals.set('_sys_rho_o',  p.rho_solute);
    pyodide.globals.set('_sys_rho_d',  p.rho_carrier);
    pyodide.globals.set('_sys_mw_o',   p.mw_solute);
    const comps = sysData.components || {};
    pyodide.globals.set('_sys_labels', pyodide.toPy({
      solute:  { name: comps.solute?.name  || 'Solute',  abbr: comps.solute?.abbr  || 'S'  },
      solvent: { name: comps.solvent?.name || 'Solvent', abbr: comps.solvent?.abbr || 'Sv' },
      carrier: { name: comps.carrier?.name || 'Carrier', abbr: comps.carrier?.abbr || 'D'  },
    }));
    _lbls = {
      solute:  { name: comps.solute?.name  || 'Solute',  abbr: comps.solute?.abbr  || 'PA' },
      carrier: { name: comps.carrier?.name || 'Carrier', abbr: comps.carrier?.abbr || 'BP' },
      solvent: { name: comps.solvent?.name || 'Solvent', abbr: comps.solvent?.abbr || 'W'  },
    };
    updateTableHeaders();

    await pyodide.runPythonAsync(`
import numpy as np, builtins as _b, config as _cfg, equilibrium as _eq_mod
equil = np.array([[float(v) for v in row] for row in list(_sys_equil)])
ties  = [(float(row[0]), float(row[1])) for row in list(_sys_ties)]
# Update physical properties in both config and equilibrium module namespaces
# (equilibrium.py imports them at module load, so both need updating)
for _mod in (_cfg, _eq_mod):
    _mod.RHO_BP = float(_sys_rho_d)
    _mod.RHO_PA = float(_sys_rho_o)
    _mod.RHO_W  = float(_sys_rho_s)
    _mod.MW_PA  = float(_sys_mw_o)
_lbs = {k: dict(v) for k, v in dict(_sys_labels).items()}
_system    = EquilibriumSystem(equil_data=equil, tie_data=ties, labels=_lbs)
_conjugate = ConjugateCurve(_system)
_b._esystem    = _system
_b._econjugate = _conjugate
_b._eready     = False
`);

    cache = {}; rendered = {}; explorerReady = false;
    ['fig3','fig1','fig2a','fig2b','fig4','fig_sf','fig_feed',
     'fig_corr_ot','fig_corr_hand','fig_corr_bachman'].forEach(k => {
      const el = document.getElementById('chart-' + k) || document.getElementById('plot-' + k);
      if (el) { try { Plotly.purge(el); } catch(e) {} }
    });
    document.getElementById('panel-fig1')?.classList.remove('has-data');
    document.getElementById('panel-fig2a')?.classList.remove('has-data');
    const _ce = document.getElementById('corr-chart');
    if (_ce) { try { Plotly.purge(_ce); } catch(e) {} }
    const _se = document.getElementById('selectivity-chart');
    if (_se) { try { Plotly.purge(_se); } catch(e) {} }
    const _pe = document.getElementById('plait-chart');
    if (_pe) { try { Plotly.purge(_pe); } catch(e) {} }
    _corrStats = null;
    _corrActive = 'ot';
    _selStats = null;
    _plaitStats = null;
    _conjPlaitStats = null;
    _plaitOverlayAdded = false;
    const _ps = document.getElementById('plait-stats');
    if (_ps) _ps.innerHTML = '';
    document.querySelectorAll('.corr-tab').forEach(b => {
      const sel = b.dataset.model === 'ot';
      b.classList.toggle('active', sel);
      b.setAttribute('aria-selected', sel);
    });
    document.getElementById('results-panel').classList.remove('show');
    if (activeTab !== 'guide' && activeTab !== 'system') {
      document.getElementById('empty').style.display = 'flex';
    }
    await renderSystemFigs();
    setSysMsg('System applied. Press Calculate to run extraction analysis.', 'success');

  } catch (e) {
    setSysMsg('Failed to build system: ' + e.message, 'error');
  }
}

// ── Guide ──────────────────────────────────────────────────────────────────
let guideLoaded = false;
async function loadGuide() {
  if (guideLoaded) return;
  const el = document.getElementById('plot-guide');
  el.innerHTML = '<div style="padding:20px;color:var(--muted);font-size:13px">Loading guide…</div>';
  try {
    const resp = await fetch('/docs/guide.md');
    if (!resp.ok) throw new Error('guide.md not found');
    const md = await resp.text();
    el.innerHTML = `<div class="guide-content">${marked.parse(md)}</div>`;
    guideLoaded = true;
  } catch (e) {
    el.innerHTML = `<div style="padding:20px;color:#dc2626;font-size:13px">Failed to load guide: ${e.message}</div>`;
  }
}

// ── Data drawer (mobile/tablet) ────────────────────────────────────────────
let _drawerPanel = null;

function openDataDrawer() {
  if (!_drawerPanel) return;
  document.getElementById(_drawerPanel).classList.add('drawer-open');
  document.getElementById('drawer-backdrop').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeDataDrawer() {
  if (_drawerPanel) document.getElementById(_drawerPanel)?.classList.remove('drawer-open');
  document.getElementById('drawer-backdrop')?.classList.remove('show');
  document.body.style.overflow = '';
}

function _setDataTrigger(show, panelId) {
  _drawerPanel = show ? panelId : null;
  const btn = document.getElementById('data-trigger-btn');
  if (!btn) return;
  if (show && window.innerWidth < 1200) {
    btn.style.display = 'flex';
  } else {
    btn.style.display = 'none';
  }
}

// ── Panel chart resize on window resize / orientation change ─────────────
let _resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(_resizeTimer);
  _resizeTimer = setTimeout(() => {
    if (window.innerWidth >= 1200) {
      // Going to desktop: close drawer, hide trigger, re-render panel charts
      closeDataDrawer();
      const btn = document.getElementById('data-trigger-btn');
      if (btn) btn.style.display = 'none';
      if (activeTab === 'fig1' && _corrStats) { _renderCorrChart(_corrActive); _renderSelectivityChart(); }
      else if (activeTab === 'fig2a' && _plaitStats) { _renderPlaitChart(); }
    } else {
      // Mobile/tablet: re-render active ternary chart on orientation/resize.
      // (Desktop relies on responsive:true ResizeObserver; switchTab() handles switch-back-after-resize.)
      const ternaryTabs = ['fig1', 'fig2a', 'fig2b', 'fig3', 'fig4'];
      if (ternaryTabs.includes(activeTab) && cache[activeTab]) {
        const chartEl = document.getElementById('chart-' + activeTab) || document.getElementById('plot-' + activeTab);
        if (chartEl?.data) Plotly.react(chartEl, cache[activeTab].data, patchedLayout(cache[activeTab].layout), PLOTLY_CFG);
      }
      // Keep trigger visible for the right tabs on mobile/tablet
      if (_drawerPanel) {
        const btn = document.getElementById('data-trigger-btn');
        if (btn) btn.style.display = 'flex';
      }
    }
  }, 150);
});

// ── Boot ───────────────────────────────────────────────────────────────────
renderContactPane();
loadGuide();
initPyodide();
// Show trigger button if starting on a data-panel tab on mobile
_setDataTrigger(activeTab === 'fig1' || activeTab === 'fig2a',
  activeTab === 'fig1' ? 'panel-fig1' : 'panel-fig2a');
