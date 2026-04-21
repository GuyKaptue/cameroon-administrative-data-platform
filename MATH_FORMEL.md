You’ve basically built the ingredients of a serious demographic engine already—what’s missing now is the **explicit calibration objective** and how all these parameters plug into the simulation from **2005 → 2025**.

I’ll give you a **tight, mathematical calibration model** that uses exactly the objects in `optimized_parameters.py` and your hierarchy (country → region → department → arrondissement → village).

---

## 1. Core simulation structure (2005 → 2025)

Let:

- \( t \in \{2005,\dots,2025\} \)
- \( r \): region, \( d \): department, \( a \): arrondissement, \( v \): village

You already have:

- **UN national targets**:
  \[
  P_c^{\text{UN}}(t) \in \texttt{UN\_POPULATION\_TARGETS}
  \]
- **Period growth rates** (national):
  \[
  g_c^{\text{period}} \in \texttt{PERIOD\_GROWTH\_RATES}
  \]
- **Urbanization targets**:
  \[
  U_c(t) \in \texttt{URBANIZATION\_TARGETS}
  \]
- **Regional multipliers**:
  \[
  m_r \in \texttt{REGIONAL\_MULTIPLIERS\_OPTIMIZED}
  \]
- **Regional fertility indices**:
  \[
  f_r^{\text{fert}} \in \texttt{REGIONAL\_FERTILITY\_INDICES}
  \]
- **Regional mortality indices**:
  \[
  f_r^{\text{mort}} \in \texttt{REGIONAL\_MORTALITY\_INDICES}
  \]
- **Regional urbanization baseline**:
  \[
  U_r(2005) \in \texttt{REGIONAL\_URBANIZATION\_2005}
  \]
- **Model parameters**:
  \[
  \alpha_{\text{fert}}, \alpha_{\text{mort}}, \alpha_{\text{urban}}, \gamma_{\text{urban}}, \delta_{\text{rural}}, \delta_{\text{increase}} \in \texttt{MODEL\_PARAMETERS}
  \]

And **true census** at arrondissement level:

- \(P_a(2005)\), \(P_a(2010)\) from `get_arrondissement_population_2005/2010()`
- Derived growth factors from `calculate_arrondissement_growth_rates()`.

---

## 2. National growth factor

From UN targets:

\[
G_c(t) = \frac{P_c^{\text{UN}}(t+1)}{P_c^{\text{UN}}(t)}
\]

This is the **hard constraint** for the whole system.

---

## 3. Regional growth factor (using your parameters)

For each region \(r\) and year \(t\):

### 3.1 Regional urbanization path

Approximate linear trend from 2005:

\[
U_r(t) = U_r(2005) + \beta_r \cdot (t - 2005)
\]

where \(\beta_r\) is chosen so that the **population‑weighted national urbanization** matches \(U_c(t)\):

\[
\frac{\sum_r U_r(t) \cdot P_r(t)}{\sum_r P_r(t)} \approx U_c(t)
\]

(You can solve \(\beta_r\) numerically or keep them as calibration parameters.)

### 3.2 Raw regional growth factor

Use your indices and model parameters:

\[
G_r^{\text{raw}}(t) = G_c(t) \cdot
\underbrace{\left[1 + \alpha_{\text{fert}} \cdot (f_r^{\text{fert}} - 1)\right]}_{\text{fertility}}
\cdot
\underbrace{\left[1 - \alpha_{\text{mort}} \cdot (f_r^{\text{mort}} - 1)\right]}_{\text{mortality}}
\cdot
\underbrace{\left[1 + \alpha_{\text{urban}} \cdot (U_r(t) - U_c(t))\right]}_{\text{urbanization}}
\cdot
\underbrace{m_r}_{\text{regional multiplier}}
\]

So you’re explicitly using:

- `alpha_fert`, `alpha_mort`, `alpha_urban`
- `REGIONAL_FERTILITY_INDICES`
- `REGIONAL_MORTALITY_INDICES`
- `REGIONAL_URBANIZATION_2005` + trend
- `REGIONAL_MULTIPLIERS_OPTIMIZED`

### 3.3 Regional update + national rescaling

Pre‑update:

\[
\tilde{P}_r(t+1) = P_r(t) \cdot G_r^{\text{raw}}(t)
\]

Rescale to match UN national total:

