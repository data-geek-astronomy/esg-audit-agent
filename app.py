import gradio as gr
import json

# ── GHG Protocol emission factors ────────────────────────────────────────────
EF_ELECTRICITY  = 0.000233   # tCO2e / kWh
EF_NAT_GAS      = 0.0533     # tCO2e / MMBtu
EF_DIESEL       = 0.00268    # tCO2e / litre
EF_AIR_TRAVEL   = 0.000255   # tCO2e / km
EF_HOTEL        = 0.031      # tCO2e / night
EF_WASTE        = 0.467      # tCO2e / tonne


def calc_emissions(elec_kwh, nat_gas, diesel_l, air_km, hotel_nights, waste_t):
    scope1 = nat_gas * EF_NAT_GAS + diesel_l * EF_DIESEL
    scope2 = elec_kwh * EF_ELECTRICITY
    scope3 = air_km * EF_AIR_TRAVEL + hotel_nights * EF_HOTEL + waste_t * EF_WASTE
    return round(scope1, 2), round(scope2, 2), round(scope3, 2)


# ── Pre-computed demo company profiles ───────────────────────────────────────

DEMO_COMPANIES = [
    {
        "name": "TechCorp Inc",
        "sector": "Software & Technology",
        "scope1": 12.4,
        "scope2": 38.7,
        "scope3": 29.1,
        "revenue": 85.0,
        "renewable_pct": 72,
        "top_opportunities": [
            "Switch remaining 28% electricity to renewable PPA contracts → est. −11 tCO2e",
            "Video-first remote work policy to reduce business travel by 40% → est. −9 tCO2e",
            "Transition company fleet to BEV by 2026 → est. −6 tCO2e",
        ],
        "cdp_paragraph": (
            "TechCorp Inc reports total Scope 1+2+3 emissions of 80.2 tCO2e for the reporting year, "
            "representing a carbon intensity of 0.94 tCO2e per USD million revenue. The company has "
            "achieved 72% renewable electricity coverage and is on track for a 1.5°C-aligned Science "
            "Based Target pathway. TechCorp discloses under CDP Climate Change category C (Management). "
            "Key reduction initiatives include a renewable PPA signed in Q3 and a company-wide remote-first "
            "travel policy reducing Scope 3 business travel emissions by 38% year-on-year."
        ),
        "offset_recommendation": "Purchase 20 tCO2e in high-quality Gold Standard REDD+ forest conservation credits to bridge remaining gap to net-zero.",
    },
    {
        "name": "ManufactureCo",
        "sector": "Heavy Industry / Manufacturing",
        "scope1": 4820.0,
        "scope2": 1940.0,
        "scope3": 3210.0,
        "revenue": 320.0,
        "renewable_pct": 8,
        "top_opportunities": [
            "Electrify process heat using industrial heat pumps → est. −1,200 tCO2e/yr",
            "Switch grid electricity to renewable tariff → est. −1,750 tCO2e/yr",
            "Fuel switch from diesel to HVO (Hydrotreated Vegetable Oil) for on-site vehicles → est. −380 tCO2e/yr",
            "Waste heat recovery system on main furnace → est. −290 tCO2e/yr",
        ],
        "cdp_paragraph": (
            "ManufactureCo reports total Scope 1+2+3 emissions of 9,970 tCO2e, yielding a carbon intensity "
            "of 31.2 tCO2e per USD million revenue — significantly above the industrial sector median of "
            "18 tCO2e/USD M. Scope 1 emissions are dominated by natural gas combustion in process furnaces "
            "and diesel consumption in on-site logistics. The company currently discloses at CDP level D "
            "(Disclosure). Urgent decarbonisation action is required to align with Paris Agreement trajectories. "
            "ManufactureCo has committed to a net-zero target by 2045 with an interim 50% absolute reduction by 2030."
        ),
        "offset_recommendation": "Engage a Voluntary Carbon Market broker to purchase 1,000 tCO2e in verified industrial methane capture credits while internal reductions are implemented.",
    },
    {
        "name": "RetailChain",
        "sector": "Consumer Retail",
        "scope1": 145.0,
        "scope2": 620.0,
        "scope3": 2870.0,
        "revenue": 210.0,
        "renewable_pct": 31,
        "top_opportunities": [
            "Last-mile delivery electrification (EV fleet) → est. −680 tCO2e/yr",
            "Supplier engagement programme — Scope 3.1 purchased goods emissions → est. −800 tCO2e/yr",
            "LED lighting retrofit across all stores → est. −120 tCO2e/yr",
            "Packaging lightweighting and recycled content → est. −95 tCO2e/yr",
        ],
        "cdp_paragraph": (
            "RetailChain reports total Scope 1+2+3 emissions of 3,635 tCO2e, with Scope 3 representing "
            "79% of the total footprint — typical for the consumer retail sector where upstream supply chain "
            "and downstream logistics dominate. Carbon intensity stands at 17.3 tCO2e/USD M revenue. "
            "RetailChain discloses at CDP level B (Management). The company has launched a Supplier "
            "Sustainability Charter requiring all Tier-1 suppliers to set emissions reduction targets by 2025. "
            "A science-based net-zero target has been submitted to SBTi for validation."
        ),
        "offset_recommendation": "Invest in 500 tCO2e Blue Carbon (coastal wetland restoration) credits to offset residual Scope 3 logistics while supply chain initiatives mature.",
    },
    {
        "name": "StartupXYZ",
        "sector": "SMB / Early Stage",
        "scope1": 2.1,
        "scope2": 4.8,
        "scope3": 7.3,
        "revenue": 3.2,
        "renewable_pct": 55,
        "top_opportunities": [
            "Move office hosting to a 100% renewable-certified cloud provider → est. −2 tCO2e",
            "Adopt a remote-first hiring policy to eliminate commute Scope 3 → est. −1.5 tCO2e",
            "Switch to a green energy tariff for office electricity → est. −1.8 tCO2e",
        ],
        "cdp_paragraph": (
            "StartupXYZ reports a minimal total footprint of 14.2 tCO2e for the reporting year, "
            "representing a carbon intensity of 4.4 tCO2e/USD M revenue — well below sector benchmarks. "
            "The company currently operates as a carbon-light business given its predominantly remote "
            "workforce and SaaS delivery model. While SMBs are not required to disclose under CDP, "
            "StartupXYZ has proactively conducted this GHG inventory to establish a baseline ahead of "
            "anticipated customer and investor ESG due diligence requirements."
        ),
        "offset_recommendation": "Offset the full 14.2 tCO2e with a certified carbon-neutral label using community-based renewable energy credits in developing markets — cost-effective at this scale.",
    },
]


