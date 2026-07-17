// ── Sidebar toggle (mobile) ───────────────────────────────────────────────
function toggleSidebar() {
  const aside = document.querySelector('aside');
  const backdrop = document.getElementById('sidebar-backdrop');
  const open = aside.classList.toggle('open');
  backdrop.classList.toggle('show', open);
  // Sidebar is position:fixed on tablet/phone — doesn't affect layout, no resize needed.
  if (window.innerWidth >= 1200) setTimeout(() => window.dispatchEvent(new Event('resize')), 270);
}

// ── Sidebar collapse (desktop) ────────────────────────────────────────────
const TABS_NEED_SIDEBAR = new Set(['fig3','fig2b','fig4','fig_sf','fig_feed']);
const TABS_AUTO_COLLAPSE = new Set(['fig1','fig2a']);
// Tabs with a right-side data-panel drawer (see _setDataTrigger)
const DATA_PANEL_TABS = { fig1: 'panel-fig1', fig2a: 'panel-fig2a', fig3: 'panel-fig3', fig_sf: 'panel-fig_sf', fig_feed: 'panel-fig_feed' };
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
    email: 'justinp54@snu.ac.kr',
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
      'Microfluidics and Coating Process Laboratory (MCPL)',
      'Department of Chemical and Biological Engineering',
      'Seoul National University',
    ],
    links: [
      { label: 'LinkedIn', href: 'https://www.linkedin.com/in/seonglee-snu', external: true },
    ],
  },
  {
    name: 'Youn-Woo Lee',
    email: 'ywlee@snu.ac.kr',
    role: 'Advisor',
    photo: '/images/youn-woo-lee.png',
    initials: 'YL',
    gradient: 'linear-gradient(135deg, #0f2744 0%, #071a2e 100%)',
    bio: [
      'Professor Emeritus',
      'Supercritical Fluid Process Laboratory (SFPL)',
      'Department of Chemical and Biological Engineering',
      'Institute of Chemical Process',
      'Seoul National University',
    ],
    links: [],
  },
];

// Both submission CTAs below point at the two devs directly (not the
// advisor) — mailto has no server, so whoever's address is here just gets
// the email; easy to change later if that should move to a shared inbox.
const DEV_EMAILS = 'justinp54@snu.ac.kr,andylee1208@snu.ac.kr';
function _mailtoHref(subject, bodyLines) {
  return `mailto:${DEV_EMAILS}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(bodyLines.join('\n'))}`;
}

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
        <p class="contact-sub">Department of Chemical and Biological Engineering<br>
          Seoul National University<br>
          Seoul 08826, Republic of Korea</p>
        <p class="contact-tagline">Built CBPL-kit to make LLE data analysis more accessible for lab students.</p>
        <p class="contact-sub" style="color:var(--text)">Developed in Spring 2026 | Last updated in July 2026</p>
      </div>
      <div class="team-rows">${rows}</div>
      <div class="contact-submit">
        <div class="contact-submit-text">
          <div class="contact-submit-title">Contribute a System</div>
          <div class="contact-submit-desc">Have a new LLE system? Submit a YAML file and we'll review it for inclusion in CBPL-kit.</div>
        </div>
        <div class="contact-submit-actions">
          <a class="contact-submit-btn"
             href="https://github.com/justinp54/CBPL-kit/issues/new?template=system-submission.yml"
             target="_blank" rel="noopener">Submit via GitHub →</a>
          <a class="contact-submit-secondary" href="${_mailtoHref('New System Submission - CBPL-kit', [
            'System name: ',
            'Components (carrier/solute/solvent): ',
            'Data source/citation: ',
            '',
            '(Please attach your YAML file to this email)',
          ])}">No GitHub? Email us instead →</a>
        </div>
      </div>
      <div class="contact-submit">
        <div class="contact-submit-text">
          <div class="contact-submit-title">Report a Bug or Feedback</div>
          <div class="contact-submit-desc">Found something that doesn't work, or have a suggestion? Let us know.</div>
        </div>
        <div class="contact-submit-actions">
          <a class="contact-submit-btn"
             href="https://github.com/justinp54/CBPL-kit/issues/new?title=Bug+Report&labels=bug"
             target="_blank" rel="noopener">Report on GitHub →</a>
          <a class="contact-submit-secondary" href="${_mailtoHref('Bug Report / Feedback - CBPL-kit', [
            'System used: ',
            'What happened: ',
            'What you expected: ',
            '',
            '(Please attach a screenshot if you have one)',
          ])}">No GitHub? Email us instead →</a>
        </div>
      </div>
      <div class="contact-footer">
        <a href="https://github.com/justinp54/CBPL-kit" target="_blank" rel="noopener" class="contact-gh-link">⟨/⟩ View on GitHub</a>
        &nbsp;·&nbsp; cbpl-kit.vercel.app
      </div>
    </div>`;
}

// ── State ─────────────────────────────────────────────────────────────────
const FIELDS = ['V_R0','V_E1','V_RN','flow_solvent','flow_feed','c_naoh','v_aliquot'];
let pyodide   = null;
let pyReady   = false;
let cache     = {};
let rendered  = {};
let activeTab = 'guide';
let computing = false;
let _lbls = { solute:{name:'Propionic Acid', abbr:'PA'}, carrier:{name:'n-Bromopropane', abbr:'BP'}, solvent:{name:'Water', abbr:'W'} };

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
      'exp06/validate_system.py',
    ];

    pyodide.runPython(`
      import os, sys
      os.makedirs('/cbpl/systems', exist_ok=True)
      if '/cbpl' not in sys.path: sys.path.insert(0, '/cbpl')
    `);

    // Fetch default system YAML and write to Pyodide FS (needed by config.py)
    const sysResp = await fetch('/systems/bp_pa_w_snu_cbe.yaml', { cache: 'no-store' });
    if (!sysResp.ok) throw new Error(`Failed to fetch system YAML: ${sysResp.status}`);
    pyodide.FS.writeFile('/cbpl/systems/bp_pa_w_snu_cbe.yaml', await sysResp.text());

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
      from lever_rule import find_M_and_P, mixing_point, find_E1_prime, find_smin_over_f, find_smax_over_f, find_feed_bounds
      import plot_util

      # Build equilibrium system once (literature data — never changes)
      _system    = EquilibriumSystem()
      _conjugate = ConjugateCurve(_system)
    `);

    setProgress(100, 'Ready!');
    pyReady = true;

    // Auto-render system figures (no titration data needed).
    // Non-fatal here: a figure failure must not block the rest of init
    // (overlay hide, button enable) — the error surfaces on the System tab.
    await renderSystemFigs().catch(e => {
      console.error('Initial system figs:', e);
      setSysMsg('Default system figures failed to render: ' + pyErrMsg(e), 'error');
    });

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
    document.getElementById('calc-label').textContent = 'Calculate';
    FIELDS.forEach(f => {
      document.getElementById(f).disabled = false;
    });
    document.getElementById('export-btn').disabled = false;

  } catch (err) {
    setProgress(100, '⚠ ' + pyErrMsg(err));
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

# Two conjugate-curve constructions (which two triangle sides the
# auxiliary lines are drawn parallel to). _conjugate (diagonal) stays the
# one used everywhere else in the app (Hunter-Nash, etc.) — 'horizontal'
# only feeds the compare toggle on this tab.
_conj_h = ConjugateCurve(_system, method='horizontal')
_conj_methods = {'diagonal': _conjugate, 'horizontal': _conj_h}
for _mname, _conj in _conj_methods.items():
    _sf['fig2a_' + _mname] = plot_util.fig_conjugate_curve(_system, _conj).to_json()
_sf['fig2a'] = _sf['fig2a_diagonal']

# Extract tie line full compositions from pre-computed tie_coords.
# Keep full precision here; rounding is a display-only concern handled in JS.
# D/S are NOT computed here — they come from compute_correlations below, so
# the whole app has a single source of truth for the ratios.
from ternary import xy_to_comp as _xyc
_tl_comps = []
_pos = lambda v: max(0.0, v)   # clamp tiny numerical negatives only
for (_ptL, _ptR) in _system.tie_coords:
    _cL = _xyc(*_ptL)
    _cR = _xyc(*_ptR)
    _tl_comps.append({'left': [_pos(_cL[0]), _pos(_cL[1]), _pos(_cL[2])],
                      'right': [_pos(_cR[0]), _pos(_cR[1]), _pos(_cR[2])]})
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

_conj_plait_by_method = {}
for _mname, _conj in _conj_methods.items():
    _pp = _xyc(*_conj.pt_plait)
    # Full precision on purpose — rounded once at display (toFixed) in _renderPlaitTable.
    _conj_plait_by_method[_mname] = {'carrier': max(0.0, _pp[1]), 'solute': max(0.0, _pp[0]), 'solvent': max(0.0, _pp[2])}
_sf['conj_plait_by_method'] = _conj_plait_by_method
_sf['conj_plait'] = _conj_plait_by_method['diagonal']
_sf['conj_horizontal_side'] = _conj_h.horizontal_side

json.dumps(_sf)
`);
    const figs = JSON.parse(json);
    for (const [k, v] of Object.entries(figs)) {
      if (k === 'tie_comps') continue;
      if (k === 'corr_stats') continue;
      if (k === 'sel_stats') continue;
      if (k === 'plait_stats') continue;
      if (k === 'conj_plait') continue;
      if (k === 'conj_plait_by_method') continue;
      if (k === 'conj_horizontal_side') continue;
      cache[k] = JSON.parse(v);
      rendered[k] = false;
    }
    // Populate before rendering: renderFig('fig2a') draws the Treybal star
    // from _plaitStats, which populatePlaitPanel is what sets.
    if (figs.plait_stats !== undefined) populatePlaitPanel(figs.plait_stats, figs.conj_plait_by_method);
    if (activeTab === 'fig1' || activeTab === 'fig2a') {
      document.getElementById('empty').style.display = 'none';
      renderFig(activeTab);
    }
    if (figs.tie_comps) populateTieLineTable(figs.tie_comps, figs.sel_stats);
    if (figs.corr_stats) populateCorrelationPanel(figs.corr_stats);
    if (figs.sel_stats) populateSelectivityPanel(figs.sel_stats);
    // Re-render panel charts with correct width after DOM paints
    requestAnimationFrame(() => {
      if (activeTab === 'fig1') { _renderCorrChart(_corrActive); _renderSelectivityChart(); }
      else if (activeTab === 'fig2a') { _renderPlaitChart(); }
    });
  } catch (e) { console.error('System fig render:', e); throw e; }
}

function populateTieLineTable(comps, sel) {
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
      <th>D<sub>1</sub></th><th>D<sub>2</sub></th><th>S</th>
    </tr>
    <tr>
      <th></th>
      ${th(ca,'100w<sub>13</sub>')}${th(so,'100w<sub>23</sub>')}${th(sv,'100w<sub>33</sub>')}
      ${th(ca,'100w<sub>11</sub>')}${th(so,'100w<sub>21</sub>')}${th(sv,'100w<sub>31</sub>')}
      <th></th><th></th><th></th>
    </tr>`;
  // D₁, D₂, S come straight from compute_correlations (the same full-precision
  // values the selectivity chart uses) — the table only rounds for display and
  // never recomputes the ratios from the rounded compositions in the cells.
  // Display precision by significant figures: compositions 2 dp; D₁ 4 dp (its
  // values are small, so 3 dp would collapse distinct rows to 0.056); D₂ 3 dp
  // and S 2 dp (both ~4 sig figs — 3 dp on S would over-state the precision).
  const fComp = v => Number(v).toFixed(2);
  const fD1   = v => (v == null ? '' : Number(v).toFixed(4));
  const fD2   = v => (v == null ? '' : Number(v).toFixed(3));
  const fS    = v => (v == null ? '' : Number(v).toFixed(2));
  tbody.innerHTML = comps.map((t, i) => `<tr>
      <td>${i+1}</td>
      <td>${fComp(t.left[1])}</td><td>${fComp(t.left[0])}</td><td>${fComp(t.left[2])}</td>
      <td>${fComp(t.right[1])}</td><td>${fComp(t.right[0])}</td><td>${fComp(t.right[2])}</td>
      <td>${fD1(sel?.d1?.[i])}</td><td>${fD2(sel?.d2?.[i])}</td><td>${fS(sel?.s?.[i])}</td>
    </tr>`).join('');
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
  return Plotly.react(el, cache[key].data, layout, { displayModeBar: false });
}

