from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]
FEATURE_FILE = PROJECT_ROOT / "analysis_outputs" / "ch6_window_features_2s.csv"
OUTPUT_DIR = PROJECT_ROOT / "analysis_outputs"
FIG_DIR = PROJECT_ROOT / "figs"
FIRMWARE_HEADER = WORKSPACE_ROOT / "可部署震动" / "src" / "knn_model.h"

TRAIN_PARTICIPANTS = ["person_1", "person_2", "person_3", "person_4"]
TEST_PARTICIPANT = "person_5"
LABELS = ["static_sitting", "pelvic_rotation"]
CLASS_TO_INT = {"static_sitting": 0, "pelvic_rotation": 1}
INT_TO_CLASS = {0: "static_sitting", 1: "pelvic_rotation"}

COMPACT_FEATURES = [
    "gyro_x_rms",
    "gyro_x_std",
    "gyro_x_range",
    "gyro_mag_std",
    "gyro_mag_max",
    "gyro_mag_rms",
    "gyro_mag_range",
    "gyro_mag_mean",
    "accel_z_max",
    "accel_z_range",
    "accel_z_std",
    "acc_motion_mag_std",
]

FULL_K = 7
COMPACT_K = 7
PROTOTYPES_PER_CLASS = 64
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10

METADATA_COLUMNS = {
    "person",
    "source_file",
    "window_index",
    "window_start_epoch_ms",
    "window_end_epoch_ms",
    "sample_count",
    "label",
}


def load_feature_table() -> pd.DataFrame:
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {FEATURE_FILE}. Run ch6_train_pelvic_rotation_classifier.py first."
        )
    return pd.read_csv(FEATURE_FILE)


def split_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_df = df[df["person"].isin(TRAIN_PARTICIPANTS)].copy()
    test_df = df[df["person"].eq(TEST_PARTICIPANT)].copy()
    if train_df.empty or test_df.empty:
        raise ValueError("The expected train/test participants were not found in the feature table.")
    return train_df, test_df


def metric_row(model: str, y_true: pd.Series, y_pred: np.ndarray, reference_points: int) -> dict[str, float | int | str]:
    return {
        "model": model,
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision": precision_score(
            y_true,
            y_pred,
            labels=LABELS,
            pos_label="pelvic_rotation",
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            labels=LABELS,
            pos_label="pelvic_rotation",
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            y_pred,
            labels=LABELS,
            pos_label="pelvic_rotation",
            zero_division=0,
        ),
        "reference_points": reference_points,
    }


def train_full_knn(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[np.ndarray, int]:
    feature_cols = [col for col in train_df.columns if col not in METADATA_COLUMNS]
    model = make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=FULL_K, weights="distance"),
    )
    model.fit(train_df[feature_cols], train_df["label"])
    return model.predict(test_df[feature_cols]), len(train_df)


