# CBPL-kit Roadmap

## Vision

An interactive web toolkit for SNU CBE lab experiments: runs in the browser
with no installation, customizable with your own experimental data, and easy
to hand off to next year's students.

---

## Deployment

| Channel | URL | Status |
|---------|-----|--------|
| Web app (Vercel) | https://cbpl-kit.vercel.app | Live (main branch) |
| Source | https://github.com/justinp54/CBPL-kit | Public |
| Zenodo DOI | — | Pending — see Phase 4 |

**Architecture:** Pyodide — Python runs entirely in the browser (no server,
no cold start). Python modules served from `public/exp06/`.

> ⚠ `public/exp06/*.py` and `experiments/experiment_06/*.py` must be kept
> in sync. After editing experiment modules, copy to `public/exp06/` and run
> `python scripts/check_dual_copy.py` (CI enforces it).
>
> **Status: temporary.** This rule exists only because there is no build step.
> Phase 7 replaces it with a real Python package — see 7.4. Until then the rule
> is fully binding; do not weaken it, and do not build new tooling around it.

---

## Experiment Status

| Experiment | Python Modules | Web App | Notebook |
|------------|---------------|---------|----------|
| Exp 06 — LLE Hunter-Nash | Done | **Live** | `demo.ipynb` (partial) |
| Exp 04 — VLE (Modified Raoult / PR EOS) | Done | Not started | `exp_05.ipynb` (partial) |
| Exp 05 — McCabe-Thiele Distillation | Done | Not started | `test.ipynb` |
| Exp 01, 02, 03 | Not started | — | — |

---

## Phase 1 — Documentation ✓ Completed

- [x] Extract coding patterns → 이후 `AGENTS.md`의 Patterns 절로 흡수됨
      (원래 산출물 `CBPL_PATTERNS.md`는 untracked였고, README가 그 파일을 링크해
      clone 시 깨진 링크가 되어 있었다)
- [x] Write `ROADMAP.md`

## Phase 2 — Experiment 06 Web App ✓ Completed

- [x] Modular Python package (equilibrium, conjugate, hunter_nash, lever_rule, plot_util)
- [x] Pyodide deployment on Vercel (browser-side Python, no server)
- [x] Real-time S:F Explorer — slider computes single frame instantly (~20ms)
- [x] Real-time Feed Explorer — same approach
- [x] Auto-recalculate on sidebar input change (250ms debounce)
- [x] Number inputs + sliders for all parameters
- [x] Legend moved outside ternary for clean layout
- [x] `StreamPoints` dataclass, `conjugate.py` ValueError on solver failure
- [x] `experiments/experiment_04/__init__.py` added

## Phase 3 — Multi-System & Onboarding ✓ Completed

- [x] **Guide tab** — `public/docs/guide.md` rendered via marked.js; default active tab
  on load so users read usage instructions while Pyodide initialises
- [x] **System ✦ tab** — YAML textarea + Apply System; js-yaml parses in JS,
  rebuilds `EquilibriumSystem` + `ConjugateCurve` in Pyodide
- [x] **YAML system definition** — `systems/bp_pa_w_snu_cbe.yaml` covers equilibrium
  data, tie lines, and physical properties; human-editable without touching Python
- [x] **config.py → YAML** — thermodynamic data loaded from YAML; only experiment
  defaults (V_R0, V_E1, V_RN, flow rates) remain hardcoded in config.py
- [x] **`EquilibriumSystem.from_yaml()`** — classmethod for Python / Jupyter users
- [x] **Robustness fixes** — equilibrium data auto-sorted by ternary x; near-duplicate
  point detection with clear error
  - ~~conjugate polynomial degree auto-fallback (4→3→2)~~ — **superseded.** The polyfit
    approach was replaced by branch-Hermite + clamped-tangent extension (see 6.4);
    `conjugate.py` no longer has a polynomial degree at all.

## Phase 4 — Paper Preparation (next)

Target journal: *Education for Chemical Engineers* (Elsevier). The guide for authors
does **not** mandate a code-availability section, but its own software-reference example
is a Zenodo DOI, and this is a tool paper — if the artifact rots, the paper's value goes
with it. So the DOI is optional-but-worth-it, not a formality.