const _CORR_FORMULA = {
  ot:      { label: 'Othmer-Tobias', latex: '\\ln\\dfrac{1-w_{33}}{w_{33}} = a + b\\cdot\\ln\\dfrac{1-w_{11}}{w_{11}}' },
  hand:    { label: 'Hand',          latex: '\\ln\\dfrac{w_{23}}{w_{33}} = a + b\\cdot\\ln\\dfrac{w_{21}}{w_{11}}' },
  bachman: { label: 'Bachman',       latex: 'w_{33} = a + b\\cdot\\dfrac{w_{33}}{w_{11}}' },
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
    <div class="fml-label">${f.label} Correlation</div>
    <div class="fml-eq">${_katex(f.latex)}</div>
    <div class="fml-params">a = ${d.a} &nbsp;&nbsp; b = ${d.b} &nbsp;&nbsp; <span class="fml-r2">R² = ${d.r2}</span></div>`;
}

// ── Selectivity panel ─────────────────────────────────────────────────────
let _selStats = null;
let _plaitStats = null;
let _conjPlaitByMethod = null;
let _conjMethod = 'diagonal';
const CONJ_METHOD_LABELS = {
  diagonal: 'Diagonal', horizontal: 'Horizontal',
};

function populateSelectivityPanel(stats) {
  _selStats = stats;
  _renderSelectivityChart();
  const el = document.getElementById('selectivity-stats');
  if (el) el.innerHTML = `
    <div class="fml-label">Distribution Coefficient &amp; Selectivity</div>
    <div class="fml-eq">${_katex(_SEL_LATEX)}</div>`;
}

function _renderSelectivityChart() {
  const el = document.getElementById('selectivity-chart');
  if (!el || !cache['fig_selectivity']) return;
  const w = el.offsetWidth || 350;
  const layout = { ...cache['fig_selectivity'].layout, width: w, autosize: false };
  return Plotly.react(el, cache['fig_selectivity'].data, layout, { displayModeBar: false });
}

// ── Plait point panel ─────────────────────────────────────────────────────
function _renderPlaitChart() {
  const el = document.getElementById('plait-chart');
  if (!el || !cache['fig_plait']) return;
  const w = el.offsetWidth || 350;
  const layout = { ...cache['fig_plait'].layout, width: w, height: w, autosize: false };
  return Plotly.react(el, cache['fig_plait'].data, layout, { displayModeBar: false });
}

// Shared by the on-screen render (see _figData) and the offscreen export
// render, so the star marker never has to be kept in sync by hand in two places.
function _plaitStarTrace() {
  const x = _plaitStats.carrier + 0.5 * _plaitStats.solute;
  const y = Math.sqrt(3) / 2 * _plaitStats.solute;
  return {
    type: 'scatter', x: [x], y: [y],
    mode: 'markers',
    marker: { symbol: 'star', color: '#dc2626', size: 14,
              line: { color: 'white', width: 0.5 } },
    name: 'Plait pt. (Treybal)',
    showlegend: true,
    hovertemplate:
      `<b>Plait pt. (Treybal)</b><br>${_lbls.carrier.abbr}: ${_plaitStats.carrier.toFixed(1)}%  ${_lbls.solute.abbr}: ${_plaitStats.solute.toFixed(1)}%  ${_lbls.solvent.abbr}: ${_plaitStats.solvent.toFixed(1)}%<extra></extra>`,
  };
}

// Trace list to render for a cached figure. The Treybal star is an overlay the
// app adds on top of what Python built for fig2a, so it is appended here at
// render time.
//
// EVERY path that draws chart-fig2a must go through this — there are four
// (renderFig, switchConjugateMethod, switchTab's resize re-render, and the
// mobile resize handler), and any one of them passing cache.fig2a.data raw
// silently strips the star back off whatever the others just drew.
//
// The star must also never be pushed into cache[key].data itself (e.g. via
// Plotly.addTraces): Plotly keeps the array we hand it as gd.data, so mutating
// it leaves a star behind in the cache and stacks up another on every re-render.
function _figData(key) {
  const fig = cache[key];
  if (!fig) return [];
  if (key === 'fig2a' && _plaitStats) return [...fig.data, _plaitStarTrace()];
  return fig.data;
}

function populatePlaitPanel(treybalStats, conjPlaitByMethod) {
  _plaitStats = treybalStats;
  _conjPlaitByMethod = conjPlaitByMethod || null;
  _renderPlaitChart();
  document.getElementById('panel-fig2a')?.classList.add('has-data');
  _renderPlaitTable();
}

function _renderPlaitTable() {
  const el = document.getElementById('plait-stats');
  if (!el) return;

  const c = _lbls.carrier.abbr, s = _lbls.solute.abbr, sv = _lbls.solvent.abbr;
  const f1 = v => Number(v).toFixed(1);   // display/export: 1 decimal place (computation stays full precision)
  const tdH = `style="text-align:right;padding:3px 5px 5px;font-size:9.5px;font-weight:600;color:#1878a8"`;
  const tdN = `style="text-align:left;padding:3px 5px 5px;font-size:9.5px;font-weight:600;color:#1878a8"`;
  const td  = (active) => `style="text-align:right;padding:3px 4px;font-family:'JetBrains Mono',monospace;font-size:10px;font-variant-numeric:tabular-nums;border-bottom:1px solid #f0f1f3${active ? ';background:var(--blue-lt)' : ''}"`;
  const tdL = (active) => `style="text-align:left;padding:3px 4px;font-family:'IBM Plex Sans',sans-serif;font-weight:600;font-size:10.5px;color:var(--text);border-bottom:1px solid #f0f1f3;white-space:nowrap${active ? ';background:var(--blue-lt)' : ''}"`;

  const treybalRow = _plaitStats
    ? `<tr><td ${tdL(false)}><span style="color:#dc2626;margin-right:5px">★</span>Treybal</td><td ${td(false)}>${f1(_plaitStats.carrier)}</td><td ${td(false)}>${f1(_plaitStats.solute)}</td><td ${td(false)}>${f1(_plaitStats.solvent)}</td></tr>`
    : `<tr><td colspan="4" style="text-align:center;padding:4px;color:var(--muted);font-size:10px">Treybal: not found in range</td></tr>`;

  const conjRows = _conjPlaitByMethod
    ? Object.entries(CONJ_METHOD_LABELS).map(([m, label]) => {
        const st = _conjPlaitByMethod[m];
        if (!st) return '';
        const active = m === _conjMethod;
        return `<tr><td ${tdL(active)}><span style="color:darkorange;margin-right:5px">★</span>Conj. Curve — ${label}</td><td ${td(active)}>${f1(st.carrier)}</td><td ${td(active)}>${f1(st.solute)}</td><td ${td(active)}>${f1(st.solvent)}</td></tr>`;
      }).join('')
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
      <tbody>${treybalRow}${conjRows}</tbody>
    </table>`;
}

