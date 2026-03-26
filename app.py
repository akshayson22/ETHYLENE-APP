from datetime import datetime
from pathlib import Path
import os
import tempfile

from flask import Flask, render_template, request
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from calculations import run_simulation

app = Flask(
    __name__,
    static_url_path="/ethyleneprediction/static"
)

EMAIL_LOG_FILENAME = "email_submission_log.txt"
EMAIL_LOG_HEADER = "# Timestamp (ISO 8601 with timezone)\tEmail\n"

def plot_to_base64(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def iter_email_log_paths():
    seen = set()
    configured_path = os.environ.get("EMAIL_LOG_PATH", "").strip()
    candidates = []

    if configured_path:
        candidates.append(Path(configured_path).expanduser())

    candidates.extend([
        Path(__file__).resolve().parent / EMAIL_LOG_FILENAME,
        Path(app.instance_path) / EMAIL_LOG_FILENAME,
        Path.cwd() / EMAIL_LOG_FILENAME,
        Path(tempfile.gettempdir()) / EMAIL_LOG_FILENAME,
    ])

    for candidate in candidates:
        resolved = str(candidate)
        if resolved in seen:
            continue
        seen.add(resolved)
        yield candidate

def append_email_submission(email):
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = f"{timestamp}\t{email}\n"
    last_error = None

    # Try the project log first, then fall back to writable runtime locations.
    for log_path in iter_email_log_paths():
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_exists = log_path.exists()
            with log_path.open("a", encoding="utf-8") as log_file:
                if not file_exists:
                    log_file.write(EMAIL_LOG_HEADER)
                log_file.write(entry)
            app.logger.info("Logged email submission to %s", log_path)
            return
        except OSError as exc:
            last_error = exc

    app.logger.warning("Failed to log email submission for %s: %s", email, last_error)

@app.route("/", methods=["GET", "POST"])
def index():
    # Default (empty) inputs
    fields = {
        "Wp": "",  # kg
        "StorageTemperature": "",
        "Perforationdiamicron": "",
        "NumberofPerfo": "",
        "mryan": "",
        "Vl": "",
        "Test_days": ""
    }

    errors = []
    plot1_b64 = None
    plot2_b64 = None
    extra_info = {}

    if request.method == "POST":
        # Reset action
        if "reset" in request.form:
            return render_template("index.html", fields=fields, errors=[], plot1_b64=None, plot2_b64=None, extra_info=extra_info)

        # Collect values
        try:
            collector_email = request.form.get("collector_email", "").strip()
            if not collector_email:
                raise ValueError("Email address is required before updating plots.")

            append_email_submission(collector_email)

            fields["Wp"] = request.form.get("Wp", "").strip()
            fields["StorageTemperature"] = request.form.get("StorageTemperature", "").strip()
            fields["Perforationdiamicron"] = request.form.get("Perforationdiamicron", "").strip()
            fields["NumberofPerfo"] = request.form.get("NumberofPerfo", "").strip()
            fields["mryan"] = request.form.get("mryan", "").strip()
            fields["Vl"] = request.form.get("Vl", "").strip()
            fields["Test_days"] = request.form.get("Test_days", "").strip()

            # Convert to floats (validation will happen in run_simulation too)
            params = {
                "Wp": float(fields["Wp"]),
                "StorageTemperature": float(fields["StorageTemperature"]),
                "Perforationdiamicron": float(fields["Perforationdiamicron"]),
                "NumberofPerfo": float(fields["NumberofPerfo"]),
                "mryan": float(fields["mryan"]),
                "Vl": float(fields["Vl"]),
                "Test_days": float(fields["Test_days"]),
            }

            result = run_simulation(params)
            errors = result.get("errors", [])

            if not errors:
                # Plot 1: O2 + CO2
                fig1 = plt.figure(figsize=(6, 4))
                ax1 = fig1.add_subplot(111)
                ax1.plot(result["TimesInDays"], result["Oxy_pct"], label="Predicted O₂")
                ax1.plot(result["TimesInDays"], result["CO2_pct"], label="Predicted CO₂")
                ax1.set_ylim(0, 24)
                ax1.set_xlim(0, result["xlim_days"])
                ax1.set_xlabel("Time, days")
                ax1.set_ylabel("O₂ and CO₂, %")
                ax1.legend(loc="upper right")
                ax1.set_facecolor("#DFF6FF")
                fig1.tight_layout()
                plot1_b64 = plot_to_base64(fig1)

                # Plot 2: Ethylene
                fig2 = plt.figure(figsize=(6, 4))
                ax3 = fig2.add_subplot(111)
                ax3.plot(result["TimesInDays"], result["FinalEthy_ppm"], label="Predicted C₂H₄")
                ax3.set_ylim(0, 5)
                ax3.set_xlim(0, result["xlim_days"])
                ax3.set_xlabel("Time, days")
                ax3.set_ylabel("C₂H₄, ppm")
                ax3.legend(loc="upper right")
                ax3.set_facecolor("#DFF6FF")
                fig2.tight_layout()
                plot2_b64 = plot_to_base64(fig2)                

        except ValueError as ve:
            errors = [str(ve)]
        except Exception as e:
            errors = [f"Unexpected error: {str(e)}"]

    return render_template(
        "index.html",
        fields=fields,
        errors=errors,
        plot1_b64=plot1_b64,
        plot2_b64=plot2_b64,
        extra_info=extra_info
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

