"""
KernHell v2.0 - Enhanced Report Generator.
Produces a premium dark-mode HTML dashboard with Chart.js visualizations.
"""
import time
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter

from kernhell.utils import log_info, log_success, log_error


def _format_timestamp(ts: float) -> str:
    """Convert Unix timestamp to human-readable string."""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return "Unknown"


def _compute_metrics(stats: Dict, runs: List[Dict]) -> Dict[str, Any]:
    """Compute advanced metrics from raw data."""
    total_runs = stats.get("total_runs", 0)
    total_healed = stats.get("total_healed", 0)
    saved_hours = stats.get("saved_hours", 0.0)

    success_rate = round((total_healed / total_runs * 100), 1) if total_runs > 0 else 0
    money_saved = round(saved_hours * 50, 2)  # $50/hr avg dev rate

    # Provider breakdown
    provider_counts = Counter(r.get("model", "unknown") for r in runs)

    # Daily activity (last 7 days)
    now = time.time()
    daily = {}
    for r in runs:
        ts = r.get("timestamp", 0)
        if now - ts < 7 * 86400:
            day = datetime.fromtimestamp(ts).strftime("%a")
            daily[day] = daily.get(day, 0) + 1

    # Heal vs fail counts for chart
    healed_count = sum(1 for r in runs if r.get("healed"))
    failed_count = len(runs) - healed_count

    return {
        "total_runs": total_runs,
        "total_healed": total_healed,
        "success_rate": success_rate,
        "saved_hours": round(saved_hours, 1),
        "money_saved": money_saved,
        "provider_counts": dict(provider_counts),
        "daily_activity": daily,
        "healed_count": healed_count,
        "failed_count": failed_count,
    }