**Archive scope.** The Zenodo snapshot is a curated subset of `main`, not a mirror:

| Excluded from archive | Why |
|---|---|
| `experiments/experiment_04`, `experiment_05` | Not described in the paper |
| Contact tab personal data (student IDs, emails, photo, LinkedIn) | A Zenodo record is permanent and cannot be deleted |
| `paper/` | Already untracked |

The live site keeps all of it — only the archive is pruned. This is legitimate because
none of it touches computation; disclose it in one sentence in the paper and it reads as
curation rather than discrepancy.

**Invariant:** `public/exp06/*.py`, `experiments/experiment_06/*.py`, and
`public/systems/*.yaml` must be byte-identical between the archive and the site at
submission time. That is the whole reproducibility surface. Run
`scripts/check_dual_copy.py` before tagging.

- [ ] **`SOURCES.md`** — full citation for each bundled system (7 of 8 are from
      Treybal 1980 / Seader 2006 / Lee 1988). Current `note:` fields are dropdown
      labels, not attributions — no edition, page, or table number.
- [ ] **`refs.bib`** — add Treybal, Seader, Lee entries (currently missing entirely)
- [ ] **README licence note** — code is MIT; bundled equilibrium data is not ours to
      relicense, point at `SOURCES.md`
- [ ] **`CITATION.cff`** — machine-readable citation (GitHub "Cite this repo" button)
- [ ] **`.zenodo.json`** — authors, ORCIDs, keywords, licence. Without it Zenodo
      derives authorship from the GitHub account name.
- [ ] **`scripts/make_release_snapshot.py`** — deterministic prune → release branch,
      so the exclusions above are reproducible rather than hand-repeated each version
- [ ] **Reserve DOI on Zenodo** *before* final submission, so the real DOI can go in
      the manuscript
- [ ] **Connect Zenodo → toggle repo ON → then `git tag v1.0.0` + GitHub Release**
      (releases created before the toggle are not captured)
- [ ] **README + Contact tab** — DOI badge and version, so a visitor can tell which
      site state corresponds to the archive
- [ ] **Re-shoot paper screenshots** if any figure shows a tab absent from the archive

Cite the **concept DOI** (all versions) in the paper, not a version DOI.

## Phase 5 — Future Features

- [x] ~~**Conjugate curve degree adaptive** — auto-set `degree = min(4, n_ties)` at init~~
  — **obsolete.** Written against the polyfit implementation, which no longer exists.
- [ ] **Exp 04 web app** — VLE simulator (Python done, needs Plotly UI)
- [ ] **Exp 05 web app** — McCabe-Thiele (image digitization → canvas click)
- [ ] **Landing page** — experiment selector when multiple apps exist
- [ ] **Service Worker caching** — eliminate 20 s Pyodide cold start on repeat visits

---

## Phase 6 — Data Quality, Analysis & UX (planned 2026-06)

이 phase는 평형 데이터의 **신뢰도 검증** (tie-line consistency), **곡선 피팅
robustness** (conjugate smoothing), 그리고 **사용성** (data panel, guide, system
selection) 세 갈래를 함께 다룬다. 6개 feature는 의존성에 따라 묶여 있으므로 아래
"권장 우선순위"를 따른다.

### 6.1 — Data Panel 구조화 (Equilibrium 탭 내부 sub-tab) — ✓ Completed

> 구현됨. `DATA_PANEL_TABS` (app.js)가 figure 탭별 패널을 매핑하고,
> `panel-fig1`(Equilibrium) 안에 correlation sub-tab이 들어 있다.
> (아래 원래 스코프는 이력 참고용으로 유지)

- **설명**: 현재 Equilibrium 탭의 340px 사이드 패널은 tie line 조성 표 하나만
  담고 있다. 앞으로 추가될 correlation plot, 전체 binodal 데이터 표를 수용하려면
  패널 내부에 sub-tab 구조가 필요하다. 이 feature는 자체 가치보다 **6.2/6.3의
  그릇** 역할이 크므로 먼저 구축한다.
  - `Tie Lines` — 현재 조성 표 (done, 이전으로 이동)
  - `Equil. Data` — 전체 binodal curve 데이터 표 (`equilibrium_data` 3-component)
  - `Correlations` — Othmer-Tobias + Bachman plot + 파라미터 (6.2에서 채움)