def intensity_style(intensity):
    if intensity < 5:
        return ("rgba(21,128,61,0.25)", "#86efac", "#16a34a", "LOW")
    elif intensity < 20:
        return ("rgba(161,98,7,0.25)", "#fde047", "#ca8a04", "MEDIUM")
    else:
        return ("rgba(185,28,28,0.25)", "#fca5a5", "#dc2626", "HIGH")


def build_esg_card(c: dict) -> str:
    total = c["scope1"] + c["scope2"] + c["scope3"]
    intensity = round(total / c["revenue"], 2) if c["revenue"] else 0
    bg, text_color, border_color, label = intensity_style(intensity)

    opps_html = "".join(
        f'<li style="color:#e2e8f0;margin-bottom:5px;">{o}</li>'
        for o in c["top_opportunities"]
    )

    scope1_pct = round(c["scope1"] / total * 100) if total else 0
    scope2_pct = round(c["scope2"] / total * 100) if total else 0
    scope3_pct = 100 - scope1_pct - scope2_pct

    return f"""
<div style="background:rgba(15,23,42,0.85);border:1px solid rgba(148,163,184,0.2);
            border-radius:16px;padding:24px;margin-bottom:20px;font-family:system-ui,sans-serif;">

  <!-- Header -->
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">
    <div>
      <div style="color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Company</div>
      <div style="color:#f1f5f9;font-size:20px;font-weight:700;">{c['name']}</div>
      <div style="color:#94a3b8;font-size:13px;">{c['sector']} · 🌱 Renewables: {c['renewable_pct']}%</div>
    </div>
    <div style="background:{bg};border:2px solid {border_color};border-radius:12px;padding:10px 20px;text-align:center;">
      <div style="color:{text_color};font-size:22px;font-weight:800;">{intensity} tCO₂e/M$</div>
      <div style="color:{text_color};font-size:11px;margin-top:2px;">CARBON INTENSITY · {label}</div>
    </div>
  </div>

  <!-- Scope breakdown -->
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px;">
    <div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:12px;text-align:center;">
      <div style="color:#94a3b8;font-size:11px;margin-bottom:4px;">Scope 1 (Direct)</div>
      <div style="color:#fca5a5;font-size:18px;font-weight:700;">{c['scope1']:,.1f}</div>
      <div style="color:#94a3b8;font-size:11px;">tCO₂e · {scope1_pct}%</div>
    </div>
    <div style="background:rgba(234,179,8,0.15);border:1px solid rgba(234,179,8,0.3);border-radius:10px;padding:12px;text-align:center;">
      <div style="color:#94a3b8;font-size:11px;margin-bottom:4px;">Scope 2 (Energy)</div>
      <div style="color:#fde047;font-size:18px;font-weight:700;">{c['scope2']:,.1f}</div>
      <div style="color:#94a3b8;font-size:11px;">tCO₂e · {scope2_pct}%</div>
    </div>
    <div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);border-radius:10px;padding:12px;text-align:center;">
      <div style="color:#94a3b8;font-size:11px;margin-bottom:4px;">Scope 3 (Value Chain)</div>
      <div style="color:#a5b4fc;font-size:18px;font-weight:700;">{c['scope3']:,.1f}</div>
      <div style="color:#94a3b8;font-size:11px;">tCO₂e · {scope3_pct}%</div>
    </div>
    <div style="background:{bg};border:2px solid {border_color};border-radius:10px;padding:12px;text-align:center;">
      <div style="color:#94a3b8;font-size:11px;margin-bottom:4px;">Total Footprint</div>
      <div style="color:{text_color};font-size:18px;font-weight:700;">{total:,.1f}</div>
      <div style="color:#94a3b8;font-size:11px;">tCO₂e</div>
    </div>
  </div>

  <!-- Reduction opportunities -->
  <div style="background:rgba(51,65,85,0.4);border-radius:10px;padding:14px;margin-bottom:14px;">
    <div style="color:#86efac;font-size:13px;font-weight:600;margin-bottom:8px;">🎯 Top Reduction Opportunities</div>
    <ul style="margin:0;padding-left:18px;">{opps_html}</ul>
  </div>

  <!-- CDP paragraph -->
  <div style="background:rgba(51,65,85,0.4);border-radius:10px;padding:14px;margin-bottom:14px;">
    <div style="color:#7dd3fc;font-size:13px;font-weight:600;margin-bottom:6px;">📋 CDP Disclosure Paragraph</div>
    <div style="color:#cbd5e1;font-size:13px;line-height:1.65;font-style:italic;">"{c['cdp_paragraph']}"</div>
  </div>

  <!-- Offset recommendation -->
  <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:14px;">
    <div style="color:#6ee7b7;font-size:13px;font-weight:600;margin-bottom:4px;">♻️ Carbon Offset Recommendation</div>
    <div style="color:#cbd5e1;font-size:13px;">{c['offset_recommendation']}</div>
  </div>
</div>
"""