function switchConjugateMethod(method) {
  if (method === _conjMethod || !cache['fig2a_' + method]) return;
  _conjMethod = method;
  cache.fig2a = cache['fig2a_' + method];

  document.querySelectorAll('.conj-method-tab').forEach(b => {
    const sel = b.dataset.method === method;
    b.classList.toggle('active', sel);
    b.setAttribute('aria-selected', sel);
  });

  const el = document.getElementById('chart-fig2a');
  if (el && rendered.fig2a) {
    Plotly.react(el, _figData('fig2a'), patchedLayout(cache.fig2a.layout), PLOTLY_CFG);
  }
  _renderPlaitTable();
}

// ── Input sync ─────────────────────────────────────────────────────────────
FIELDS.forEach(f => {
  const num = document.getElementById(f);
  num.disabled = true;

  num.addEventListener('change', () => {
    let v = parseFloat(num.value);
    const lo = parseFloat(num.min), hi = parseFloat(num.max);
    if (isNaN(v)) v = parseFloat(num.defaultValue);
    v = Math.max(lo, Math.min(hi, v));
    num.value = v;
  });
});

document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && pyReady && !computing) calculate();
});

// Titration formula box — rendered on window load because katex.min.js is
// deferred and executes after this classic script.
const _TITR_LATEX = 'C_{\\mathrm{solute}} = \\dfrac{C_{\\mathrm{NaOH}} \\cdot V_{\\mathrm{NaOH}} \\cdot f}{V_{\\mathrm{aliquot}}}';
window.addEventListener('load', () => {
  document.getElementById('titr-formula-eq').innerHTML = _katex(_TITR_LATEX);
});