\[
P_r(t+1) = \tilde{P}_r(t+1) \cdot
\frac{P_c^{\text{UN}}(t+1)}{\sum_{r'} \tilde{P}_{r'}(t+1)}
\]

---

## 4. Department and arrondissement levels

### 4.1 Department growth

Let department \(d\) belong to region \(r\).

You can define:

\[
G_d(t) = G_r^{\text{raw}}(t) \cdot F_d^{\text{city}} \cdot F_d^{\text{rural}}
\]

Where:

- \(F_d^{\text{city}} > 1\) if \(d\) contains a major city in `CITY_DEPARTMENT_MAP`
- \(F_d^{\text{rural}} < 1\) for highly rural departments (you can derive a rurality index from share of villages vs towns)

Update + rescale within region:

\[
\tilde{P}_d(t+1) = P_d(t) \cdot G_d(t)
\]
\[
P_d(t+1) = \tilde{P}_d(t+1) \cdot
\frac{P_r(t+1)}{\sum_{d' \in \mathcal{D}_r} \tilde{P}_{d'}(t+1)}
\]

### 4.2 Arrondissement growth (using `gamma_urban`)

Let \(U_a\) be an arrondissement urbanization index (0–1). For arrondissement \(a\) in department \(d\):

\[
G_a(t) = G_d(t) \cdot \left[1 + \gamma_{\text{urban}} \cdot (U_a - \bar{U}_d)\right]
\]

Update + rescale within department:

\[
\tilde{P}_a(t+1) = P_a(t) \cdot G_a(t)
\]
\[
P_a(t+1) = \tilde{P}_a(t+1) \cdot
\frac{P_d(t+1)}{\sum_{a' \in \mathcal{A}_d} \tilde{P}_{a'}(t+1)}
\]

---

## 5. Village level and rural decline (using `delta_rural`)

For village \(v\) in arrondissement \(a\):

- Let \(R_v \in [0,1]\) be a rurality index (1 = very rural).
- Let:
  \[
  \delta_{\text{rural}}(t) = \delta_{\text{rural}} + \delta_{\text{increase}} \cdot (t - 2005)
  \]

Then:

\[
G_v(t) = G_a(t) \cdot \left[1 - \delta_{\text{rural}}(t) \cdot R_v\right]
\]

Update + rescale within arrondissement:

\[
\tilde{P}_v(t+1) = P_v(t) \cdot G_v(t)
\]
\[
P_v(t+1) = \tilde{P}_v(t+1) \cdot
\frac{P_a(t+1)}{\sum_{v' \in \mathcal{V}_a} \tilde{P}_{v'}(t+1)}
\]

---

## 6. City constraints (using `MAJOR_CITIES_2025`)

For each city \(m\) with target \(P_m^{\text{obs}}(2025)\):

1. Define the set of units (villages/arrondissements) \(\mathcal{V}_m\) composing the agglomeration.
2. Compute simulated city population:

   \[
   \hat{P}_m(2025) = \sum_{v \in \mathcal{V}_m} P_v(2025)
   \]

3. Define city correction factor:

   \[
   \lambda_m = \frac{P_m^{\text{obs}}(2025)}{\hat{P}_m(2025)}
   \]

4. Apply a **per‑year correction** over 2015–2025:

   \[
   G_v^{\text{city}}(t) = G_v(t) \cdot \lambda_m^{1/10}, \quad v \in \mathcal{V}_m
   \]

Then re‑run the simulation with these adjusted growth factors (keeping the rescaling steps).

---

## 7. Calibration / optimization problem

You now **optimize** the parameters in `MODEL_PARAMETERS` and possibly `REGIONAL_MULTIPLIERS_OPTIMIZED` to minimize a global loss.

### 7.1 Decision variables

- \(\theta = \{\alpha_{\text{fert}}, \alpha_{\text{mort}}, \alpha_{\text{urban}}, \gamma_{\text{urban}}, \delta_{\text{rural}}, \delta_{\text{increase}}, m_r\}\)

### 7.2 Loss components

1. **National totals (hard constraint, should be near 0)**
   \[
   L_{\text{national}} = \sum_{t} \left( \frac{\hat{P}_c(t) - P_c^{\text{UN}}(t)}{P_c^{\text{UN}}(t)} \right)^2
   \]

