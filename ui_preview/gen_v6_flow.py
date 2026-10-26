"""Generate SmartFind AI V6 technical pipeline flowchart image."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W, HEIGHT = 1000, 2350
fig, ax = plt.subplots(figsize=(10, 23.5), dpi=110)
ax.set_xlim(0, W)
ax.set_ylim(0, HEIGHT)
ax.axis("off")
fig.patch.set_facecolor("#0a1428")
ax.set_facecolor("#0a1428")

# color groups
C_INPUT = ("#f39c12", "#3a2a08")   # target onboarding
C_CAM   = ("#2f80ed", "#0d2247")   # camera / server
C_AI    = ("#2ecc71", "#0d3320")   # detection / AI
C_FEAT  = ("#9b59b6", "#2a1440")   # features
C_MATCH = ("#1abc9c", "#0a332c")   # match engine
C_STORE = ("#e74c3c", "#3a1210")   # storage
C_OUT   = ("#38bdf8", "#0b2a45")   # output

def box(x, y, w, h, text, fc, tc="white", fs=15, sub=None):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                       boxstyle="round,pad=6,rounding_size=14",
                       linewidth=2, edgecolor=fc, facecolor=fc, alpha=0.95)
    ax.add_patch(p)
    if sub:
        ax.text(x, y + 7, text, ha="center", va="center", fontsize=fs,
                color=tc, fontweight="bold")
        ax.text(x, y - 17, sub, ha="center", va="center", fontsize=fs - 4,
                color=tc, alpha=0.85)
    else:
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                color=tc, fontweight="bold")

def arrow(x1, y1, x2, y2, color="#8a9bb5"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                        mutation_scale=26, linewidth=2.6, color=color,
                        shrinkA=2, shrinkB=2)
    ax.add_patch(a)

# Title
ax.text(W / 2, HEIGHT - 45, "SmartFind AI V6 — Technical Pipeline",
        ha="center", va="center", fontsize=24, color="white", fontweight="bold")
ax.text(W / 2, HEIGHT - 85, "Target Onboarding  •  Multi-Camera Ingestion  •  AI Match  •  Intelligence",
        ha="center", va="center", fontsize=13, color="#8a9bb5")

CX = W / 2
y = HEIGHT - 160
STEP = 118
BW, BH = 430, 66

# 1 target onboarding chain
box(CX, y, BW, BH, "Target Person Image", *C_INPUT, sub="User Upload")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Target Profile Creation", *C_INPUT, sub="Person Record")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Face Quality Check", *C_INPUT, sub="Blur / Pose / Brightness Gate")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "ArcFace Embedding", *C_INPUT, sub="512-dim Vector")
ref_y = y

# Multi camera group box
y -= STEP + 30; arrow(CX, y + STEP + 30 - BH/2 - 8, CX, y + 60 + 14)
gy = y + 10
grp = FancyBboxPatch((CX - 330, gy - 62), 660, 124,
                     boxstyle="round,pad=6,rounding_size=16",
                     linewidth=2.5, edgecolor="#2f80ed", facecolor="#0d2247")
ax.add_patch(grp)
ax.text(CX, gy + 34, "Multiple Camera Sources", ha="center", fontsize=16,
        color="white", fontweight="bold")
ax.text(CX, gy - 6, "CAM 1   /   CAM 2   /   CAM 3 ...", ha="center",
        fontsize=15, color="#7fb3ff", fontweight="bold")
ax.text(CX, gy - 40, "N no. of IP / Edge Cameras", ha="center", fontsize=11,
        color="#8a9bb5")

y = gy - 95
arrow(CX, gy - 68, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "API / RTSP / IoT", *C_CAM, sub="Stream Ingestion Layer")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Central AI Server", *C_CAM, sub="GPU Inference Hub")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "YOLOv11", *C_AI, sub="Person Detection (conf 0.4)")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "ByteTrack", *C_AI, sub="Per-Camera Track ID")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Face + Body Features", *C_FEAT, sub="Crop + CLAHE + Sharpen")

# branch: ArcFace / OSNet
branch_y = y - STEP + 30
arrow(CX, y - BH/2 - 8, CX, branch_y + 46)
ax.plot([CX, CX - 230], [branch_y + 46, branch_y + 46], color="#9b59b6", lw=2.6)
ax.plot([CX, CX + 230], [branch_y + 46, branch_y + 46], color="#9b59b6", lw=2.6)
arrow(CX - 230, branch_y + 46, CX - 230, branch_y + BH/2 + 10)
arrow(CX + 230, branch_y + 46, CX + 230, branch_y + BH/2 + 10)
box(CX - 230, branch_y, 300, BH, "ArcFace", *C_FEAT, sub="Face Identity")
box(CX + 230, branch_y, 300, BH, "OSNet", *C_FEAT, sub="Body ReID")

# merge to Match Engine
y = branch_y - STEP
arrow(CX - 230, branch_y - BH/2 - 8, CX - 100, y + BH/2 + 12, "#9b59b6")
arrow(CX + 230, branch_y - BH/2 - 8, CX + 100, y + BH/2 + 12, "#9b59b6")
box(CX, y, BW, BH, "Match Engine", *C_MATCH, sub="Score Fusion + 5-Frame Smoothing")

y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "FAISS", *C_MATCH, sub="Vector ANN Search (Top-K)")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Candidate Matches", *C_MATCH, sub="Threshold >= 15%")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Cross-Camera Fusion", *C_AI, sub="Multi-Cam Identity Link")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "Event Correlation", *C_AI, sub="Timeline / Path Reconstruction")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "PostgreSQL + Evidence", *C_STORE, sub="Persons / Events / Match Crops")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW, BH, "GenAI", *C_OUT, sub="Incident Summary + Smart Q&A")
y -= STEP; arrow(CX, y + STEP - BH/2 - 8, CX, y + BH/2 + 10)
box(CX, y, BW + 40, BH + 6, "Web Dashboard", *C_OUT, sub="Live Grid • Search • Reports • Alerts", fs=17)

# Reference line: target embedding feeds match engine
ax.annotate("", xy=(CX + BW/2 + 6, y + 10), xytext=(CX + 250, ref_y - 4),
            arrowprops=dict(arrowstyle="-|>", color="#f39c12", lw=2,
                            connectionstyle="arc3,rad=-0.25", linestyle=(0, (6, 4))))
ax.text(W - 40, (y + ref_y) / 2, "reference\nembedding", ha="center",
        va="center", fontsize=11, color="#f39c12", rotation=90)

fig.subplots_adjust(left=0.01, right=0.99, top=0.995, bottom=0.005)
out = "ui_preview/v6_flowchart.png"
fig.savefig(out, facecolor=fig.get_facecolor(), dpi=110)
print("saved", out)