- **구현 방향**: 기존 탭 시스템과 동일한 JS show/hide 패턴을 패널 안에 한 단계
  중첩. 패널은 `overflow-y: auto`로 스크롤 가능하게, mini Plotly chart는 300px
  width로 렌더 (검증된 사이즈). Responsive: `< 1024px`에서 패널 숨김 (기존 동작
  유지). Python 변경 없음 — `EquilibriumSystem`이 이미 보유한 데이터를 표로 출력.
- **의존성**: 없음. 6.2와 6.4의 **전제 조건**.
- **복잡도**: **Low** (순수 프론트엔드, 기존 패턴 재사용)

### 6.2 — Tie-Line Consistency Analysis (Othmer-Tobias / Bachman) — ✓ Completed (스코프 초과 달성)

> `correlation.py`로 구현됨. 계획된 Othmer-Tobias / Bachman에 더해 **Hand** 상관식과
> **selectivity (D₁, D₂, S)** 까지 포함하며, Hand 좌표는 Treybal 방식의 plait point
> 추정에도 쓰인다 (`compute_plait_loglog`). UI는 `panel-fig1` 안 3개 sub-tab
> (Othmer-Tobias / Hand / Bachman) + KaTeX 수식.
> (아래 원래 스코프는 이력 참고용으로 유지)

- **설명**: tie-line 데이터의 열역학적 일관성을 정량 평가하는 표준 상관식.
  실험 데이터의 신뢰도를 보여주는 지표로 논문/보고서에 자주 인용된다.
  - **Othmer-Tobias**: `ln((1-w_carrier)/w_carrier)` vs `ln((1-w_solvent)/w_solvent)`
    → 선형 회귀. carrier-rich 상의 carrier 분율과 solvent-rich 상의 solvent 분율
    사용.
  - **Bachman**: `w_carrier` vs `w_carrier/w_solvent` → 선형 회귀.
  - 각각 R², SD, 파라미터 (기울기 a, 절편 b) 표시 + mini Plotly scatter+fit line.
  - 일관성이 높으면 R² → 1. 낮으면 데이터 품질 의심 (→ 6.3 outlier 연결).
- **구현 방향**: tie line 양 상의 조성은 이미 추출되어 있음 (`tie_lines` +
  binodal 보간으로 conjugate 계산 시 사용하는 값 재활용). Pyodide에 numpy /
  `scipy.stats.linregress` 사용 가능. Python 쪽에 순수 계산 함수 추가
  (예: `equilibrium.py` 또는 신규 `correlations.py`) → 파라미터 dict 반환.
  plot은 `plot_util.py`에 builder 추가. UI는 6.1의 `Correlations` sub-tab에 표시.
- **의존성**: **6.1** (표시할 패널 구조). tie-line 조성 추출 로직 재사용.
- **복잡도**: **Medium** (계산은 단순하나 양 상 조성 정확 추출 + 2개 plot + 패널
  통합)

### 6.3 — Tie-Line Outlier Detection — ✗ Dropped (2026-07-13)

> 결정: 진행하지 않음. Othmer-Tobias/Bachman correlation 자체가 근사식이라
> 그 회귀 잔차 기반 outlier 판정의 신뢰도가 낮고, 투자 대비 가치가 없다고 판단.
> (아래 원래 스코프는 참고용으로 유지)

- **설명**: 6.2의 회귀선을 기준으로 이상치 tie-line을 통계적으로 탐지·시각화.
  실험 측정 오류를 잡아내고, conjugate 곡선의 kink (6.4) 원인을 진단한다.
  - **Studentized residuals**: `|residual| > 2σ` → 의심 점 (numpy만으로 가능).
  - **Cook's distance**: 회귀선에 대한 영향도(leverage) 측정.
  - **Leave-one-out**: 각 점을 하나씩 제거 후 R² 개선폭 확인 → 큰 개선 = 이상치.
  - correlation plot과 **ternary diagram 양쪽**에 의심 점 강조 표시.