2. **Regional 2026 targets** (`REGIONAL_TARGETS_2026`):
   \[
   L_{\text{regional}} = \sum_r \left( \frac{\hat{P}_r(2026) - P_r^{\text{target}}(2026)}{P_r^{\text{target}}(2026)} \right)^2
   \]

3. **Urbanization path** (`URBANIZATION_TARGETS`):
   \[
   \hat{U}_c(t) = \frac{\sum_v U_v P_v(t)}{\sum_v P_v(t)}
   \]
   \[
   L_{\text{urban}} = \sum_t \left( \hat{U}_c(t) - U_c(t) \right)^2
   \]

4. **Arrondissement 2005–2010 growth** (using `calculate_arrondissement_growth_rates()`):
   Let \(g_a^{\text{obs}}\) be observed annual rate, \(g_a^{\text{sim}}\) simulated:

   \[
   L_{\text{arr}} = \sum_a \left( g_a^{\text{sim}} - g_a^{\text{obs}} \right)^2
   \]

5. **Major cities 2025** (`MAJOR_CITIES_2025`):
   \[
   L_{\text{cities}} = \sum_m \left( \frac{\hat{P}_m(2025) - P_m^{\text{obs}}(2025)}{P_m^{\text{obs}}(2025)} \right)^2
   \]

### 7.3 Global loss

\[
L(\theta) = w_1 L_{\text{national}} + w_2 L_{\text{regional}} + w_3 L_{\text{urban}} + w_4 L_{\text{arr}} + w_5 L_{\text{cities}}
\]

You choose weights \(w_i\) according to your priorities (e.g. national and regional stronger, then urbanization, then cities, then arrondissement growth).

You then run a **black‑box optimizer** (e.g. CMA‑ES, Bayesian optimization, or even grid/random search) over \(\theta\), using your simulator as the forward model.

######

### 1. National level (using `NATIONAL_POPULATION` and `GROWTH_RATES`)

From `config.NATIONAL_POPULATION`:

\[
P_c(t) = \texttt{NATIONAL\_POPULATION}[t]
\]

For each 5‑year period:

- Period growth rate from `config.GROWTH_RATES`:

\[
g_c^{\text{period}}(t, t+5) = \texttt{GROWTH\_RATES}["t-(t+5)"]
\]

Annualized factor:

\[
G_c^{\text{annual}}(t) = 1 + g_c^{\text{period}}(t, t+5)
\]

But the **hard constraint** is:

\[
P_c(t+5) = \texttt{NATIONAL\_POPULATION}[t+5]
\]

So all sub‑levels must sum to this.

---

### 2. Regional level (using `DEPT_POPULATION_2005` + `REGIONAL_MULTIPLIERS` or optimized ones)

1. Aggregate 2005 department totals to regions:

\[
P_r(2005) = \sum_{d \in \mathcal{D}_r} \texttt{DEPT\_POPULATION\_2005}[d]
\]

2. Base regional share:

\[
s_r(2005) = \frac{P_r(2005)}{\sum_{r'} P_{r'}(2005)}
\]

3. For each 5‑year period \(t \to t+5\):

- National period factor:

\[
F_c(t) = \frac{P_c(t+5)}{P_c(t)}
\]

- Regional multiplier (either `config.REGIONAL_MULTIPLIERS` or `REGIONAL_MULTIPLIERS_OPTIMIZED`):

\[
m_r = \texttt{REGIONAL\_MULTIPLIERS\_OPTIMIZED}[r]
\]

- Raw regional factor:

\[
\tilde{F}_r(t) = F_c(t) \cdot m_r
\]

4. Update regional populations (pre‑rescale):

\[
\tilde{P}_r(t+5) = P_r(t) \cdot \tilde{F}_r(t)
\]

5. Rescale to match national total:

\[
P_r(t+5) = \tilde{P}_r(t+5) \cdot
\frac{P_c(t+5)}{\sum_{r'} \tilde{P}_{r'}(t+5)}
\]

This uses **only**:

- `NATIONAL_POPULATION`
- `GROWTH_RATES`
- `REGIONAL_MULTIPLIERS[_OPTIMIZED]`
- `DEPT_POPULATION_2005`

---

### 3. Department level (inside each region)

1. Department share in region at base year:

