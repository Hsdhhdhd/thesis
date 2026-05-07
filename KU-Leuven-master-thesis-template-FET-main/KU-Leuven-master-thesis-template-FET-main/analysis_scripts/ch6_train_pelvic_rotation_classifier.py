from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[1]
DATA_ROOT = WORKSPACE_ROOT / "5人在火车上的分类"
OUTPUT_DIR = PROJECT_ROOT / "analysis_outputs"
FIG_DIR = PROJECT_ROOT / "figs"

WINDOW_MS = 2000
STEP_MS = 1000
MIN_SAMPLES_PER_WINDOW = 50
GRAVITY = 9.80665

IMU_COLUMNS = ["accel_x", "accel_y", "accel_z", "gyro_x", "gyro_y", "gyro_z"]
SELECTED_KNN_MODEL = "KNN k=7"
REPORT_MODELS = [
    "Logistic Regression",
    "SVM",
    "Decision Tree",
    "Random Forest",
    SELECTED_KNN_MODEL,
]


def label_from_filename(path):
    name = path.name.lower()
    if "pelvic_rotation" in name:
        return "pelvic_rotation"
    if "static_sitting" in name:
        return "static_sitting"
    raise ValueError(f"Cannot infer label from file name: {path.name}")


def person_from_path(path):
    return path.parent.name


def read_segment(path):
    usecols = ["epoch_ms", *IMU_COLUMNS]
    df = pd.read_csv(path, usecols=usecols)
    for col in usecols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=usecols).sort_values("epoch_ms")
    df = df.drop_duplicates()
    return df


def add_derived_signals(values):
    accel = values[:, :3]
    gyro = values[:, 3:6]
    acc_mag = np.linalg.norm(accel, axis=1)
    gyro_mag = np.linalg.norm(gyro, axis=1)
    acc_motion_mag = np.abs(acc_mag - GRAVITY)
    return np.column_stack([values, acc_mag, acc_motion_mag, gyro_mag])


def robust_iqr(x):
    return float(np.percentile(x, 75) - np.percentile(x, 25))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def extract_features(window):
    signal_names = [
        "accel_x",
        "accel_y",
        "accel_z",
        "gyro_x",
        "gyro_y",
        "gyro_z",
        "acc_mag",
        "acc_motion_mag",
        "gyro_mag",
    ]
    features = {}
    for idx, name in enumerate(signal_names):
        x = window[:, idx]
        features[f"{name}_mean"] = float(np.mean(x))
        features[f"{name}_std"] = float(np.std(x))
        features[f"{name}_min"] = float(np.min(x))
        features[f"{name}_max"] = float(np.max(x))
        features[f"{name}_range"] = float(np.max(x) - np.min(x))
        features[f"{name}_rms"] = rms(x)
        features[f"{name}_median"] = float(np.median(x))
        features[f"{name}_iqr"] = robust_iqr(x)

        dx = np.diff(x)
        if len(dx):
            features[f"{name}_diff_abs_mean"] = float(np.mean(np.abs(dx)))
            features[f"{name}_diff_std"] = float(np.std(dx))
        else:
            features[f"{name}_diff_abs_mean"] = 0.0
            features[f"{name}_diff_std"] = 0.0
    return features


def window_segment(path):
    label = label_from_filename(path)
    person = person_from_path(path)
    df = read_segment(path)
    if df.empty:
        return [], None

    t = df["epoch_ms"].to_numpy(dtype=np.int64)
    values = df[IMU_COLUMNS].to_numpy(dtype=float)
    values = add_derived_signals(values)

    duration_s = (t[-1] - t[0]) / 1000.0
    summary = {
        "person": person,
        "file": path.name,
        "label": label,
        "rows": len(t),
        "duration_s": duration_s,
        "median_dt_ms": float(np.median(np.diff(t))) if len(t) > 1 else np.nan,
    }

    rows = []
    start = int(t[0])
    end = int(t[-1])
    window_index = 0
    current = start
    while current + WINDOW_MS <= end:
        left = np.searchsorted(t, current, side="left")
        right = np.searchsorted(t, current + WINDOW_MS, side="left")
        if right - left >= MIN_SAMPLES_PER_WINDOW:
            window = values[left:right]
            features = extract_features(window)
            features.update(
                {
                    "person": person,
                    "source_file": path.name,
                    "window_index": window_index,
                    "window_start_epoch_ms": current,
                    "window_end_epoch_ms": current + WINDOW_MS,
                    "sample_count": right - left,
                    "label": label,
                }
            )
            rows.append(features)
        window_index += 1
        current += STEP_MS
    summary["windows"] = len(rows)
    return rows, summary