// ── Core Python computation ────────────────────────────────────────────────
const PY_COMPUTE = `
import json, math
from config import RHO_BP, RHO_PA, RHO_W, MW_PA, FLOW_SOLVENT_ML_MIN, FLOW_FEED_ML_MIN

def _r(v):      return round(float(v), 2)
def _comp(t):   return {'wpa': _r(t[0]), 'wbp': _r(t[1]), 'ww': _r(t[2])}

# Use cached system & conjugate
system    = _system
conjugate = _conjugate

c_R0 = config.conc_from_titration(config.V_R0, _f_R0)
c_E1 = config.conc_from_titration(config.V_E1, _f_E1)
c_Rn = config.conc_from_titration(config.V_RN, _f_Rn)

denom  = c_R0 * MW_PA + RHO_BP * (1000.0 - c_R0 * MW_PA / RHO_PA)
wpa_R0 = c_R0 * MW_PA / denom * 100.0
wbp_R0 = 100.0 - wpa_R0
pt_R0  = comp_to_xy(wbp_R0, wpa_R0)

pt_E1, comp_E1, _ = system.find_curve_point_by_concentration(c_E1, left=True)
pt_Rn, comp_Rn, _ = system.find_curve_point_by_concentration(c_Rn, left=False)
pt_En1 = (0.0, 0.0)

pt_M, pt_P = find_M_and_P(pt_E1, pt_Rn, pt_En1, pt_R0)

# S:F Explorer slider bounds — the solvent-ratio range within which this
# system can actually be extracted (S_min: below this the cascade needs
# infinite stages; S_max: above this M leaves the two-phase region
# entirely). Falls back to the old fixed 0.40-0.97 span if either can't
# be found (e.g. a solutropic system — see find_smin_over_f's docstring).
_sf_frac_min = find_smin_over_f(system, pt_R0, pt_Rn, pt_En1, conjugate)
_sf_frac_max = find_smax_over_f(system, pt_R0, pt_En1)
sf_frac_min = round(_sf_frac_min, 4) if _sf_frac_min is not None else 0.40
sf_frac_max = round(_sf_frac_max, 4) if _sf_frac_max is not None else 0.97

solver = HunterNashSolver(system, conjugate, pt_P, pt_E1, pt_Rn)
steps, N_theory = solver.solve()

mass_En1   = config.FLOW_SOLVENT_ML_MIN * RHO_W
vol_per_g  = wpa_R0/100/RHO_PA + wbp_R0/100/RHO_BP
mass_R0_gm = config.FLOW_FEED_ML_MIN / vol_per_g

pt_Mp_exp  = mixing_point(pt_R0, pt_En1, mass_R0_gm, mass_En1)
pt_E1p_exp = find_E1_prime(pt_Rn, pt_Mp_exp, system.spline)
pp         = xy_to_comp(*conjugate.pt_plait)

# Stages-needed trend as S:F falls toward S_min — only genuinely-computed
# points (see stage_count_trend's docstring), so only built when a real
# S_min was found.
fig_sf_trend = None
if _sf_frac_min is not None and _sf_frac_max is not None:
    _fig_sf_trend = plot_util.fig_sf_stage_trend(system, conjugate, pt_R0, pt_Rn, pt_En1, _sf_frac_min, _sf_frac_max)
    fig_sf_trend = _fig_sf_trend.to_json() if _fig_sf_trend is not None else None

# Raw (un-fallback'd) S_min/S_max, for the reference cards — sf_frac_min/max
# above always have a value (falls back to 0.40/0.97 for the slider), which
# would misrepresent "no clear limit found" as a real number if used here.
sf_min_found = round(_sf_frac_min, 4) if _sf_frac_min is not None else None
sf_max_found = round(_sf_frac_max, 4) if _sf_frac_max is not None else None

# Feed Explorer slider bounds — the feasible feed-composition span for
# this system and these flows, probed outward from the experimental feed
# (see lever_rule.find_feed_bounds). No named textbook limit exists here
# (unlike S_min/S_max), so this is presented only as the slider's range.
# Falls back to the legacy fixed 10-55 span if the probe fails. Rounded
# inward to the slider's 0.5 step so the endpoints stay feasible.
_feed_bounds = find_feed_bounds(system, pt_Rn, pt_En1, mass_R0_gm, mass_En1, wpa_R0)
if _feed_bounds is not None:
    feed_wpa_lo = math.ceil(_feed_bounds[0] * 2) / 2
    feed_wpa_hi = math.floor(_feed_bounds[1] * 2) / 2
else:
    feed_wpa_lo, feed_wpa_hi = 10.0, 55.0

# Stages-needed trend over the Feed Explorer's slider range — E1 is
# recomputed per wpa via mass balance (mass_R0_gm/mass_En1), matching
# fig_lever_rule_interactive_feed's own construction, not held at its
# real fixed value. See feed_stage_count_trend's docstring for why
# there's no named limit line and why the shape isn't necessarily
# monotonic.
_fig_feed_trend = plot_util.fig_feed_stage_trend(system, conjugate, pt_Rn, pt_En1, mass_R0_gm, mass_En1, feed_wpa_lo, feed_wpa_hi)
fig_feed_trend = _fig_feed_trend.to_json() if _fig_feed_trend is not None else None

def _build(key):
    if key == 'fig1':   return plot_util.fig_ternary_equilibrium(system).to_json()
    if key == 'fig2a':  return plot_util.fig_conjugate_curve(system, conjugate).to_json()
    if key == 'fig2b':  return plot_util.fig_interpolated_tie_lines(system, conjugate, steps, N_theory).to_json()
    if key == 'fig3':   return plot_util.fig_hunter_nash(system, steps, N_theory, pt_R0, pt_Rn, pt_E1, pt_En1, pt_P).to_json()
    if key == 'fig4':   return plot_util.fig_lever_rule(system, pt_R0, pt_Rn, pt_E1, pt_En1, pt_M, pt_Mp_exp, pt_E1p_exp, title='Overall Mass Balance (Lever Rule)').to_json()
    # fig_sf / fig_feed are NOT batch-built here — the explorer tabs render live
    # in the browser via PY_SF / PY_FEED (see computeExplorer). The static
    # slider-frame figures (fig_lever_rule_interactive[_feed]) are only used by
    # main.py's standalone-HTML export, not the web app.
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

_req_keys = [k for k in _requested_keys if k in ('fig1', 'fig2a', 'fig2b', 'fig3', 'fig4')]
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
    'sf_range': {'min': sf_frac_min, 'max': sf_frac_max},
    'feed_range': {'min': feed_wpa_lo, 'max': feed_wpa_hi},
    'fig_sf_trend': fig_sf_trend,
    'sf_min_found': sf_min_found,
    'sf_max_found': sf_max_found,
    'fig_feed_trend': fig_feed_trend,
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

// Feed Explorer live view: real R₀ and its real mixing point M (_b._ept_M) stay
// fixed as anchors — exactly like the other tabs — while the slider explores a
// hypothetical feed R₀' whose M' and E₁' move. See plot_util.fig_feed_explorer.
const PY_FEED = `
import json, math, builtins as _b
wpa    = float(_feed_wpa)
wbp    = 100.0 - wpa
pt_R0h = (wbp + 0.5*wpa, math.sqrt(3)/2 * wpa)
pt_Mph = mixing_point(pt_R0h, _b._ept_En1, mass_A=_b._emass_R0, mass_B=_b._emass_En1)
pt_E1ph = find_E1_prime(_b._ept_Rn, pt_Mph, _b._esystem.spline)
_solute_abbr = _b._esystem.labels['solute']['abbr']
plot_util.fig_feed_explorer(
    _b._esystem, _b._ept_R0, _b._ept_Rn, _b._ept_E1, _b._ept_En1, _b._ept_M,
    pt_R0h, pt_Mph, pt_E1ph,
    title=f"Feed {_solute_abbr} {wpa:.1f} wt%"
).to_json()
`;

let explorerReady = false;

async function computeExplorer(type) {
  if (!explorerReady) return;
  // 'sf' renders into the plot-with-panel's chart-fig_sf; 'feed' has no
  // side panel and renders straight into plot-fig_feed.
  const el = document.getElementById('chart-fig_' + type) || document.getElementById('plot-fig_' + type);
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
// S/F derived from the same rounded wt% shown in #sf-num (not the raw
// frac), so a hand-check against the displayed % always reconciles — see
// the same fix applied to the (S/F)_min/(S/F)_max reference cards.
function _sfRatioText(wtPctStr) {
  const wt = parseFloat(wtPctStr);
  return `S/F: ${(wt / (100 - wt)).toFixed(2)}`;
}

function updateSfLabels(frac) {
  document.getElementById('sf-slider').value  = frac;
  const wt = (frac * 100).toFixed(0);
  document.getElementById('sf-num').value     = wt;
  document.getElementById('sf-ratio-label').textContent = _sfRatioText(wt);
  document.getElementById('sf-feed-label').textContent = `Feed ${((1-frac)*100).toFixed(0)} wt%`;
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

// S:F number input — clamp (to whatever range is currently set on the
// element, see updateSfRange) and sync
document.getElementById('sf-num').addEventListener('change', function() {
  const lo = parseFloat(this.min), hi = parseFloat(this.max);
  let v = parseFloat(this.value);
  if (isNaN(v)) v = (lo + hi) / 2;
  v = Math.max(lo, Math.min(hi, v));
  updateSfLabels(v / 100);
  computeExplorer('sf');
});
document.getElementById('sf-num').addEventListener('input', function() {
  const lo = parseFloat(this.min), hi = parseFloat(this.max);
  const v = parseFloat(this.value);
  if (!isNaN(v) && v >= lo && v <= hi) {
    document.getElementById('sf-slider').value = v / 100;
    document.getElementById('sf-ratio-label').textContent = _sfRatioText(v.toFixed(0));
    document.getElementById('sf-feed-label').textContent = `Feed ${(100-v).toFixed(0)} wt%`;
    computeExplorer('sf');
  }
});

// System-specific S:F range (S_min/S_max, see lever_rule.find_smin_over_f /
// find_smax_over_f). The background track always shows the full 0-100%
// range (valid/invalid zones + markers) for context, but the draggable
// #sf-slider itself is physically resized/repositioned and min/max-clamped
// to [S_min, S_max] on every Calculate — so it's impossible to drag past
// either limit, not just visually discouraged.
const SF_SLIDER_LO = 0.0, SF_SLIDER_HI = 1.0;
let _sfBounds = null;
let _sfLimits = null;   // raw S_min/S_max fracs from the last Calculate, for export

function updateSfRange(sfRange) {
  if (!sfRange) return;
  _sfBounds = sfRange;
  const pct = v => Math.max(0, Math.min(100, (v - SF_SLIDER_LO) / (SF_SLIDER_HI - SF_SLIDER_LO) * 100));
  const loPct = pct(sfRange.min), hiPct = pct(sfRange.max);

  // Background track: full 0-100% context, valid/invalid zones + markers.
  document.getElementById('sf-zone-lo').style.cssText    = `left:0; width:${loPct}%`;
  document.getElementById('sf-zone-valid').style.cssText = `left:${loPct}%; width:${Math.max(0, hiPct - loPct)}%`;
  document.getElementById('sf-zone-hi').style.cssText    = `left:${hiPct}%; width:${100 - hiPct}%`;
  document.getElementById('sf-marker-min').style.left = loPct + '%';
  document.getElementById('sf-marker-max').style.left = hiPct + '%';

  // Foreground (actually draggable) slider: sized/positioned to exactly the
  // S_min-S_max slice, with its own min/max set to match — so it's
  // physically impossible to drag past either limit, not just visually
  // discouraged.
  const slider = document.getElementById('sf-slider');
  const num = document.getElementById('sf-num');
  slider.style.left  = loPct + '%';
  slider.style.width = Math.max(0, hiPct - loPct) + '%';
  slider.min = sfRange.min;
  slider.max = sfRange.max;
  num.min = (sfRange.min * 100).toFixed(0);
  num.max = (sfRange.max * 100).toFixed(0);

  const clamped = Math.min(Math.max(parseFloat(slider.value), sfRange.min), sfRange.max);
  // Always refresh (not just on clamp) — the S/F ratio label needs to
  // populate on the very first Calculate even when the default value
  // didn't need to move.
  updateSfLabels(clamped);
}

// System-specific feed-composition range (lever_rule.find_feed_bounds —
// the probed feasible span for the current system and flows, or the fixed
// legacy 10-55 fallback). Applied to both the slider and the number input
// on every Calculate; the current value is clamped into the new range,
// falling back to the experimental feed composition.
function updateFeedRange(feedRange, wpaExp) {
  if (!feedRange) return;
  const slider = document.getElementById('feed-slider');
  const num = document.getElementById('feed-num');
  slider.min = feedRange.min;
  slider.max = feedRange.max;
  num.min = feedRange.min;
  num.max = feedRange.max;
  let v = parseFloat(slider.value);
  if (isNaN(v)) v = wpaExp;
  v = Math.max(feedRange.min, Math.min(feedRange.max, v));
  updateFeedLabels(v);
}

// Feed slider
document.getElementById('feed-slider').addEventListener('input', function() {
  updateFeedLabels(parseFloat(this.value));
  computeExplorer('feed');
});

// Feed number input — clamp to whatever range is currently set on the
// element (see updateFeedRange) and sync
document.getElementById('feed-num').addEventListener('change', function() {
  const lo = parseFloat(this.min), hi = parseFloat(this.max);
  let v = parseFloat(this.value);
  if (isNaN(v)) v = (lo + hi) / 2;
  v = Math.max(lo, Math.min(hi, v));
  updateFeedLabels(v);
  computeExplorer('feed');
});
document.getElementById('feed-num').addEventListener('input', function() {
  const lo = parseFloat(this.min), hi = parseFloat(this.max);
  const v = parseFloat(this.value);
  if (!isNaN(v) && v >= lo && v <= hi) {
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
      config.C_NAOH             = _c_naoh
      config.V_ALIQUOT_ML       = _v_aliquot
    `);

    pyodide.globals.set('_f_R0', parseInt(document.getElementById('f-R0').value));
    pyodide.globals.set('_f_E1', parseInt(document.getElementById('f-E1').value));
    pyodide.globals.set('_f_Rn', parseInt(document.getElementById('f-Rn').value));
    pyodide.globals.set('_requested_keys', toFetch);
    const json = await pyodide.runPythonAsync(PY_COMPUTE);
    const data = JSON.parse(json);

    // Update cache
    for (const [k, v] of Object.entries(data.figures)) {
      cache[k] = JSON.parse(v);
      rendered[k] = false;
      if (k === 'fig2a') {
        // The Calculate path only ever recomputes the diagonal method
        // (see PY_COMPUTE) — keep that cached under its own key and
        // restore whichever method the toggle is currently on, instead
        // of silently reverting the displayed curve to diagonal.
        cache.fig2a_diagonal = cache.fig2a;
        cache.fig2a = cache['fig2a_' + _conjMethod] || cache.fig2a;
      }
    }

    renderFig(activeTab);
    showResults(data);
    updateSfRange(data.sf_range);
    updateFeedRange(data.feed_range, data.stream_points.R0.wpa);
    explorerReady = true;

    // If currently on an explorer tab, reveal it now that data exists
    if (activeTab === 'fig_sf' || activeTab === 'fig_feed') showExplorerTab(activeTab);

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
  // fig2b (interpolated tie-lines) and fig4 (lever rule) are always
  // computed so the zip export can include them even if their tabs were
  // never opened.
  const keys = ['fig3', 'fig2b', 'fig4'];
  // fig_sf / fig_feed are never batch-built — they render live via computeExplorer.
  if (cache['fig1']  || activeTab === 'fig1')  keys.push('fig1');
  if (cache['fig2a'] || activeTab === 'fig2a') keys.push('fig2a');
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
      // b fits the two bottom ternary axis titles, which _bottom_axis_title()
      // lifts off the tick numbers; at the old b:10 they fell off the figure
      // entirely. t drops the triangle far enough that the apex title clears
      // the chart title — the apex title's own distance from its tick numbers
      // is fixed by Plotly and cannot be tuned (ternary axes have no
      // title.standoff, and a trailing <br> is stripped).
      patched.margin = { l: 40, r: 130, t: 60, b: 50 };
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
  Plotly.newPlot(el, _figData(key), patchedLayout(fig.layout), PLOTLY_CFG);
  if (fig.frames?.length) Plotly.addFrames(el, fig.frames);
  rendered[key] = true;
  requestAnimationFrame(() => Plotly.Plots.resize(el));
}