\[
s_d(2005) = \frac{\texttt{DEPT\_POPULATION\_2005}[d]}{P_r(2005)}
\]

2. For each period \(t \to t+5\):

- Use **same regional factor** \(F_r(t)\) for all departments in region \(r\):

\[
\tilde{P}_d(t+5) = P_d(t) \cdot F_r(t)
\]

3. Rescale within region:

\[
P_d(t+5) = \tilde{P}_d(t+5) \cdot
\frac{P_r(t+5)}{\sum_{d' \in \mathcal{D}_r} \tilde{P}_{d'}(t+5)}
\]

This keeps:

\[
\sum_{d \in \mathcal{D}_r} P_d(t+5) = P_r(t+5)
\]

---

### 4. Arrondissement level (using 2005 & 2010 census)

You already have:

- `ARRONDISSEMENT_POPULATION_2005`
- `ARRONDISSEMENT_POPULATION_2010`
- `calculate_arrondissement_growth_rates()`

#### 4.1. 2005 → 2010 (use **observed** growth)

For arrondissement \(a\):

- From `calculate_arrondissement_growth_rates()`:

\[
g_a^{\text{obs}} = \left(\frac{P_a(2010)}{P_a(2005)}\right)^{1/5} - 1
\]

- 5‑year factor:

\[
F_a(2005) = (1 + g_a^{\text{obs}})^5
\]

- Update:

\[
\tilde{P}_a(2010) = P_a(2005) \cdot F_a(2005)
\]

Then rescale within department \(d\):

\[
P_a(2010) = \tilde{P}_a(2010) \cdot
\frac{P_d(2010)}{\sum_{a' \in \mathcal{A}_d} \tilde{P}_{a'}(2010)}
\]

This ensures arrondissement totals match department totals, which in turn match region and national.

#### 4.2. 2010 → 2015 → 2020 → 2025 (modelled growth)

For later periods, you no longer have census, so you use **department factor** plus an arrondissement modifier.

Let:

- Department factor:

\[
F_d(t) = \frac{P_d(t+5)}{P_d(t)}
\]

- Arrondissement modifier (e.g. based on 2005–2010 growth rank):

\[
M_a = \frac{g_a^{\text{obs}}}{\bar{g}_d^{\text{obs}}}
\]

Then:

\[
\tilde{F}_a(t) = F_d(t) \cdot M_a
\]

Update:

\[
\tilde{P}_a(t+5) = P_a(t) \cdot \tilde{F}_a(t)
\]

Rescale within department:

\[
P_a(t+5) = \tilde{P}_a(t+5) \cdot
\frac{P_d(t+5)}{\sum_{a' \in \mathcal{A}_d} \tilde{P}_{a'}(t+5)}
\]

---

### 5. Urbanization and validation (using `URBANIZATION_TARGETS` & thresholds)

From `URBANIZATION_TARGETS` (in `optimized_parameters.py`):

\[
U_c(t) = \texttt{URBANIZATION\_TARGETS}[t]
\]

You classify arrondissements as urban/rural (e.g. based on presence of major cities or density), then compute simulated:

\[
\hat{U}_c(t) = \frac{\sum_a U_a \cdot P_a(t)}{\sum_a P_a(t)}
\]

Validation:

- Check:

\[
\left|\frac{\hat{P}_c(t) - P_c(t)}{P_c(t)}\right| \le \texttt{VALIDATION\_THRESHOLDS["national\_diff\_percent"]} / 100
\]

- And:

\[
|\hat{U}_c(t) - U_c(t)| \le \texttt{VALIDATION\_THRESHOLDS["urbanization\_diff\_percent"]} / 100
\]

---

### 6. What this gives you

With **only the data already in `config.py` and `optimized_parameters.py`**, you now have:

- A **deterministic, hierarchical model**:
  - National → Region → Department → Arrondissement
- That:
  - Matches UN totals for 2005–2025
  - Uses true 2005 & 2010 arrondissement census
  - Propagates realistic structure to 2015, 2020, 2025
  - Is fully compatible with your existing config layout

If you want, I can now write a **`PopulationSimulator` class** that:

- Takes `config` + `optimized_parameters`
- Exposes `simulate(years=[2005,2010,2015,2020,2025])`
- Returns a tidy DataFrame with `level`, `region`, `dept`, `arrondissement`, `population`, `year`.