def _build_runs_table(runs: List[Dict]) -> str:
    """Build HTML table rows for recent runs."""
    if not runs:
        return '<tr><td colspan="5" style="text-align:center;color:#666;">No runs recorded yet</td></tr>'

    rows = []
    for r in reversed(runs[-25:]):  # Last 25, newest first
        ts = _format_timestamp(r.get("timestamp", 0))
        fname = Path(r.get("file", "unknown")).name
        status = "Healed ✅" if r.get("healed") else "Failed ❌"
        status_class = "healed" if r.get("healed") else "failed"
        model = r.get("model", "—")
        error_preview = (r.get("error") or "—")[:60]

        rows.append(
            f'<tr>'
            f'<td>{ts}</td>'
            f'<td class="file-cell">{fname}</td>'
            f'<td class="{status_class}">{status}</td>'
            f'<td>{model}</td>'
            f'<td class="error-cell" title="{r.get("error", "")}">{error_preview}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def generate_report(stats: Dict, runs: List[Dict], output_path: Path = None) -> Path:
    """
    Generate a premium HTML dashboard report.

    Args:
        stats: Dictionary with total_runs, total_healed, saved_hours
        runs: List of run records with timestamp, file, healed, model, error
        output_path: Optional custom output path

    Returns:
        Path to the generated HTML file
    """
    if output_path is None:
        output_path = Path("kernhell_report.html")

    metrics = _compute_metrics(stats, runs)
    runs_table = _build_runs_table(runs)

    # Chart data
    provider_labels = list(metrics["provider_counts"].keys()) or ["none"]
    provider_values = list(metrics["provider_counts"].values()) or [0]
    daily_labels = list(metrics["daily_activity"].keys()) or ["—"]
    daily_values = list(metrics["daily_activity"].values()) or [0]

    generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KernHell Mission Control</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #0a0a0f;
            color: #e0e0e5;
            min-height: 100vh;
        }}

        .header {{
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
            border-bottom: 1px solid rgba(0, 255, 100, 0.15);
            padding: 24px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00ff64, #00cc52, #22dd88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }}

        .header .version {{
            background: rgba(0, 255, 100, 0.1);
            border: 1px solid rgba(0, 255, 100, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            color: #00ff64;
            font-weight: 500;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px 24px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}

        .stat-card {{
            background: linear-gradient(145deg, #12121f, #1a1a2e);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(0, 255, 100, 0.2);
        }}

        .stat-card .label {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: #fff;
        }}

        .stat-card .value.green {{ color: #00ff64; }}
        .stat-card .value.blue {{ color: #4d9fff; }}
        .stat-card .value.gold {{ color: #ffd700; }}
        .stat-card .value.purple {{ color: #b366ff; }}

        .charts-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 32px;
        }}

        .chart-card {{
            background: linear-gradient(145deg, #12121f, #1a1a2e);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 24px;
        }}

        .chart-card h3 {{
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 16px;
            font-weight: 500;
        }}

        .chart-container {{
            position: relative;
            height: 220px;
        }}

        .table-card {{
            background: linear-gradient(145deg, #12121f, #1a1a2e);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 24px;
            overflow: hidden;
        }}

        .table-card h3 {{
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 16px;
            font-weight: 500;
        }}

        .table-wrapper {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            text-align: left;
            padding: 10px 14px;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #666;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}

        td {{
            padding: 10px 14px;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            color: #ccc;
        }}

        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

        .healed {{ color: #00ff64; font-weight: 600; }}
        .failed {{ color: #ff4444; font-weight: 600; }}
        .file-cell {{ color: #4d9fff; font-family: 'Courier New', monospace; font-size: 0.8rem; }}
        .error-cell {{ color: #888; font-size: 0.75rem; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

        .footer {{
            text-align: center;
            padding: 32px;
            color: #444;
            font-size: 0.75rem;
        }}

        .footer a {{ color: #00ff64; text-decoration: none; }}

        @media (max-width: 768px) {{
            .charts-row {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .header {{ padding: 16px 20px; }}
            .container {{ padding: 16px; }}
        }}
    </style>
</head>
<body>

<div class="header">
    <h1>⚡ KernHell Mission Control</h1>
    <span class="version">v2.0</span>
</div>

<div class="container">

    <!-- Stats Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">Total Runs</div>
            <div class="value blue">{metrics['total_runs']}</div>
        </div>
        <div class="stat-card">
            <div class="label">Fractures Healed</div>
            <div class="value green">{metrics['total_healed']}</div>
        </div>
        <div class="stat-card">
            <div class="label">Success Rate</div>
            <div class="value gold">{metrics['success_rate']}%</div>
        </div>
        <div class="stat-card">
            <div class="label">Hours Saved</div>
            <div class="value purple">{metrics['saved_hours']}h</div>
        </div>
        <div class="stat-card">
            <div class="label">Money Saved</div>
            <div class="value green">${metrics['money_saved']}</div>
        </div>
    </div>

    <!-- Charts -->
    <div class="charts-row">
        <div class="chart-card">
            <h3>Heal Success Rate</h3>
            <div class="chart-container">
                <canvas id="successChart"></canvas>
            </div>
        </div>
        <div class="chart-card">
            <h3>Provider Usage</h3>
            <div class="chart-container">
                <canvas id="providerChart"></canvas>
            </div>
        </div>
    </div>

    <div class="charts-row">
        <div class="chart-card">
            <h3>7-Day Activity</h3>
            <div class="chart-container">
                <canvas id="activityChart"></canvas>
            </div>
        </div>
        <div class="chart-card" style="display:flex;flex-direction:column;justify-content:center;align-items:center;">
            <div style="font-size:3.5rem;margin-bottom:12px;">🔥</div>
            <div style="font-size:1.8rem;font-weight:700;color:#00ff64;">{metrics['total_healed']}</div>
            <div style="color:#888;font-size:0.85rem;margin-top:4px;">Tests Resurrected</div>
            <div style="color:#444;font-size:0.7rem;margin-top:8px;">That's {metrics['saved_hours']}h you didn't spend debugging</div>
        </div>
    </div>

    <!-- Recent Runs Table -->
    <div class="table-card">
        <h3>Recent Healing Operations (Last 25)</h3>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>File</th>
                        <th>Status</th>
                        <th>Model</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
                    {runs_table}
                </tbody>
            </table>
        </div>
    </div>

</div>

<div class="footer">
    Generated by <a href="#">KernHell v2.0</a> &middot; {generated_at}
</div>

<script>
    Chart.defaults.color = '#888';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';

    // Success Rate Doughnut
    new Chart(document.getElementById('successChart'), {{
        type: 'doughnut',
        data: {{
            labels: ['Healed', 'Failed'],
            datasets: [{{
                data: [{metrics['healed_count']}, {metrics['failed_count']}],
                backgroundColor: ['#00ff64', '#ff4444'],
                borderWidth: 0,
                spacing: 2,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ padding: 16, usePointStyle: true, pointStyle: 'circle' }} }}
            }}
        }}
    }});

    // Provider Usage Bar
    new Chart(document.getElementById('providerChart'), {{
        type: 'bar',
        data: {{
            labels: {provider_labels},
            datasets: [{{
                label: 'API Calls',
                data: {provider_values},
                backgroundColor: ['#4d9fff', '#b366ff', '#ffd700', '#00ff64', '#ff6b6b'],
                borderRadius: 6,
                borderSkipped: false,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }},
                x: {{ grid: {{ display: false }} }}
            }}
        }}
    }});

    // 7-Day Activity
    new Chart(document.getElementById('activityChart'), {{
        type: 'line',
        data: {{
            labels: {daily_labels},
            datasets: [{{
                label: 'Runs',
                data: {daily_values},
                borderColor: '#00ff64',
                backgroundColor: 'rgba(0, 255, 100, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#00ff64',
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }},
                x: {{ grid: {{ display: false }} }}
            }}
        }}
    }});
</script>

</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    log_success(f"Report generated: {output_path.absolute()}")

    return output_path


def open_report(report_path: Path):
    """Open the HTML report in the default browser."""
    try:
        webbrowser.open(report_path.absolute().as_uri())
    except Exception as e:
        log_error(f"Could not open browser: {e}")
        log_info(f"Open manually: {report_path.absolute()}")