def build_dataset():
    all_rows = []
    summaries = []
    for path in sorted(DATA_ROOT.glob("person_*/*.csv")):
        rows, summary = window_segment(path)
        if summary is not None:
            summaries.append(summary)
        all_rows.extend(rows)
    feature_df = pd.DataFrame(all_rows)
    summary_df = pd.DataFrame(summaries)
    return feature_df, summary_df


def make_models():
    return {
        "Dummy majority": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42),
        ),
        "SVM": make_pipeline(
            StandardScaler(),
            SVC(class_weight="balanced", probability=True, random_state=42),
        ),
        "KNN k=3": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=3, weights="distance"),
        ),
        "KNN k=5": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=5, weights="distance"),
        ),
        "KNN k=7": make_pipeline(
            StandardScaler(),
            KNeighborsClassifier(n_neighbors=7, weights="distance"),
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight="balanced",
            min_samples_leaf=5,
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
    }


def evaluate_models(feature_df):
    train_df = feature_df[feature_df["person"].isin(["person_1", "person_2", "person_3", "person_4"])].copy()
    test_df = feature_df[feature_df["person"].eq("person_5")].copy()
    feature_cols = [
        col
        for col in feature_df.columns
        if col
        not in {
            "person",
            "source_file",
            "window_index",
            "window_start_epoch_ms",
            "window_end_epoch_ms",
            "sample_count",
            "label",
        }
    ]

    x_train = train_df[feature_cols]
    y_train = train_df["label"]
    x_test = test_df[feature_cols]
    y_test = test_df["label"]

    labels = ["static_sitting", "pelvic_rotation"]
    results = []
    fitted_models = {}
    predictions = {}
    for name, model in make_models().items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        fitted_models[name] = model
        predictions[name] = pred
        results.append(
            {
                "model": name,
                "train_windows": len(train_df),
                "test_windows": len(test_df),
                "accuracy": accuracy_score(y_test, pred),
                "balanced_accuracy": balanced_accuracy_score(y_test, pred),
                "precision_pelvic_rotation": precision_score(
                    y_test, pred, labels=labels, pos_label="pelvic_rotation", zero_division=0
                ),
                "recall_pelvic_rotation": recall_score(
                    y_test, pred, labels=labels, pos_label="pelvic_rotation", zero_division=0
                ),
                "f1_pelvic_rotation": f1_score(
                    y_test, pred, labels=labels, pos_label="pelvic_rotation", zero_division=0
                ),
            }
        )

    return pd.DataFrame(results), fitted_models, predictions, train_df, test_df, feature_cols


def safe_slug(name):
    return name.lower().replace(" ", "_").replace("-", "_")


def save_confusion_matrix(y_true, y_pred, model_name, suffix="best_model"):
    labels = ["static_sitting", "pelvic_rotation"]
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"true_{x}" for x in labels], columns=[f"pred_{x}" for x in labels])
    cm_df.to_csv(OUTPUT_DIR / f"ch6_person5_confusion_matrix_{suffix}.csv")

    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels=["Static sitting", "Pelvic rotation"], rotation=25, ha="right")
    ax.set_yticks(range(len(labels)), labels=["Static sitting", "Pelvic rotation"])
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"Person 5 test confusion matrix\n{model_name}")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"ch6_person5_confusion_matrix_{suffix}.png", dpi=250)
    plt.close(fig)


def save_feature_importance(model, feature_cols):
    if not hasattr(model, "feature_importances_"):
        return
    importances = pd.DataFrame(
        {"feature": feature_cols, "importance": model.feature_importances_}
    ).sort_values("importance", ascending=False)
    importances.to_csv(OUTPUT_DIR / "ch6_random_forest_feature_importance.csv", index=False)

    top = importances.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.barh(top["feature"], top["importance"])
    ax.set_xlabel("Random forest importance")
    ax.set_title("Top 15 IMU features")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ch6_random_forest_feature_importance.png", dpi=250)
    plt.close(fig)