- **구현 방향**: 6.2의 회귀 결과 위에 잔차 통계 계산 (numpy). 탐지된 인덱스를
  JS로 넘겨 Plotly trace에 별도 marker(빨강/테두리)로 overlay. **Consider**:
  사용자가 outlier 제안을 accept/reject 하는 UI (체크박스) → reject 시 6.2 회귀와
  6.4 fitting에서 해당 점 제외. 단순 1차 버전은 "표시만" → 추후 accept/reject 확장.
- **의존성**: **6.2** (회귀 결과 필요), ternary plot trace 접근 (6.1/기존 plot).
  accept/reject UI는 **6.4**와 데이터 흐름 공유.
- **복잡도**: **Medium** (통계는 표준, accept/reject 상태 관리 시 Medium-High)

### 6.4 — Conjugate Curve Smoothing / MAKIMA 전환 — ✓ Resolved (다른 방식으로)

> 이 항목은 옛 polyfit 기반 코드 기준으로 작성됨. 이후 plait-point 탐색이
> clamped-tangent extension 방식으로 교체되어(커밋 b5c8eb1, 498c00d) kink 문제가
> 해소됨 — MAKIMA 전환 불필요. 현재 conjugate 곡선은 branch-Hermite 기반.
> (아래 원래 스코프는 이력 참고용으로 유지)

- **설명**: 현재 conjugate 표시 곡선은 aux intersection point 위에 PCHIP을
  올리는데, 데이터에 outlier가 있으면 **날카로운 kink**가 생긴다. CLAUDE.md에
  이미 `polyfit degree 4 → MAKIMA 전환 검토 중`으로 기록됨. 이 변경은 plait
  point 계산에 영향을 주고, plait point는 다시 Hunter-Nash 단계 수(N_theory)에
  영향을 주므로 **가장 알고리즘적으로 민감한 작업**이다.
- **구현 방향** (옵션 평가 후 택1 또는 조합):
  1. **MAKIMA interpolation** (`scipy.interpolate.Akima1DInterpolator`,
     `method="makima"`) — PCHIP보다 부드럽고 oscillation 적음.
  2. **Smoothing spline** (`UnivariateSpline` + smoothing factor `s`) — `s`로
     데이터 추종/평활 trade-off 조절, 노이즈 흡수에 강함.
  3. **Outlier aux point 제거 후 fitting** — 6.3 결과로 의심 점을 빼고 곡선 피팅.
  - **검증 필수**: 변경 전후로 (a) plait point 좌표, (b) 대표 시스템의 N_theory,
    (c) `intersect_line()` 부호 반전 스캔 결과를 비교. 회귀가 없는지 확인 후 반영.
    가능하면 기존 PCHIP과 신규 곡선을 토글로 비교 (개발용).
- **의존성**: **6.3** (옵션 3은 outlier 정보 필요). Hunter-Nash / plait point
  로직과 강결합 → 단독 변경 위험.
- **복잡도**: **High** (수치적 민감, downstream 영향 광범위, 검증 비용 큼)

### 6.5 — Guide 콘텐츠 작성 (`public/docs/guide.md`) — ◐ 대부분 완료

> `guide.md` 121줄 작성됨: Overview, Quick Start, Sidebar Inputs, Figure Tabs(탭별
> 설명), System Configuration, Tips. 적정 공식(`c = 0.05 × V`)도 포함.
> **남은 것**: (a) LLE 기초 이론(ternary diagram 읽는 법, phase equilibrium 개념)이
> 얕음 — 사용법 위주로만 쓰여 있음. (b) **탭 이름이 stale** — `### Tie Lines`로
> 되어 있으나 실제 탭 라벨은 `Stages`. 사용자용 문서라 우선 수정 대상.

- **설명**: 코드가 아닌 **콘텐츠 작업**. 내년 학생 인수인계를 위한 핵심.
  marked.js로 렌더되는 Guide 탭을 채운다.
  - LLE 기초 (ternary diagram 읽는 법, phase equilibrium 개념)
  - Hunter-Nash method 단계별 설명 (operating point, tie line stepping)
  - Workflow guide ("이 탭들을 순서대로 따라가세요")
  - 적정 공식 유도 (`c = 0.05 × V × f`의 배경: 0.1 mol/L NaOH, 2 mL 시료)