// Explorer tabs (S:F, Feed) render live via computeExplorer once an analysis
// has been run. Before that they show the same "ready to analyze" prompt as the
// other tabs instead of a blank chart. Called from switchTab and from the
// Calculate handler, so switching in early then computing still reveals it.
function showExplorerTab(key) {
  const bar     = document.getElementById('explorer-bar');
  const sfBar   = document.getElementById('sf-bar');
  const feedBar = document.getElementById('feed-bar');
  if (!explorerReady) {
    bar.style.display = 'none';
    document.getElementById('empty').style.display = 'flex';
    return;
  }
  document.getElementById('empty').style.display = 'none';
  bar.style.display = 'flex';
  if (key === 'fig_sf') {
    sfBar.style.display   = 'flex';
    feedBar.style.display = 'none';
    document.getElementById('plot-fig_sf').style.paddingTop = '52px';
    computeExplorer('sf');
    requestAnimationFrame(() => { _renderSfTrendChart(); });
  } else {
    sfBar.style.display   = 'none';
    feedBar.style.display = 'flex';
    document.getElementById('plot-fig_feed').style.paddingTop = '52px';
    computeExplorer('feed');
    requestAnimationFrame(() => { _renderFeedTrendChart(); });
  }
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
  _setDataTrigger(key in DATA_PANEL_TABS, DATA_PANEL_TABS[key]);

  // Re-render all chart tabs on every tab switch so Plotly sizes to the current container.
  if (['fig1', 'fig2a', 'fig2b', 'fig3', 'fig4'].includes(key) && cache[key]) {
    requestAnimationFrame(() => {
      const _el = document.getElementById('chart-' + key) || document.getElementById('plot-' + key);
      if (_el?.data) Plotly.react(_el, _figData(key), patchedLayout(cache[key].layout), PLOTLY_CFG);
    });
  }

  if (key === 'contact' || key === 'guide' || key === 'system') {
    document.getElementById('empty').style.display = 'none';
  }

  if (key === 'contact' && window.innerWidth < 1200) {
    // Mobile/tablet: close overlay sidebar if open
    document.querySelector('aside').classList.remove('open');
    document.getElementById('sidebar-backdrop')?.classList.remove('show');
  }
  if (!sidebarManualOverride && window.innerWidth >= 1200) {
    const hasData = Object.keys(cache).length > 0;
    if (TABS_AUTO_COLLAPSE.has(key) || key === 'contact') {
      setSidebarCollapsed(true);
    } else if (TABS_NEED_SIDEBAR.has(key)) {
      setSidebarCollapsed(false);
    } else if (hasData) {
      setSidebarCollapsed(true);
    }
  }
  sidebarManualOverride = false;

  if (key === 'fig_sf' || key === 'fig_feed') {
    showExplorerTab(key);
  } else {
    document.getElementById('explorer-bar').style.display = 'none';
    document.getElementById('plot-fig_sf').style.paddingTop   = '0';
    document.getElementById('plot-fig_feed').style.paddingTop = '0';
    if (key === 'guide')  { document.getElementById('empty').style.display = 'none'; loadGuide(); return; }
    if (key === 'system') { document.getElementById('empty').style.display = 'none'; loadSystemTab(); return; }
    if (cache[key]) {
      document.getElementById('empty').style.display = 'none';
      renderFig(key);
      if (key === 'fig1') requestAnimationFrame(() => { _renderCorrChart(_corrActive); _renderSelectivityChart(); });
      if (key === 'fig2a') requestAnimationFrame(() => { _renderPlaitChart(); });
    } else if (pyReady && cache['fig3'] && key.startsWith('fig')) {
      // Only figure tabs may be requested from Python — a non-figure tab
      // (contact) would make PY_COMPUTE's _build() return '' and crash
      // JSON.parse with "Unexpected end of JSON input".
      calculate([key]);
    } else if (pyReady && !TABS_AUTO_COLLAPSE.has(key)) {
      document.getElementById('empty').style.display = 'flex';
    }
  }
}

// ── Results panel ──────────────────────────────────────────────────────────
function updateTableHeaders() {
  const s = _lbls.solute.abbr, c = _lbls.carrier.abbr, sv = _lbls.solvent.abbr;
  document.getElementById('stream-thead').innerHTML =
    `<tr><th>Stream</th><th>${s}%</th><th>${c}%</th><th>${sv}%</th></tr>`;
  document.getElementById('stages-thead').innerHTML =
    `<tr><th>#</th><th></th><th>${s}%</th><th>${c}%</th><th>${sv}%</th></tr>`;
  document.getElementById('feed-pa-label').textContent = `Feed ${s}`;
}
updateTableHeaders();

function showResults(data) {
  document.getElementById('n-val').textContent   = data.N_theory.toFixed(1);
  document.getElementById('badge-n').textContent = 'N=' + data.N_theory.toFixed(1);
  document.getElementById('n-sub').textContent   = '';

  const streams = [
    {name:'R<sub>0</sub>',   cls:'R', d:data.stream_points.R0 },
    {name:'E<sub>1</sub>',   cls:'E', d:data.stream_points.E1 },
    {name:'R<sub>N</sub>',   cls:'R', d:data.stream_points.Rn },
    {name:'E<sub>N+1</sub>', cls:'E', d:data.stream_points.En1},
  ];
  document.getElementById('stream-tbody').innerHTML = streams.map(s =>
    `<tr><td><span class="dot dot-${s.cls}"></span>${s.name}</td><td>${s.d.wpa}</td><td>${s.d.wbp}</td><td>${s.d.ww}</td></tr>`
  ).join('');

  document.getElementById('stages-tbody').innerHTML = data.stages.flatMap(s => [
    `<tr><td>${s.index}</td><td style="color:#dc2626">E</td><td>${s.E.wpa}</td><td>${s.E.wbp}</td><td>${s.E.ww}</td></tr>`,
    `<tr><td></td><td style="color:var(--blue)">R</td><td>${s.R.wpa}</td><td>${s.R.wbp}</td><td>${s.R.ww}</td></tr>`,
  ]).join('');

  document.getElementById('flows-text').innerHTML =
    `<strong>Solvent</strong>${data.mass_flows.solvent_g_min} g/min<br>` +
    `<strong>Feed</strong>${data.mass_flows.feed_g_min} g/min`;

  document.getElementById('panel-fig3').classList.add('has-data');

  if (data.fig_sf_trend) {
    cache.fig_sf_trend = JSON.parse(data.fig_sf_trend);
    _renderSfTrendChart();
  } else {
    cache.fig_sf_trend = null;
    const el = document.getElementById('sf-trend-chart');
    if (el) { try { Plotly.purge(el); } catch(e) {} }
  }

  // frac is S/(F+S) (the slider's own convention); (S/F)_min/max is the
  // textbook solvent-to-feed ratio itself, S/F = frac/(1-frac). Derive the
  // ratio from the ALREADY-ROUNDED wt% (not the raw frac) so a reader who
  // hand-checks S/F from the displayed wt% gets exactly the number shown
  // — two independently-rounded views of the same frac can otherwise
  // silently disagree at the displayed precision (e.g. 92.4 wt% by hand
  // gives 12.16, not a separately-rounded 12.14).
  const sfWtPct = frac => (frac * 100).toFixed(1);
  const sfRatioFromWt = wtStr => {
    const wt = parseFloat(wtStr);
    return (wt / (100 - wt)).toFixed(2);
  };

  // Stash the raw computed limits for the zip export (result.xlsx), so the
  // exported values come from the same numbers the cards below display.
  _sfLimits = { min: data.sf_min_found, max: data.sf_max_found };

  if (data.sf_min_found != null) {
    const wt = sfWtPct(data.sf_min_found);
    document.getElementById('sf-min-val').textContent =
      sfRatioFromWt(wt) + ' (solvent ' + wt + ' wt%)';
    document.getElementById('sf-min-desc').innerHTML =
      '<strong>How it\'s found:</strong><br>Where P lands on a tie line, a stage\'s step and that tie line become the same line — the step moves nothing, so no stage count reaches the target.';
  } else {
    document.getElementById('sf-min-val').textContent = '—';
    document.getElementById('sf-min-desc').innerHTML =
      '<strong>Not found:</strong><br>This system\'s tie-line data doesn\'t produce a clear (S/F)<sub>min</sub> (e.g. a solutropic system).';
  }
  if (data.sf_max_found != null) {
    const wt = sfWtPct(data.sf_max_found);
    document.getElementById('sf-max-val').textContent =
      sfRatioFromWt(wt) + ' (solvent ' + wt + ' wt%)';
    document.getElementById('sf-max-desc').innerHTML =
      '<strong>How it\'s found:</strong><br>Where the feed+solvent line meets the binodal curve, M becomes a single phase, nothing left to separate.';
  } else {
    document.getElementById('sf-max-val').textContent = '—';
    document.getElementById('sf-max-desc').innerHTML =
      '<strong>Not found:</strong><br>This system\'s equilibrium data doesn\'t produce a clear (S/F)<sub>max</sub>.';
  }

  document.getElementById('panel-fig_sf').classList.add('has-data');

  if (data.fig_feed_trend) {
    cache.fig_feed_trend = JSON.parse(data.fig_feed_trend);
    _renderFeedTrendChart();
  } else {
    cache.fig_feed_trend = null;
    const el = document.getElementById('feed-trend-chart');
    if (el) { try { Plotly.purge(el); } catch(e) {} }
  }
  document.getElementById('panel-fig_feed').classList.add('has-data');
}