def render_all_esg_demos():
    return "".join(build_esg_card(c) for c in DEMO_COMPANIES)


def run_esg_analysis(company_name, elec_kwh, nat_gas, diesel_l, air_km, hotel_nights, waste_t, revenue, renewable_pct, api_key):
    if not api_key or not api_key.strip():
        return '<div style="color:#f87171;padding:20px;background:rgba(220,38,38,0.15);border-radius:10px;">Please enter your OpenAI API key.</div>'
    if not company_name or not company_name.strip():
        return '<div style="color:#fde047;padding:20px;background:rgba(161,98,7,0.15);border-radius:10px;">Please enter a company name.</div>'

    scope1, scope2, scope3 = calc_emissions(elec_kwh, nat_gas, diesel_l, air_km, hotel_nights, waste_t)
    total = scope1 + scope2 + scope3
    intensity = round(total / revenue, 2) if revenue else 0

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key.strip())

        prompt = f"""You are an ESG and sustainability expert. Generate a full CDP-style carbon audit report.

Company: {company_name}
Scope 1 (Direct combustion): {scope1} tCO2e
Scope 2 (Purchased electricity): {scope2} tCO2e
Scope 3 (Travel + waste): {scope3} tCO2e
Total: {total} tCO2e
Carbon intensity: {intensity} tCO2e per USD million revenue
Renewable electricity: {renewable_pct}%
Revenue: USD {revenue} million

Input data breakdown:
- Electricity: {elec_kwh:,.0f} kWh
- Natural gas: {nat_gas:,.1f} MMBtu
- Diesel: {diesel_l:,.0f} litres
- Air travel: {air_km:,.0f} km
- Hotel nights: {hotel_nights:,.0f}
- Waste: {waste_t:,.1f} tonnes

Return a JSON object with these exact keys:
- sector_benchmark: string describing how intensity compares to sector average
- top_opportunities: list of 4 strings, each a specific reduction action with estimated tCO2e saving
- cdp_paragraph: string, 4-5 sentence CDP-style disclosure paragraph
- offset_recommendation: string, specific carbon credit recommendation
- net_zero_year: string, estimated year achievable for net-zero with recommended actions
- rating: one of "LOW", "MEDIUM", "HIGH" (carbon intensity rating)

Return ONLY valid JSON. No markdown fences."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=900,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)

        company = {
            "name": company_name,
            "sector": data.get("sector_benchmark", ""),
            "scope1": scope1,
            "scope2": scope2,
            "scope3": scope3,
            "revenue": revenue,
            "renewable_pct": renewable_pct,
            "top_opportunities": data.get("top_opportunities", []),
            "cdp_paragraph": data.get("cdp_paragraph", ""),
            "offset_recommendation": data.get("offset_recommendation", ""),
        }

        card = build_esg_card(company)
        extra = f"""