def save_prediction_tables(test_df, y_pred, model_name):
    pred_df = test_df[
        [
            "person",
            "source_file",
            "window_index",
            "window_start_epoch_ms",
            "window_end_epoch_ms",
            "sample_count",
            "label",
        ]
    ].copy()
    pred_df["predicted_label"] = y_pred
    pred_df["correct"] = pred_df["label"].eq(pred_df["predicted_label"])
    pred_df.to_csv(OUTPUT_DIR / "ch6_person5_window_predictions_best_f1.csv", index=False)

    rows = []
    for source_file, group in pred_df.groupby("source_file", sort=True):
        true_label = group["label"].iloc[0]
        windows = len(group)
        predicted_rotation = int(group["predicted_label"].eq("pelvic_rotation").sum())
        predicted_static = int(group["predicted_label"].eq("static_sitting").sum())
        correct = int(group["correct"].sum())
        rows.append(
            {
                "source_file": source_file,
                "true_label": true_label,
                "windows": windows,
                "predicted_static_sitting": predicted_static,
                "predicted_pelvic_rotation": predicted_rotation,
                "correct_windows": correct,
                "window_accuracy": correct / windows if windows else np.nan,
                "model": model_name,
            }
        )
    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "ch6_person5_prediction_by_segment.csv", index=False)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    feature_df, summary_df = build_dataset()
    feature_df.to_csv(OUTPUT_DIR / "ch6_window_features_2s.csv", index=False)
    summary_df.to_csv(OUTPUT_DIR / "ch6_segment_summary.csv", index=False)

    person_summary = (
        feature_df.groupby(["person", "label"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    person_summary.to_csv(OUTPUT_DIR / "ch6_window_count_by_person.csv", index=False)

    results, models, preds, train_df, test_df, feature_cols = evaluate_models(feature_df)
    results = results.sort_values(["f1_pelvic_rotation", "balanced_accuracy"], ascending=False)
    results.to_csv(OUTPUT_DIR / "ch6_person5_model_results.csv", index=False)

    thesis_rows = []
    for model_name in ["Logistic Regression", "SVM", "Decision Tree", "Random Forest"]:
        thesis_rows.append(results[results["model"].eq(model_name)].iloc[0].copy())
    selected_knn = results[results["model"].eq(SELECTED_KNN_MODEL)].iloc[0].copy()
    selected_knn["model"] = "KNN"
    thesis_rows.append(selected_knn)
    thesis_results = pd.DataFrame(thesis_rows)
    thesis_results["model"] = pd.Categorical(
        thesis_results["model"],
        categories=[
            "Logistic Regression",
            "SVM",
            "Decision Tree",
            "Random Forest",
            "KNN",
        ],
        ordered=True,
    )
    thesis_results = thesis_results.sort_values("model")
    thesis_results.to_csv(OUTPUT_DIR / "ch6_thesis_five_model_results.csv", index=False)

    finalist_results = results[results["model"].isin(REPORT_MODELS)]
    best_name = finalist_results.iloc[0]["model"]
    y_test = test_df["label"]
    best_pred = preds[best_name]
    save_prediction_tables(test_df, best_pred, best_name)
    save_confusion_matrix(y_test, best_pred, best_name, suffix="best_f1")
    for model_name, pred in preds.items():
        save_confusion_matrix(y_test, pred, model_name, suffix=safe_slug(model_name))

    if best_name == "Random Forest":
        save_feature_importance(models[best_name], feature_cols)
    elif "Random Forest" in models:
        save_feature_importance(models["Random Forest"], feature_cols)

    report = classification_report(y_test, best_pred, labels=["static_sitting", "pelvic_rotation"], zero_division=0)
    (OUTPUT_DIR / "ch6_person5_best_model_report.txt").write_text(
        f"Best model: {best_name}\n\n{report}\n", encoding="utf-8"
    )

    print("Window length:", WINDOW_MS / 1000, "s; step:", STEP_MS / 1000, "s")
    print("Person/window summary")
    print(person_summary.to_string(index=False))
    print("\nModel results on held-out person_5")
    print(results.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    print("\nBest model:", best_name)
    print(report)


if __name__ == "__main__":
    main()