function _renderFeedTrendChart() {
  const el = document.getElementById('feed-trend-chart');
  if (!el || !cache.fig_feed_trend) return;
  const w = el.offsetWidth || 320;
  const layout = { ...cache.fig_feed_trend.layout, width: w, autosize: false };
  return Plotly.react(el, cache.fig_feed_trend.data, layout, { displayModeBar: false });
}

function _renderSfTrendChart() {
  const el = document.getElementById('sf-trend-chart');
  if (!el || !cache.fig_sf_trend) return;
  const w = el.offsetWidth || 320;
  const layout = { ...cache.fig_sf_trend.layout, width: w, autosize: false };
  return Plotly.react(el, cache.fig_sf_trend.data, layout, { displayModeBar: false });
}

// ── System configuration ───────────────────────────────────────────────────
let defaultSystemYaml = '';
let systemTabLoaded   = false;
let systemList        = [];
let currentSystemFile = 'bp_pa_w_snu_cbe.yaml';

// Dropdown label from a parsed system: "Carrier (1) + Solute (2) + Solvent (3) (note)"
// note is omitted when empty.
function systemLabel(d) {
  const c = d.components || {};
  const names = `${c.carrier?.name || 'Carrier'} (1) + ${c.solute?.name || 'Solute'} (2) + ${c.solvent?.name || 'Solvent'} (3)`;
  const note = (d.note || '').trim();
  const label = note ? `${names} (${note})` : names;
  return label.replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
}