def train_compact_knn(train_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train_features = train_df[COMPACT_FEATURES].astype(float)
    mean = train_features.mean(axis=0).to_numpy(copy=True)
    scale = train_features.std(axis=0, ddof=0).to_numpy(copy=True)
    scale[scale == 0.0] = 1.0

    reference_blocks = []
    reference_labels = []
    for class_name in LABELS:
        class_features = train_df.loc[train_df["label"].eq(class_name), COMPACT_FEATURES].astype(float)
        standardized = (class_features.to_numpy() - mean) / scale
        kmeans = KMeans(
            n_clusters=PROTOTYPES_PER_CLASS,
            random_state=KMEANS_RANDOM_STATE,
            n_init=KMEANS_N_INIT,
        )
        kmeans.fit(standardized)
        reference_blocks.append(kmeans.cluster_centers_)
        reference_labels.extend([CLASS_TO_INT[class_name]] * PROTOTYPES_PER_CLASS)

    references = np.vstack(reference_blocks)
    labels = np.array(reference_labels, dtype=np.uint8)
    return mean, scale, references, labels


def predict_compact(
    test_df: pd.DataFrame,
    mean: np.ndarray,
    scale: np.ndarray,
    references: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    standardized = (test_df[COMPACT_FEATURES].astype(float).to_numpy() - mean) / scale
    squared_distances = np.sum((standardized[:, None, :] - references[None, :, :]) ** 2, axis=2)
    nearest = np.argpartition(squared_distances, kth=COMPACT_K - 1, axis=1)[:, :COMPACT_K]

    predictions = []
    for row_index, neighbor_index in enumerate(nearest):
        distances = np.sqrt(squared_distances[row_index, neighbor_index])
        weights = 1.0 / (distances + 1.0e-6)
        neighbor_labels = labels[neighbor_index]
        static_vote = float(weights[neighbor_labels == CLASS_TO_INT["static_sitting"]].sum())
        rotation_vote = float(weights[neighbor_labels == CLASS_TO_INT["pelvic_rotation"]].sum())
        predicted_int = CLASS_TO_INT["pelvic_rotation"] if rotation_vote > static_vote else CLASS_TO_INT["static_sitting"]
        predictions.append(INT_TO_CLASS[predicted_int])

    return np.array(predictions, dtype=object)


def c_float(value: float) -> str:
    return f"{value:.8g}f"


def format_c_array(values: np.ndarray, indent: str = "    ") -> str:
    return indent + ", ".join(c_float(float(value)) for value in values)


def write_header(
    path: Path,
    mean: np.ndarray,
    scale: np.ndarray,
    references: np.ndarray,
    reference_labels: np.ndarray,
    compact_metrics: dict[str, float | int | str],
) -> None:
    lines: list[str] = []
    lines.append("/* Auto-generated compact KNN model for embedded pelvic-rotation detection. */")
    lines.append("/* Generated by analysis_scripts/ch6_reproduce_compact_knn.py. */")
    lines.append("/* Training windows: participants 1-4, 2 s windows, 1 s offline step. */")
    lines.append(
        f"/* One-shot participant 5 test: accuracy {compact_metrics['accuracy']:.4f}, "
        f"balanced accuracy {compact_metrics['balanced_accuracy']:.4f}, "
        f"F1 {compact_metrics['f1']:.4f}. */"
    )
    lines.append("#ifndef KNN_MODEL_H")
    lines.append("#define KNN_MODEL_H")
    lines.append("")
    lines.append("#include <float.h>")
    lines.append("#include <math.h>")
    lines.append("#include <stdint.h>")
    lines.append("")
    lines.append(f"#define KNN_FEATURE_COUNT {len(COMPACT_FEATURES)}")
    lines.append(f"#define KNN_REFERENCE_COUNT {len(references)}")
    lines.append(f"#define KNN_K {COMPACT_K}")
    lines.append("#define KNN_STATIC_SITTING 0")
    lines.append("#define KNN_PELVIC_ROTATION 1")
    lines.append("")
    lines.append("/* Feature order:")
    for index, feature in enumerate(COMPACT_FEATURES):
        lines.append(f" * {index:2d}: {feature}")
    lines.append(" */")
    lines.append("static const float KNN_MEAN[KNN_FEATURE_COUNT] = {")
    lines.append(format_c_array(mean))
    lines.append("};")
    lines.append("")
    lines.append("static const float KNN_SCALE[KNN_FEATURE_COUNT] = {")
    lines.append(format_c_array(scale))
    lines.append("};")
    lines.append("")
    lines.append("static const float KNN_REFERENCE[KNN_REFERENCE_COUNT][KNN_FEATURE_COUNT] = {")
    for row in references:
        lines.append("    {" + ", ".join(c_float(float(value)) for value in row) + "},")
    lines.append("};")
    lines.append("")
    lines.append("static const uint8_t KNN_LABEL[KNN_REFERENCE_COUNT] = {")
    for start in range(0, len(reference_labels), 32):
        chunk = reference_labels[start : start + 32]
        lines.append("    " + ", ".join(str(int(value)) for value in chunk) + ",")
    lines.append("};")
    lines.append("")
    lines.append("static inline uint8_t knn_predict_pelvic_rotation(const float features[KNN_FEATURE_COUNT])")
    lines.append("{")
    lines.append("    float x[KNN_FEATURE_COUNT];")
    lines.append("    float best_dist[KNN_K];")
    lines.append("    uint8_t best_label[KNN_K];")
    lines.append("")
    lines.append("    for (int i = 0; i < KNN_FEATURE_COUNT; i++) {")
    lines.append("        x[i] = (features[i] - KNN_MEAN[i]) / KNN_SCALE[i];")
    lines.append("    }")
    lines.append("")
    lines.append("    for (int i = 0; i < KNN_K; i++) {")
    lines.append("        best_dist[i] = FLT_MAX;")
    lines.append("        best_label[i] = KNN_STATIC_SITTING;")
    lines.append("    }")
    lines.append("")
    lines.append("    for (int ref = 0; ref < KNN_REFERENCE_COUNT; ref++) {")
    lines.append("        float d2 = 0.0f;")
    lines.append("        for (int i = 0; i < KNN_FEATURE_COUNT; i++) {")
    lines.append("            float diff = x[i] - KNN_REFERENCE[ref][i];")
    lines.append("            d2 += diff * diff;")
    lines.append("        }")
    lines.append("")
    lines.append("        int worst = 0;")
    lines.append("        for (int i = 1; i < KNN_K; i++) {")
    lines.append("            if (best_dist[i] > best_dist[worst]) {")
    lines.append("                worst = i;")
    lines.append("            }")
    lines.append("        }")
    lines.append("        if (d2 < best_dist[worst]) {")
    lines.append("            best_dist[worst] = d2;")
    lines.append("            best_label[worst] = KNN_LABEL[ref];")
    lines.append("        }")
    lines.append("    }")
    lines.append("")
    lines.append("    float static_vote = 0.0f;")
    lines.append("    float rotation_vote = 0.0f;")
    lines.append("    for (int i = 0; i < KNN_K; i++) {")
    lines.append("        float weight = 1.0f / (sqrtf(best_dist[i]) + 1.0e-6f);")
    lines.append("        if (best_label[i] == KNN_PELVIC_ROTATION) {")
    lines.append("            rotation_vote += weight;")
    lines.append("        } else {")
    lines.append("            static_vote += weight;")
    lines.append("        }")
    lines.append("    }")
    lines.append("")
    lines.append("    return (rotation_vote > static_vote) ? KNN_PELVIC_ROTATION : KNN_STATIC_SITTING;")
    lines.append("}")
    lines.append("")
    lines.append("#endif")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_plot(results: pd.DataFrame) -> None:
    metrics = ["accuracy", "balanced_accuracy", "precision", "recall", "f1"]
    labels = ["Accuracy", "Balanced acc.", "Precision", "Recall", "F1"]
    x = np.arange(len(metrics))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [3.2, 1.2]})
    for index, (_, row) in enumerate(results.iterrows()):
        offset = (index - 0.5) * width
        values = [row[metric] for metric in metrics]
        axes[0].bar(x + offset, values, width=width, label=row["model"])

    axes[0].set_ylim(0.88, 1.01)
    axes[0].set_ylabel("Score")
    axes[0].set_title("Held-out participant 5 performance")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(loc="upper right", frameon=False)

    axes[1].bar(results["model"], results["reference_points"], color=["#4c78a8", "#f58518"])
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Stored reference points")
    axes[1].set_title("Model size")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].grid(axis="y", alpha=0.25)

    fig.tight_layout()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "ch6_full_vs_compact_knn_comparison.png", dpi=220)
    fig.savefig(FIG_DIR / "ch6_full_vs_compact_knn_comparison.pdf")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce the compact prototype KNN model used in Chapter 6.")
    parser.add_argument(
        "--update-firmware-header",
        action="store_true",
        help="Also overwrite the deployed firmware header in the wearable firmware folder.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_feature_table()
    train_df, test_df = split_train_test(df)

    y_true = test_df["label"]
    full_pred, full_reference_count = train_full_knn(train_df, test_df)
    mean, scale, references, reference_labels = train_compact_knn(train_df)
    compact_pred = predict_compact(test_df, mean, scale, references, reference_labels)

    full_metrics = metric_row("Full KNN", y_true, full_pred, full_reference_count)
    compact_metrics = metric_row("Compact prototype KNN", y_true, compact_pred, len(references))
    results = pd.DataFrame([full_metrics, compact_metrics])
    results.to_csv(OUTPUT_DIR / "ch6_full_vs_compact_knn_comparison.csv", index=False)

    header_path = OUTPUT_DIR / "ch6_compact_knn_model_reproduced.h"
    write_header(header_path, mean, scale, references, reference_labels, compact_metrics)
    if args.update_firmware_header:
        write_header(FIRMWARE_HEADER, mean, scale, references, reference_labels, compact_metrics)

    write_plot(results)

    summary_lines = [
        "Compact KNN reproducibility summary",
        "",
        f"Feature table: {FEATURE_FILE.relative_to(PROJECT_ROOT)}",
        f"Training participants: {', '.join(TRAIN_PARTICIPANTS)}",
        f"Test participant: {TEST_PARTICIPANT}",
        f"Compact features: {', '.join(COMPACT_FEATURES)}",
        f"KMeans: {PROTOTYPES_PER_CLASS} prototypes per class, random_state={KMEANS_RANDOM_STATE}, n_init={KMEANS_N_INIT}",
        f"Compact KNN: k={COMPACT_K}, distance-weighted voting",
        "",
        results.to_string(index=False),
        "",
        f"Generated header: {header_path.relative_to(PROJECT_ROOT)}",
    ]
    if args.update_firmware_header:
        summary_lines.append("Updated firmware header: workspace wearable firmware folder")
    (OUTPUT_DIR / "ch6_compact_knn_reproducibility_summary.txt").write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    print(results.to_string(index=False))
    print(f"Wrote {OUTPUT_DIR / 'ch6_full_vs_compact_knn_comparison.csv'}")
    print(f"Wrote {header_path}")
    print(f"Wrote {FIG_DIR / 'ch6_full_vs_compact_knn_comparison.png'}")


if __name__ == "__main__":
    main()