<div style="background:rgba(51,65,85,0.5);border-radius:12px;padding:16px;margin-top:12px;font-family:system-ui,sans-serif;">
  <div style="color:#6ee7b7;font-weight:600;margin-bottom:6px;">🎯 Estimated Net-Zero Year</div>
  <div style="color:#e2e8f0;font-size:18px;font-weight:700;">{data.get('net_zero_year', 'N/A')}</div>
  <div style="color:#94a3b8;font-size:12px;margin-top:4px;">Based on implementing all recommended reduction opportunities</div>
</div>"""
        return card + extra

    except json.JSONDecodeError as e:
        return f'<div style="color:#f87171;padding:20px;background:rgba(220,38,38,0.15);border-radius:10px;">JSON parse error: {str(e)}</div>'
    except Exception as e:
        return f'<div style="color:#f87171;padding:20px;background:rgba(220,38,38,0.15);border-radius:10px;">Error: {str(e)}</div>'


HOW_IT_WORKS_HTML = """
<div style="font-family:system-ui,sans-serif;color:#e2e8f0;padding:8px;">
  <h2 style="color:#f8fafc;font-size:22px;margin-bottom:6px;">How the ESG Carbon Audit Agent Works</h2>
  <p style="color:#94a3b8;margin-bottom:24px;">GHG Protocol methodology + n8n automation + GPT-4 CDP-style report generation.</p>

  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-bottom:24px;">
    <div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);border-radius:12px;padding:16px;">
      <div style="font-size:28px;margin-bottom:8px;">1️⃣</div>
      <div style="color:#6ee7b7;font-weight:600;margin-bottom:6px;">Activity Data Input</div>
      <div style="color:#cbd5e1;font-size:13px;">Energy consumption (kWh, MMBtu, litres), business travel (km + hotel nights), and waste (tonnes) are entered per GHG Protocol boundary definitions.</div>
    </div>
    <div style="background:rgba(234,179,8,0.15);border:1px solid rgba(234,179,8,0.35);border-radius:12px;padding:16px;">
      <div style="font-size:28px;margin-bottom:8px;">2️⃣</div>
      <div style="color:#fde047;font-weight:600;margin-bottom:6px;">Scope 1/2/3 Calculation</div>
      <div style="color:#cbd5e1;font-size:13px;">Emissions are computed using DEFRA/EPA emission factors: electricity (0.000233 tCO₂e/kWh), natural gas (0.0533/MMBtu), diesel (0.00268/L), air travel (0.000255/km).</div>
    </div>
    <div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.35);border-radius:12px;padding:16px;">
      <div style="font-size:28px;margin-bottom:8px;">3️⃣</div>
      <div style="color:#a5b4fc;font-weight:600;margin-bottom:6px;">GPT-4 Report Generation</div>
      <div style="color:#cbd5e1;font-size:13px;">Calculated emissions are passed to GPT-4 which generates a CDP-style disclosure paragraph, benchmarks intensity against sector averages, and identifies reduction opportunities.</div>
    </div>
    <div style="background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.35);border-radius:12px;padding:16px;">
      <div style="font-size:28px;margin-bottom:8px;">4️⃣</div>
      <div style="color:#93c5fd;font-weight:600;margin-bottom:6px;">Offset & Net-Zero Planning</div>
      <div style="color:#cbd5e1;font-size:13px;">The agent recommends high-quality voluntary carbon credits and projects a net-zero achievement year based on the recommended reduction pathway.</div>
    </div>
  </div>

  <div style="background:rgba(51,65,85,0.5);border-radius:12px;padding:16px;margin-bottom:16px;">
    <div style="color:#86efac;font-weight:600;margin-bottom:8px;">📐 GHG Protocol Scope Definitions</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;">
      <div style="color:#cbd5e1;font-size:13px;"><strong style="color:#fca5a5;">Scope 1:</strong> Direct emissions from owned/controlled sources (boilers, fleet, on-site generation)</div>
      <div style="color:#cbd5e1;font-size:13px;"><strong style="color:#fde047;">Scope 2:</strong> Indirect emissions from purchased electricity, steam, heating, cooling</div>
      <div style="color:#cbd5e1;font-size:13px;"><strong style="color:#a5b4fc;">Scope 3:</strong> All other indirect emissions in the value chain (travel, waste, supply chain)</div>
    </div>
  </div>

  <div style="background:rgba(51,65,85,0.5);border-radius:12px;padding:16px;">
    <div style="color:#7dd3fc;font-weight:600;margin-bottom:8px;">🔗 n8n Automation Workflow</div>
    <div style="color:#94a3b8;font-size:13px;">
      View the underlying n8n workflow:
      <a href="https://aravind5.app.n8n.cloud/workflow/PLACEHOLDER_ESG" target="_blank"
         style="color:#7dd3fc;">https://aravind5.app.n8n.cloud/workflow/PLACEHOLDER_ESG</a>
    </div>
  </div>