- **구현 방향**: 순수 markdown 편집. 다이어그램은 앱 스크린샷 또는 텍스트 설명.
  코드 변경 없음. 다른 feature와 **병렬 진행 가능** (의존성 없음).
- **의존성**: 없음 (앱 기능이 안정된 뒤 작성하면 정확도↑).
- **복잡도**: **Low** (단, 정확한 설명을 쓰려면 도메인 시간 투자 필요)

### 6.6 — System Selection UX (YAML dropdown) — ✓ Completed

> `public/systems/index.json` manifest + dropdown 구현됨. 라벨은 `components` + `note`
> 에서 자동 생성. form 에디터(`.sys-form-*`)와 raw YAML textarea 모두 존재.
> 번들 시스템 8개(자체 측정 1 + 문헌 7).
> (아래 원래 스코프는 이력 참고용으로 유지)

- **설명**: 현재 System 탭은 raw YAML textarea (power-user용). 일반 사용자는
  `/systems/`에 있는 미리 정의된 시스템을 dropdown으로 선택하길 원한다.
  - dropdown: `/systems/`의 사용 가능한 YAML 파일 목록에서 선택 → 자동 Apply.
  - (선택) form 기반 에디터: 간단한 파라미터(물성, 라벨)만 폼으로 수정.
  - raw YAML editor는 "Advanced" 옵션으로 유지 (제거하지 않음).
- **구현 방향**: `/systems/` 파일 목록을 정적 manifest(예: `systems/index.json`)
  로 관리하거나 빌드 시 생성 (브라우저는 디렉터리 listing 불가). dropdown 선택 →
  해당 YAML fetch → 기존 `applySystem()` 재사용. form 에디터는 별도 단계로 분리.
- **의존성**: 없음 (기존 `applySystem()` 활용). 신규 시스템 YAML 추가와 시너지.
- **복잡도**: **Low** (dropdown만) / **Medium** (form 에디터 포함 시)

### Phase 6 결산

6개 항목 전부 결론이 났다. Phase 6은 종료.

| Feature | 결과 |
|---------|------|
| 6.1 Data Panel 구조화 | ✓ 완료 |
| 6.2 Othmer-Tobias / Bachman | ✓ 완료 (+ Hand, selectivity 추가 달성) |
| 6.3 Outlier Detection | ✗ Dropped (2026-07-13) — 근사식의 잔차 기반 판정은 신뢰도 낮음 |
| 6.4 Conjugate Smoothing | ✓ 다른 방식으로 해소 — clamped-tangent extension (MAKIMA 불필요) |
| 6.5 Guide 콘텐츠 | ◐ 대부분 완료 — LLE 이론 보강 + 탭 이름 stale 수정 남음 |
| 6.6 System dropdown | ✓ 완료 |

**이월 항목** (Phase 4/7로 넘김):
- `guide.md`의 `Tie Lines` → `Stages` 탭 이름 수정 (사용자용 문서 오류)
- `guide.md`에 LLE 기초 이론 보강

---

## Design Constraints

- **Browser-first**: Pyodide runs Python client-side; no server dependency
- **ASCII-only** Python source (no Korean comments in `.py` files)
- **Config is overridable** — titration volumes / flow rates in `config.py`
- **Plot functions return figures** — never call `.show()` inside
- **Pinned CDN dependencies** — every external JS/CSS in `index.html` is version-pinned
  with an SRI hash. Never loosen to `@latest`; the pinning is what makes an archived
  snapshot reproducible years later.
- **public/exp06/ sync** — always copy edited modules before committing
  (`scripts/check_dual_copy.py`, enforced by CI). *Temporary — removed in Phase 7.4.*

---

## Phase 7 — Multi-Experiment Architecture

현재 `public/index.html`이 Exp06 전용 SPA. 다른 실험(Exp04, Exp05 등)을 추가하려면 멀티페이지 구조로 전환 필요.

### 7.1 Target Structure

```
public/
  index.html              ← 랜딩 페이지 (실험 선택)
  shared/
    style.css             ← 공통 CSS 토큰 (palette, fonts, layout)
    components.css        ← 공통 컴포넌트 (header, tabs, sidebar)
  exp06/
    index.html            ← LLE Hunter-Nash (현재 public/index.html 이동)
    *.py                  ← Python 모듈 (현재와 동일)
    systems/              ← YAML 시스템 정의
  exp04/
    index.html            ← 별도 실험 SPA
    *.py
  exp05/
    index.html
    *.py
```