async function loadSystemTab() {
  if (systemTabLoaded) return;
  systemTabLoaded = true;
  try {
    const listResp = await fetch('/systems/index.json', { cache: 'no-store' });
    if (listResp.ok) {
      systemList = await listResp.json();   // array of file names
      const sel = document.getElementById('sys-select');
      const opts = await Promise.all(systemList.map(async file => {
        let label = file;
        try {
          const r = await fetch('/systems/' + file, { cache: 'no-store' });
          if (r.ok) label = systemLabel(jsyaml.load(await r.text()));
        } catch (e) { console.error('System label:', file, e); }
        return `<option value="${file}"${file === currentSystemFile ? ' selected' : ''}>${label}</option>`;
      }));
      opts.push('<option value="__new__">+ Enter your own dataset</option>');
      sel.innerHTML = opts.join('');
    }
  } catch (e) { console.error('System list:', e); }
  try {
    const resp = await fetch('/systems/' + currentSystemFile, { cache: 'no-store' });
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
  if (file === '__new__') { loadBlankTemplate(); return; }
  try {
    const resp = await fetch('/systems/' + file, { cache: 'no-store' });
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

// Fixed example shown as gray placeholders in "+ Enter your own dataset" mode, so the
// hints (and the number of rows) stay consistent regardless of which system was
// loaded before. Purely a UI hint — not parsed or applied.
const BLANK_EXAMPLE = {
  components: {
    carrier: { name: 'n-Bromopropane', abbr: 'BP' },
    solute:  { name: 'Propionic acid', abbr: 'PA' },
    solvent: { name: 'Water',          abbr: 'W'  },
  },
  properties: { rho_carrier: 1.354, rho_solute: 0.993, rho_solvent: 0.997, mw_solute: 74.08 },
  equilibrium_data: [
    [5.1, 9.49, 85.41], [8.37, 36.65, 54.98], [17.67, 49.4, 32.93],
    [32.724, 49.087, 18.189], [56.74, 37.83, 5.43], [84.18, 9.35, 6.47],
  ],
  tie_lines: [
    [6.253, 2.564], [8.02, 2.65], [8.291, 3.058],
    [14.175, 8.047], [16.73, 9.88], [26.069, 19.418],
  ],
  note: 'SNU CBE, 25 °C, Treybal (1980), Zhang (2020)',
};

// "Enter your own dataset" — clear the form and show BLANK_EXAMPLE as gray placeholders.
function loadBlankTemplate() {
  const d = BLANK_EXAMPLE;
  const c = d.components, p = d.properties;
  const ph = (id, val, prefix = '') => {
    const el = document.getElementById(id);
    if (!el) return;
    el.value = '';
    if (val !== undefined && val !== null && String(val) !== '') el.placeholder = prefix + val;
  };
  ph('sf-carrier-name', c.carrier.name, 'e.g. ');
  ph('sf-carrier-abbr', c.carrier.abbr);
  ph('sf-solute-name',  c.solute.name,  'e.g. ');
  ph('sf-solute-abbr',  c.solute.abbr);
  ph('sf-solvent-name', c.solvent.name, 'e.g. ');
  ph('sf-solvent-abbr', c.solvent.abbr);
  ph('sf-rho-carrier', p.rho_carrier);
  ph('sf-rho-solute',  p.rho_solute);
  ph('sf-rho-solvent', p.rho_solvent);
  ph('sf-mw-solute',   p.mw_solute);
  ph('sf-note', d.note, 'e.g. ');
  fillDataTable('sf-equil-tbody', [], d.equilibrium_data, 3);
  fillDataTable('sf-tie-tbody', [], d.tie_lines, 2);
  syncYamlFromForm();
  setSysMsg('Gray text shows example values — type in your own.', '');
}

function resetSystem() {
  document.getElementById('sys-yaml').value = defaultSystemYaml;
  populateFormFromYaml(defaultSystemYaml);
  setSysMsg('Editor reset to default. Press Apply System to rebuild from it.', '');
}

// Download the user's CURRENT system (form, or Advanced text if open) as a .yaml file.
// Filename is auto-derived from components + note, but the user can rename it in the save dialog.
function downloadUserYaml() {
  const advancedOpen = document.getElementById('sys-advanced').open;
  const yamlText = advancedOpen ? document.getElementById('sys-yaml').value : collectFormToYaml();
  let d = {};
  try { d = jsyaml.load(yamlText) || {}; } catch (e) {}
  const c = d.components || {};
  const slug = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const parts = [slug(c.carrier?.abbr) || 'carrier', slug(c.solute?.abbr) || 'solute', slug(c.solvent?.abbr) || 'solvent'];
  let base = parts.join('_');
  const noteSlug = slug(d.note).slice(0, 20).replace(/_+$/, '');
  if (noteSlug) base += '_' + noteSlug;
  const blob = new Blob([yamlText], { type: 'text/yaml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = base + '.yaml';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ── Bundle export (system + figures + tables as a .zip) ───────────────────

async function exportBundle() {
  if (!pyReady || typeof JSZip === 'undefined') return;
  const btn = document.getElementById('export-btn');
  const label = btn.querySelector('.export-label');
  const origLabel = label.textContent;
  btn.disabled = true;
  label.textContent = 'Exporting…';

  try {
    const zip = new JSZip();
    const included = [];
    const calculated = document.getElementById('panel-fig3').classList.contains('has-data');
    const dateStr = new Date().toISOString().slice(0, 10);
    const slug = (currentSystemFile || 'system.yaml').replace(/\.yaml$/, '');

    // System YAML
    const advancedOpen = document.getElementById('sys-advanced')?.open;
    const yamlText = advancedOpen ? document.getElementById('sys-yaml').value : collectFormToYaml();
    zip.file('system.yaml', yamlText);
    included.push('system.yaml');

    // Figures: rendered into a hidden offscreen div (#export-render, see
    // index.html) rather than the visible tab panes — so export never
    // switches the tab/model/method the user is actually looking at, and
    // nothing needs to be restored afterwards. cache[key].data/layout is
    // the exact same figure Python built for the on-screen chart; the one
    // addition is the Treybal plait-point star, which is appended at render
    // time (see _plaitStarTrace / _figData) rather than being part of the
    // cached figure itself.
    const hiddenEl = document.getElementById('export-render');
    // `scale` multiplies the PNG resolution without touching the layout —
    // used for the small explorer trend charts, whose 320x260 layouts and
    // 9-10 pt fonts would look sparse if stretched to 900 px instead.
    async function _captureFig(key, w, h, filename, extraTraces, scale) {
      if (!cache[key] || !hiddenEl) return;
      const data = extraTraces ? [...cache[key].data, ...extraTraces] : cache[key].data;
      const layout = { ...cache[key].layout, width: w, height: h, autosize: false };
      await Plotly.newPlot(hiddenEl, data, layout, { displayModeBar: false });
      const dataUrl = await Plotly.toImage(hiddenEl, { format: 'png', width: w, height: h, scale: scale || 1 });
      zip.file(filename, dataUrl.split(',')[1], { base64: true });
      included.push(filename);
    }

    // Export filenames are numbered in their own presentation order
    // (fig1..fig10), independent of the internal cache keys.
    const star = _plaitStats ? [_plaitStarTrace()] : null;
    await _captureFig('fig1', 900, 900, 'fig1_LLE_ternary_diagram.png');
    await _captureFig('fig_selectivity', 700, 500, 'fig2_selectivity.png');
    await _captureFig('fig_corr_ot', 700, 500, 'fig3a_correlation_OT.png');
    await _captureFig('fig_corr_hand', 700, 500, 'fig3b_correlation_Hand.png');
    await _captureFig('fig_corr_bachman', 700, 500, 'fig3c_correlation_Bachman.png');
    await _captureFig('fig2a_diagonal', 900, 900, 'fig4a_conjugate_curve_diagonal.png', star);
    await _captureFig('fig2a_horizontal', 900, 900, 'fig4b_conjugate_curve_horizontal.png', star);
    await _captureFig('fig_plait', 700, 700, 'fig5_treybal_plait_point.png');
    if (calculated) {
      await _captureFig('fig3', 900, 900, 'fig6_Hunter_Nash.png');
      await _captureFig('fig2b', 900, 900, 'fig7_interpolated_tie_lines.png');
      await _captureFig('fig4', 900, 900, 'fig8_lever_rule.png');
      await _captureFig('fig_sf_trend', 320, 260, 'fig9_sf_stage_trend.png', null, 3);
      await _captureFig('fig_feed_trend', 320, 260, 'fig10_feed_stage_trend.png', null, 3);
    }
    Plotly.purge(hiddenEl);

    // Tables: one result.xlsx workbook, one sheet per table (friendlier
    // for students than a scatter of loose .csv files — table_to_sheet
    // also honors colspan/rowspan as real merged cells, so the two-row
    // tie-line header lines up properly instead of the ragged CSV row
    // a plain text export would produce). Correlation model coefficients
    // (a, b, R²) are appended below the Equilibrium table on the same sheet,
    // pulled from the same _corrStats the on-screen formula panel uses.
    const wb = XLSX.utils.book_new();

    const tieEl = document.getElementById('tieline-table');
    if (tieEl?.querySelector('tr')) {
      const tieSheet = XLSX.utils.table_to_sheet(tieEl);
      if (_corrStats) {
        const range = XLSX.utils.decode_range(tieSheet['!ref']);
        const corrRows = [[], ['Correlation', 'a', 'b', 'R2']];
        for (const m of ['ot', 'hand', 'bachman']) {
          if (_corrStats[m]) corrRows.push([_CORR_FORMULA[m].label, _corrStats[m].a, _corrStats[m].b, _corrStats[m].r2]);
        }
        XLSX.utils.sheet_add_aoa(tieSheet, corrRows, { origin: { r: range.e.r + 2, c: 0 } });
      }
      XLSX.utils.book_append_sheet(wb, tieSheet, 'Equilibrium');
    }

    const plaitTableEl = document.querySelector('#plait-stats table');
    if (plaitTableEl?.querySelector('tr')) {
      XLSX.utils.book_append_sheet(wb, XLSX.utils.table_to_sheet(plaitTableEl), 'Plait Point Comparison');
    }

    if (calculated) {
      const streamEl = document.getElementById('stream-tbody')?.closest('table');
      const stageEl = document.getElementById('stages-tbody')?.closest('table');
      if (streamEl?.querySelector('tr')) {
        const streamSheet = XLSX.utils.table_to_sheet(streamEl);
        // S/F limits appended below the stream table, same pattern as the
        // correlation coefficients under Equilibrium. The w/w ratio is
        // derived from the rounded wt% (not the raw frac) so it matches
        // the S:F Explorer cards exactly and reconciles under hand
        // calculation from the wt% column shown right next to it.
        if (_sfLimits && (_sfLimits.min != null || _sfLimits.max != null)) {
          const range = XLSX.utils.decode_range(streamSheet['!ref']);
          const sfRows = [[], ['S/F limits', 'S/(S+F) (wt%)', 'S/F (w/w)']];
          const sfWtNum = frac => Number((frac * 100).toFixed(1));
          const sfRatioNum = wt => Number((wt / (100 - wt)).toFixed(2));
          if (_sfLimits.min != null) { const wt = sfWtNum(_sfLimits.min); sfRows.push(['(S/F)_min', wt, sfRatioNum(wt)]); }
          if (_sfLimits.max != null) { const wt = sfWtNum(_sfLimits.max); sfRows.push(['(S/F)_max', wt, sfRatioNum(wt)]); }
          XLSX.utils.sheet_add_aoa(streamSheet, sfRows, { origin: { r: range.e.r + 2, c: 0 } });
        }
        XLSX.utils.book_append_sheet(wb, streamSheet, 'Stream Points');
      }
      if (stageEl?.querySelector('tr')) XLSX.utils.book_append_sheet(wb, XLSX.utils.table_to_sheet(stageEl), 'Stage-by-Stage Compositions');
    }

    const xlsxName = 'result.xlsx';
    if (wb.SheetNames.length) {
      const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      zip.file(xlsxName, wbout);
      included.push(xlsxName + ' (' + wb.SheetNames.join(', ') + ')');
    }

    // Manifest: always say what's in the zip, and why anything is missing,
    // so opening it later (without the app open) still explains itself.
    let manifest = `CBPL-kit export — ${slug} — ${dateStr}\n\nIncluded:\n`
      + included.map(f => '  ' + f).join('\n');
    if (!calculated) {
      manifest += '\n\nNot included: LLE Hunter-Nash analysis results\n'
        + '  -> Run "Calculate" with titration volumes and flow rates, then export again to include these.';
    }
    zip.file('README.txt', manifest);

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `cbpl_${slug}_${dateStr}.zip`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  } catch (err) {
    console.error('Export failed:', err);
    alert('Export failed: ' + err.message);
  } finally {
    btn.disabled = false;
    label.textContent = origLabel;
  }
}

// Render a data table. When `data` has rows, show those values; otherwise show the
// `example` system's rows with empty values so they read as gray placeholders. Each
// cell also carries the matching example value as its placeholder.
function fillDataTable(tbodyId, data, example, ncol) {
  data = Array.isArray(data) ? data : [];
  example = Array.isArray(example) ? example : [];
  const hasData = data.length > 0;
  const rows = hasData ? data : example;
  document.getElementById(tbodyId).innerHTML = rows.map((row, i) => {
    const cells = Array.from({ length: ncol }, (_, j) => {
      const val = hasData ? (row[j] ?? '') : '';
      const ph = (example[i] != null && example[i][j] != null) ? example[i][j] : '';
      return `<td><input value="${val}" type="number" step="0.01" placeholder="${ph}" /></td>`;
    }).join('');
    return `<tr><td>${i + 1}</td>${cells}</tr>`;
  }).join('');
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
    // Data tables show exactly what the YAML contains (empty → empty table).
    fillDataTable('sf-equil-tbody', d.equilibrium_data, [], 3);
    fillDataTable('sf-tie-tbody', d.tie_lines, [], 2);
    document.getElementById('sf-note').value = d.note || '';
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
  syncYamlFromForm();
}

// Build the canonical system YAML string directly (with comments + note),
// so the Advanced text area matches the hand-written system files and the guide.
function collectFormToYaml() {
  const v = id => document.getElementById(id).value.trim();
  const cName = v('sf-carrier-name'), cAbbr = v('sf-carrier-abbr');
  const sName = v('sf-solute-name'),  sAbbr = v('sf-solute-abbr');
  const vName = v('sf-solvent-name'), vAbbr = v('sf-solvent-abbr');
  const rowsYaml = tbodyId => {
    const rows = [...document.getElementById(tbodyId).rows]
      .map(r => [...r.querySelectorAll('input')].map(i => i.value.trim()))
      .filter(cells => cells.some(c => c !== ''));   // drop fully-empty rows so blank form stays valid YAML
    return rows.length ? '\n' + rows.map(cells => `  - [${cells.join(', ')}]`).join('\n') : ' []';
  };
  const eqRows = rowsYaml('sf-equil-tbody');
  const tieRows = rowsYaml('sf-tie-tbody');
  return `# System Configuration

components:
  carrier: { name: "${cName}", abbr: "${cAbbr}" }   # (1)
  solute: { name: "${sName}", abbr: "${sAbbr}" }   # (2)
  solvent: { name: "${vName}", abbr: "${vAbbr}" }   # (3)

properties:
  rho_carrier: ${v('sf-rho-carrier')}   # g/mL
  rho_solute: ${v('sf-rho-solute')}   # g/mL
  rho_solvent: ${v('sf-rho-solvent')}   # g/mL
  mw_solute: ${v('sf-mw-solute')}   # g/mol

# Each row: [Carrier wt%, Solute wt%, Solvent wt%]
# (100w1, 100w2, 100w3; sorted by increasing carrier)
equilibrium_data:${eqRows}

# Each row: [Solute wt% in solvent-rich phase (3), Solute wt% in carrier-rich phase (1)]
# (100w23, 100w21; sorted by increasing solute)
tie_lines:${tieRows}

# data source, temperature, etc. - free text
note: "${v('sf-note')}"
`;
}

// Keep the Advanced YAML text area (and thus the download filename) in sync with the
// form while Advanced is open. When Advanced is closed we leave the text area alone,
// so manually-typed YAML edits there aren't clobbered.
function syncYamlFromForm() {
  const adv = document.getElementById('sys-advanced');
  if (adv && adv.open) document.getElementById('sys-yaml').value = collectFormToYaml();
}
document.getElementById('sys-form')?.addEventListener('input', syncYamlFromForm);

// Reverse sync: when the user types or pastes YAML in the Advanced editor, mirror it
// back into the form above. Programmatic .value changes don't fire 'input', so the two
// directions never trigger each other (no feedback loop).
document.getElementById('sys-yaml')?.addEventListener('input', () => {
  populateFormFromYaml(document.getElementById('sys-yaml').value);
});

function addEquilRow() {
  const tbody = document.getElementById('sf-equil-tbody');
  const n = tbody.rows.length + 1;
  tbody.insertAdjacentHTML('beforeend', `<tr><td>${n}</td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td></tr>`);
  syncYamlFromForm();
}
function removeEquilRow() {
  const tbody = document.getElementById('sf-equil-tbody');
  if (tbody.rows.length > 0) tbody.deleteRow(-1);
  syncYamlFromForm();
}
function addTieRow() {
  const tbody = document.getElementById('sf-tie-tbody');
  const n = tbody.rows.length + 1;
  tbody.insertAdjacentHTML('beforeend', `<tr><td>${n}</td><td><input value="" type="number" step="0.01" /></td><td><input value="" type="number" step="0.01" /></td></tr>`);
  syncYamlFromForm();
}
function removeTieRow() {
  const tbody = document.getElementById('sf-tie-tbody');
  if (tbody.rows.length > 0) tbody.deleteRow(-1);
  syncYamlFromForm();
}

function pyErrMsg(e) {
  const lines = (e.message || String(e)).split('\n').map(l => l.trim()).filter(Boolean);
  return lines[lines.length - 1] || String(e);
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
  await applyYamlText(yamlText);
}

// Parse → validate → build the system in Pyodide → re-render.
// Structural validation (required fields, equilibrium sort, sum-to-100,
// tie_lines monotonicity) lives in validate_system.py — the same module the
// GitHub Action uses to check system-submission issues — so there's one
// canonical rulebook instead of parallel JS/Python checks drifting apart.
async function applyYamlText(yamlText) {
  setSysMsg('', '');

  let sysData;
  try {
    sysData = jsyaml.load(yamlText);
  } catch (e) {
    setSysMsg('YAML parse error: ' + e.message, 'error'); return;
  }
  if (sysData == null) {
    setSysMsg('YAML is empty.', 'error'); return;
  }

  pyodide.globals.set('_val_json', JSON.stringify(sysData));
  const errsJson = await pyodide.runPythonAsync(`
import json, validate_system
json.dumps(validate_system.validate(json.loads(_val_json)))
`);
  const valErrors = JSON.parse(errsJson);
  if (valErrors.length > 0) {
    const sortErr = valErrors.find(e => e.startsWith('SORT:'));
    setSysMsg(sortErr ? sortErr.slice(5) + ' Please sort before applying.' : valErrors[0], 'error');
    return;
  }

  const p = sysData.properties;
  setSysMsg('Applying systems…', '');
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
    document.getElementById('panel-fig3')?.classList.remove('has-data');
    document.getElementById('panel-fig_sf')?.classList.remove('has-data');
    document.getElementById('panel-fig_feed')?.classList.remove('has-data');
    const _ce = document.getElementById('corr-chart');
    if (_ce) { try { Plotly.purge(_ce); } catch(e) {} }
    const _se = document.getElementById('selectivity-chart');
    if (_se) { try { Plotly.purge(_se); } catch(e) {} }
    const _pe = document.getElementById('plait-chart');
    if (_pe) { try { Plotly.purge(_pe); } catch(e) {} }
    const _sftrend = document.getElementById('sf-trend-chart');
    if (_sftrend) { try { Plotly.purge(_sftrend); } catch(e) {} }
    const _feedtrend = document.getElementById('feed-trend-chart');
    if (_feedtrend) { try { Plotly.purge(_feedtrend); } catch(e) {} }
    _corrStats = null;
    _corrActive = 'ot';
    _selStats = null;
    _plaitStats = null;
    _conjPlaitByMethod = null;
    _conjMethod = 'diagonal';
    const _ps = document.getElementById('plait-stats');
    if (_ps) _ps.innerHTML = '';
    document.querySelectorAll('.corr-tab').forEach(b => {
      const sel = b.dataset.model === 'ot';
      b.classList.toggle('active', sel);
      b.setAttribute('aria-selected', sel);
    });
    document.querySelectorAll('.conj-method-tab').forEach(b => {
      const sel = b.dataset.method === 'diagonal';
      b.classList.toggle('active', sel);
      b.setAttribute('aria-selected', sel);
    });
    if (activeTab !== 'guide' && activeTab !== 'system') {
      document.getElementById('empty').style.display = 'flex';
    }
    await renderSystemFigs();
    setSysMsg('System applied.', 'success');
    return true;

  } catch (e) {
    setSysMsg('Failed to build system: ' + pyErrMsg(e), 'error');
    return false;
  }
}

// ── Guide ──────────────────────────────────────────────────────────────────
let guideLoaded = false;
async function loadGuide() {
  if (guideLoaded) return;
  const el = document.getElementById('plot-guide');
  el.innerHTML = '<div style="padding:20px;color:var(--muted);font-size:13px">Loading guide…</div>';
  try {
    const resp = await fetch('/docs/guide.md', { cache: 'no-store' });
    if (!resp.ok) throw new Error('guide.md not found');
    let md = await resp.text();
    let sysYaml = '# (system file unavailable)';
    try {
      const yr = await fetch('/systems/bp_pa_w_snu_cbe.yaml', { cache: 'no-store' });
      if (yr.ok) sysYaml = (await yr.text()).trim();
    } catch (e) { console.error('Guide system YAML:', e); }
    md = md.replace('{{SYSTEM_YAML}}', () => sysYaml);
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
      else if (activeTab === 'fig_sf') { if (cache.fig_sf_trend) _renderSfTrendChart(); }
      else if (activeTab === 'fig_feed') { if (cache.fig_feed_trend) _renderFeedTrendChart(); }
    } else {
      // Mobile/tablet: re-render active ternary chart on orientation/resize.
      // (Desktop relies on responsive:true ResizeObserver; switchTab() handles switch-back-after-resize.)
      const ternaryTabs = ['fig1', 'fig2a', 'fig2b', 'fig3', 'fig4'];
      if (ternaryTabs.includes(activeTab) && cache[activeTab]) {
        const chartEl = document.getElementById('chart-' + activeTab) || document.getElementById('plot-' + activeTab);
        if (chartEl?.data) Plotly.react(chartEl, _figData(activeTab), patchedLayout(cache[activeTab].layout), PLOTLY_CFG);
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
_setDataTrigger(activeTab in DATA_PANEL_TABS, DATA_PANEL_TABS[activeTab]);