</div>
"""

# ── Gradio App ────────────────────────────────────────────────────────────────

with gr.Blocks(theme=gr.themes.Soft(), title="ESG Carbon Footprint Audit Agent") as demo:
    gr.HTML("""
    <div style="text-align:center;padding:24px 16px 8px;font-family:system-ui,sans-serif;">
      <div style="font-size:48px;margin-bottom:8px;">🌿</div>
      <h1 style="color:#f1f5f9;font-size:28px;font-weight:800;margin:0 0 6px;">ESG Carbon Footprint Audit Agent</h1>
      <p style="color:#94a3b8;font-size:15px;max-width:620px;margin:0 auto;">
        GHG Protocol-aligned Scope 1/2/3 emissions calculator with AI-generated CDP-style disclosure
        reports and science-based reduction roadmaps.
      </p>
    </div>
    """)

    with gr.Tabs():

        # ── Tab 1: Live Demo ──────────────────────────────────────────────────
        with gr.Tab("🌍 Live Demo"):
            gr.HTML("""
            <div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);
                        border-radius:10px;padding:12px 16px;margin-bottom:16px;font-family:system-ui,sans-serif;">
              <span style="color:#6ee7b7;font-weight:600;">4 pre-computed company profiles</span>
              <span style="color:#cbd5e1;"> — no API key required. Covers LOW / MEDIUM / HIGH carbon intensity.</span>
            </div>
            """)
            demo_output = gr.HTML(value=render_all_esg_demos())

        # ── Tab 2: Live Analysis ──────────────────────────────────────────────
        with gr.Tab("⚡ Live Analysis"):
            gr.HTML("""
            <div style="background:rgba(161,98,7,0.15);border:1px solid rgba(161,98,7,0.35);
                        border-radius:10px;padding:12px 16px;margin-bottom:16px;font-family:system-ui,sans-serif;">
              <span style="color:#fde047;font-weight:600;">Live GPT-4 ESG audit</span>
              <span style="color:#cbd5e1;"> — enter your company's activity data and OpenAI API key.</span>
            </div>
            """)
            with gr.Row():
                with gr.Column(scale=1):
                    company_name = gr.Textbox(label="Company Name", placeholder="e.g. Acme Corp")
                    revenue = gr.Number(label="Annual Revenue (USD millions)", value=50.0, minimum=0.1)
                    renewable_pct = gr.Slider(minimum=0, maximum=100, value=20, step=1, label="Renewable Electricity (%)")

                    gr.HTML('<div style="color:#7dd3fc;font-size:13px;font-weight:600;margin:12px 0 4px;">Scope 1 — Direct Combustion</div>')
                    nat_gas = gr.Number(label="Natural Gas (MMBtu)", value=0.0, minimum=0)
                    diesel_l = gr.Number(label="Diesel (litres)", value=0.0, minimum=0)

                    gr.HTML('<div style="color:#fde047;font-size:13px;font-weight:600;margin:12px 0 4px;">Scope 2 — Purchased Electricity</div>')
                    elec_kwh = gr.Number(label="Electricity (kWh)", value=0.0, minimum=0)

                    gr.HTML('<div style="color:#a5b4fc;font-size:13px;font-weight:600;margin:12px 0 4px;">Scope 3 — Travel & Waste</div>')
                    air_km = gr.Number(label="Air Travel (km)", value=0.0, minimum=0)
                    hotel_nights = gr.Number(label="Hotel Nights", value=0.0, minimum=0)
                    waste_t = gr.Number(label="Waste (tonnes)", value=0.0, minimum=0)

                    api_key = gr.Textbox(type="password", label="OpenAI API Key", placeholder="sk-...")
                    submit_btn = gr.Button("📊 Generate ESG Audit", variant="primary")

                with gr.Column(scale=2):
                    live_output = gr.HTML(value='<div style="color:#94a3b8;padding:40px;text-align:center;font-family:system-ui,sans-serif;">ESG audit results will appear here.</div>')

            submit_btn.click(
                fn=run_esg_analysis,
                inputs=[company_name, elec_kwh, nat_gas, diesel_l, air_km, hotel_nights, waste_t, revenue, renewable_pct, api_key],
                outputs=live_output,
            )

        # ── Tab 3: How It Works ───────────────────────────────────────────────
        with gr.Tab("ℹ️ How It Works"):
            gr.HTML(HOW_IT_WORKS_HTML)

if __name__ == "__main__":
    demo.launch()