### 7.2 Migration Steps

1. 공통 CSS를 `public/shared/style.css`로 추출 (`:root` 변수, header, tab, sidebar 스타일)
2. 현재 `public/index.html` → `public/exp06/index.html`로 이동
3. 새 `public/index.html`에 랜딩 페이지 작성 (실험 목록, 카드 또는 리스트)
4. `vercel.json` rewrites를 실험별 경로로 수정
5. 각 실험 SPA는 `shared/style.css`를 import하여 디자인 일관성 유지

### 7.3 Mobile/Tablet Improvements

| 항목 | 현재 | 개선 방향 |
|------|------|----------|
| 그래프 크기 | Plotly responsive, 고정 비율 | 모바일에서 legend 숨기기, margin 축소 |
| 데이터 패널 | 1024px 이하 숨김 | 차트 아래로 스택 옵션 |
| System 폼 | 그리드 고정 | 768px 이하에서 1열로 접기 |
| 터치 타겟 | 일부 44px 미달 | 슬라이더, 버튼 최소 크기 점검 |
| 세로 스크롤 | body overflow:hidden | 모바일에서 figure-area 스크롤 허용 |

**복잡도**: Medium  
**우선순위**: Phase 6 이후, 다른 실험 추가 필요 시점에 착수

### 7.4 Python 패키지화 — dual-copy 제거

**동기**: `public/exp06/` 와 `experiments/experiment_06/` 를 손으로 동기화하는 현재
구조는 실험이 하나일 때만 버틴다. 실험이 3~4개로 늘면 복사 대상이 배로 늘고, 계산
로직의 정본이 어디인지 불분명해진다. 지금은 `scripts/check_dual_copy.py` + CI가
사고를 막아주고 있을 뿐 근본 해결이 아니다.

**방향**: 계산 모듈을 설치 가능한 Python 패키지(`cbpl`)로 만들고, 웹앱은 복사본이
아니라 그 패키지를 소비하게 한다. **정본은 한 곳**이 된다.

**미결 사항** (착수 시 결정):

| 결정할 것 | 후보 |
|---|---|
| 브라우저가 패키지를 얻는 방법 | PyPI 배포 후 `micropip.install()` / 빌드 시 wheel을 정적 자산으로 번들 |
| 프론트엔드 빌드 도입 여부 | Vite 등 도입 (멀티 실험 페이지·공통 CSS와 시너지) / 무빌드 유지 |
| 배포 단위 | 실험별 패키지 / `cbpl.exp06` 서브패키지 하나로 |

`micropip` 경로는 무빌드라는 현재 장점을 지키지만 릴리스마다 PyPI 배포가 필요하고,
버전이 사이트와 어긋날 수 있다. 번들 경로는 빌드 스텝을 도입하지만 사이트와 코드
버전이 항상 일치한다 — **아카이브 재현성 측면에서는 후자가 유리하다**.

**전제 조건**: 7.1~7.2 멀티 실험 구조 전환과 함께 진행하는 것이 자연스럽다.
단독으로 먼저 하면 이득 대비 이행 비용이 크다.

**제거 대상** (완료 시): dual-copy 규칙, `scripts/check_dual_copy.py`, CI의 해당
스텝, 그리고 `CLAUDE.md` / `AGENTS.md` / 이 문서의 `Status: temporary` 표시 전부.

**복잡도**: High  
**우선순위**: 논문 제출(Phase 4) 이후. 릴리스 아카이브 직전에 구조를 흔들지 말 것.

---

## How to Run Locally

```bash
# Start dev server
python dev_server.py 8080
# Open http://localhost:8080
```

## How to Update Deployed Python Modules

```bash
# After editing experiments/experiment_06/*.py:
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,correlation,hunter_nash,lever_rule,plot_util,validate_system}.py public/exp06/
python scripts/check_dual_copy.py     # must print OK
git add public/exp06/ experiments/experiment_06/
git commit -m "..."
git push origin main
```

*이 절차는 Phase 7.4에서 사라진다.*
