# Process Scheduling Simulator (Python / PyQt5 + Matplotlib)

An interactive desktop application that lets you **model, run, and visualise classic CPU‑scheduling algorithms**.  Add processes with arrival & burst times (plus priority where required), pick an algorithm, and instantly see the resulting Gantt chart along with per‑process turnaround / waiting / completion times and averages.

---

## Algorithms Supported

| Abbreviation | Full Name | Pre‑emptive? |
|--------------|-----------|--------------|
| **FCFS** | First‑Come, First‑Served | No |
| **Priority** | Priority Scheduling | No |
| **Priority (P)** | Priority *Pre‑emptive* | Yes |
| **SJF** | Shortest Job First | No |
| **SRTF** | Shortest Remaining Time First | Yes |
| **LJF** | Longest Job First | No |
| **LRTF** | Longest Remaining Time First | Yes |
| **HRRN** | Highest Response Ratio Next | No |

---

## Project Layout

| File | Purpose |
|------|---------|
| `main.py` | Launch script — creates the `QApplication` and shows the main window. |
| `GUI.py` | **PyQt5 GUI**: tables for process input, algorithm picker, Matplotlib canvas for Gantt chart, results table and validation. |
| `Logic.py` | Core scheduling engine — a base `Scheduler` class plus concrete subclasses for each algorithm; includes Gantt‑chart data generation and Matplotlib figure helpers. |

---

## Preview

(Add a screenshot of the main window with a colourful Gantt chart here!)

---

## Installation

### Prerequisites

* **Python 3.8+** (3.11 tested)
* pip / venv recommended

### Steps

```bash
# 1. Clone or download
cd process‑scheduling‑sim

# 2. (Optional) create & activate venv
python -m venv venv
source venv/bin/activate   # Windows: venv\\Scripts\\activate

# 3. Install dependencies
pip install PyQt5 matplotlib numpy

# 4. Run the app
python main.py
```

> **Linux:** If you encounter `xcb` Qt plugin errors, install system packages like `sudo apt install libxcb-xinerama0`.

---

## Using the Simulator

1. **Select Algorithm** from the drop‑down.  Column headers will adjust automatically (Priority column appears when needed).
2. **Add Process** rows; fill *Arrival* and *Burst* (and *Priority* for priority‑based algorithms).
3. Click **Run** to execute the schedule.
4. View the **Gantt chart** on the right and numerical results in the bottom table. Averages are displayed in the last row.
5. **Delete** or **Clear** rows to start over.

Validation prevents negative values and empty fields; descriptive error pop‑ups guide fixes.

---

## Packaging into an EXE (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "*.png;." main.py
# resulting dist/main.exe can be shared with end‑users
```

---

## Extending the Project

* 🎨 **Theme / Dark‑mode** — tweak PyQt5 stylesheets.
* 🖼️ **Export** charts as PNG/PDF.
* 📈 **Metrics** — throughput, CPU utilisation, context‑switch count.
* 🗄️ **Persistence** — save / load process sets to JSON.
* ⚙️ **New algorithms** — e.g., Round‑Robin, Multilevel Feedback Queue.

---

