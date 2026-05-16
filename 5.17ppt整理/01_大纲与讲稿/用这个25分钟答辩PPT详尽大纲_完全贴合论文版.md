# 25 分钟答辩 PPT 详尽大纲（完全贴合论文版）

依据论文版本：`D:\最终论文\5.12论文重写`

建议结构：**22 页主讲 slides + 6 页 backup slides**

核心答辩定位：

> This thesis demonstrates the technical feasibility of a low-cost closed-loop sacrum/lower-back wearable sensing-to-cue pipeline for pelvic-region movement monitoring during prolonged sitting.

最重要边界：

- 可以说：technical feasibility, integrated sensing-to-cue pipeline, trend-level XIAO/Shimmer comparability, instructed pelvic-rotation detection in pilot data, compact embedded KNN deployment, local haptic cue execution.
- 不要说：clinical validation, anatomical pelvic-angle validation, robust spontaneous daily-use recognition, long-term comfort/battery proof, behavioural effectiveness, health benefit, commercial-ready product.

论文实际章节顺序：

```text
Chapter 1 Introduction
Chapter 2 Methods
Chapter 3 Results
Chapter 4 Discussion
Chapter 5 Conclusion
Appendix Supplementary Material
```

注：LaTeX 文件名仍是 `03-methods.tex`、`04-results.tex` 等，但最终论文中没有单独 Literature Review 章节，Related Work 已整合进 Chapter 1。

---

## 总体时间分配

| 部分 | Slides | 建议时间 |
|---|---:|---:|
| Opening, background, gap | 1-5 | 5 min |
| Research question and objective map | 6 | 2 min |
| Methods and system design | 7-12 | 7 min |
| Results | 13-20 | 8.5 min |
| Discussion, limitations, conclusion | 21-22 | 2.5 min |

总时间约 25 min。练习时允许 Slide 4、9、16 适当压缩。

---

# 主讲 Slides

## Slide 1. Title

建议时间：0:30

论文依据：

- `thesis.tex` 题目、作者、导师信息。
- `chapters/06-conclusion.tex` 的一句话结论。

页面目的：

- 开场。
- 立刻说明这是 low-cost wearable + pelvic-region movement + haptic cue 的技术可行性研究。

建议图：

- 右侧使用 `D:\最终论文\5.12论文重写\images\c3_device_external.png`

页面文字：

```text
AI-Enabled Wearable Device for Pelvic Motion Monitoring
and Haptic Intervention During Prolonged Sitting

Ruyang Luo / Yonggui Yuan
Supervisor: Prof. Bart Vanrumste
Co-supervisors: Prof. Jean-Marie Aerts, Meixing Liao

Technical feasibility of a low-cost sacrum/lower-back sensing-to-cue pipeline
```

上台语言：

> Good morning/afternoon. My name is Ruyang Luo. Today I will present my master thesis on an AI-enabled wearable device for pelvic motion monitoring and haptic intervention during prolonged sitting.  
> The main point is that this is a technical feasibility study. I developed and evaluated a low-cost closed-loop wearable pipeline that senses pelvic-region movement, supports labelled data collection, runs compact embedded detection logic, and delivers a local haptic cue.

边界提醒：

- 这里不要说 “clinical device” 或 “proven intervention”。

转场：

> I will start with why total sitting duration alone is not enough for this problem.

---

## Slide 2. Background: Prolonged Sitting and Sedentary Behaviour

建议时间：1:00

论文依据：

- Chapter 1, `Background and Motivation`
- Sedentary behaviour definition: SBRN definition, sitting/reclining/lying and `<=1.5 METs`
- Prolonged sitting as uninterrupted or insufficiently interrupted seated time

页面目的：

- 给出研究背景。
- 说明 prolonged sitting 是 sedentary behaviour 里的一个更具体问题。

建议画面：

- 左侧：简单层级图  
  `Sedentary behaviour → Prolonged sitting → Static seated bout / movement within bout`
- 右侧：3 个短 bullet。

页面文字：

```text
Prolonged sitting is a specific seated subset of sedentary behaviour

- Sedentary behaviour: waking behaviour <= 1.5 METs while sitting, reclining, or lying
- Prolonged sitting: uninterrupted or insufficiently interrupted seated time
- Risk is not described by total sedentary time alone
```

上台语言：

> Sedentary behaviour is usually defined as waking behaviour with low energy expenditure, below or equal to 1.5 METs, while sitting, reclining, or lying.  
> In this thesis, I focus more specifically on prolonged sitting, which means seated time that is uninterrupted or insufficiently interrupted.  
> The motivation is that total sedentary time is important, but it does not fully describe what happens inside a seated bout.

边界提醒：

- 不要花太久讲健康风险，这不是医学答辩。

转场：

> The next question is what is missing when we only measure duration.

---

## Slide 3. Motivation: Total Sitting Duration Is Not Enough

建议时间：1:00

论文依据：

- Chapter 1 says prolonged sitting is not fully described by total sedentary time alone.
- Relevant variables: bout duration, interruption frequency, movement variability within seated bouts.
- Pelvic rotation is treated as one measurable form of seated pelvic/lower-trunk movement.

建议画面：

- 两条横向时间线：
  - Bout A: 30 min, nearly static
  - Bout B: 30 min, with pelvic/lower-trunk movements
- 右侧强调：same duration, different movement pattern。

页面文字：

```text
Same sitting duration can hide different movement patterns

Duration:
how long the bout lasts

Interruptions:
when sitting is broken

Movement within bout:
whether pelvic/lower-trunk movement occurs
```

上台语言：

> Two seated bouts can have the same total duration but very different movement patterns. One person may remain almost static, while another may include meaningful postural variation within the same seated period.  
> This thesis focuses on that under-described layer: whether pelvic-region movement occurs during a seated bout. Pelvic rotation is used as a measurable target movement for this technical study.

边界提醒：

- 这里不要说 pelvic rotation 本身已经证明能改善健康，只说它是 measurable movement target。

转场：

> Existing monitoring technologies can measure sitting or posture, but they do not all address this specific sensing-to-cue problem.

---

## Slide 4. Related Work: Monitoring Technologies

建议时间：1:15

论文依据：

- Chapter 1, Table 1.1: `Comparison of technologies for sitting, posture, and prolonged-sitting monitoring`

建议画面：

- 不直接贴论文 Table 1.1，太密。
- 做 5 列横向简表或 5 个紧凑区块：
  1. Camera-based pose systems
  2. Smart chairs / pressure cushions
  3. Other body-worn sensors
  4. Research-grade wearable IMUs
  5. Microcontroller-based IMU wearable

页面文字：

```text
Existing directions

Camera systems:
rich posture information, but line-of-sight and privacy constraints

Smart chairs/cushions:
stable seat reference, but tied to one seat

Other body-worn sensors:
practical daily wear, but may not directly reflect pelvic movement

Research-grade IMUs:
high-quality reference/logging, often post-hoc and higher cost

Microcontroller IMU wearable:
low-cost local sensing + local cue, but needs task-specific validation
```

上台语言：

> The literature can be organised into several technology directions. Camera systems provide rich posture information, but they need line of sight and raise privacy concerns. Chair and pressure systems provide a stable seating reference, but they are tied to one seat.  
> Other body-worn sensors are practical, but wrist or thigh placement may not directly reflect pelvic movement. Research-grade IMUs provide high-quality measurements, but they are often used for logging or post-hoc analysis.  
> The direction of this thesis is a low-cost microcontroller-based IMU wearable, with local sensing, local detection, and local haptic cue delivery.

边界提醒：

- 如果提 low-cost，保持论文原边界：XIAO and Shimmer listed prices do not compare identical package contents.

转场：

> From this comparison, the research gap is not simply sitting detection, but a pelvis-focused closed loop.

---

## Slide 5. Research Gap and Scope Boundary

建议时间：1:15

论文依据：

- Chapter 1, `Research Gaps`
- Chapter 1, scope boundary: sensor agreement, field data collection, classification, embedded timing, local feedback; not behavioural change/health benefit.

建议画面：

- 左侧：4 个 research gaps。
- 右侧：scope boundary：Can evaluate / Cannot prove。

页面文字：

```text
Research gap

1. Sitting duration does not describe movement within a seated bout
2. Pelvic/lower-trunk movement is less directly monitored in daily seated contexts
3. Many systems rely on offline, external, or backend processing
4. Feedback is often not directly triggered by pelvic-rotation detection outcomes

Scope:
technical feasibility, not clinical or behavioural validation
```

上台语言：

> The reviewed work leaves four gaps for this thesis. First, most monitoring focuses on posture classes, sitting duration, or breaks, not movement within a seated bout. Second, pelvic or lower-trunk movement is less directly monitored in everyday seated contexts. Third, many systems rely on offline or external processing. Fourth, feedback may exist, but it is often not directly triggered by a local pelvic-movement detection outcome.  
> Therefore, the scope is technical feasibility: can the sensing-to-cue chain be built and tested? It is not a clinical validation study and not a behavioural intervention trial.

转场：

> These gaps lead directly to the research question and three objectives.

---

## Slide 6. Research Question, Objectives, and Contributions

建议时间：2:00

论文依据：

- Chapter 1, `Research Question and Objectives`
- Chapter 1, `Contributions`

建议画面：

- 上半部分：完整 RQ。
- 下半部分：3 objectives aligned to methods/results.
- 右下角小提示：system-level integration contribution.

页面文字：

```text
Research Question

To what extent is it technically feasible to develop and implement
a closed-loop, sacrum-mounted wearable system that monitors pelvic rotation
and provides real-time haptic feedback based on detection outcomes
to interrupt prolonged sitting in everyday seated contexts?

Objectives
1. Prototype development
2. Signal comparability with Shimmer
3. Detection and on-device feedback feasibility
```

上台语言：

> The main research question asks to what extent it is technically feasible to develop and implement a closed-loop sacrum-mounted wearable system. The system monitors pelvic rotation and provides real-time haptic feedback based on detection outcomes.  
> I addressed this through three objectives. First, prototype development. Second, signal comparability against a research-grade Shimmer IMU. Third, pelvic-rotation detection and on-device feedback feasibility.  
> The contribution is not a new sensor or a new machine-learning algorithm. It is the integration and technical evaluation of a pelvis-focused sensing-to-cue pipeline.

转场：

> I will now explain the methods in the same objective order.

---

## Slide 7. Methods Overview: Closed-Loop Sensing-to-Cue Architecture

建议时间：1:20

论文依据：

- Chapter 2 Methods, Figure 2.1 / `fig:system_architecture`

建议图：

- 重画论文 Figure 2.1 为更清楚的横向流程图。

页面文字：

```text
Closed-loop wearable research prototype

XIAO + IMU
→ BLE six-axis stream
→ Android labelled logging / PC inspection
→ CSV logs
→ offline features + model construction
→ compact KNN firmware export
→ on-device decision
→ inactivity timer
→ DRV2605L + coin vibration cue
```

上台语言：

> This is the full system architecture. The wearable streams six-axis IMU data by BLE to the Android field logger or the PC receiver. The Android tool records labels during field collection, while the PC tool supports researcher-side inspection.  
> Logged data are used for offline feature extraction and model construction. The compact KNN is then exported to firmware. On the device, the movement decision updates an inactivity timer, which triggers the haptic driver and coin vibration motor when the feedback condition is met.

边界提醒：

- 强调 pipeline，而不是单个模型。

转场：

> The physical prototype used for this pipeline is shown next.

---

## Slide 8. Objective 1 Method: Hardware and Firmware Components

建议时间：1:00

论文依据：

- Chapter 2, `Wearable Hardware and Firmware`
- Table 2.1 / `tab:prototype_components`
- Electrical connection details are in Methods but not necessary on main slide.

建议图：

- `c3_device_external.png`
- `c3_device_internal.png`

页面文字：

```text
Prototype components

- XIAO nRF54L15 Sense: MCU + IMU + BLE
- LSM6DS3TR-C: acceleration and angular velocity
- DRV2605L: haptic driver
- Coin vibration motor: local tactile reminder
- 500 mAh battery
- 3D-printed enclosure
```

上台语言：

> The prototype uses the XIAO nRF54L15 Sense as the central wearable node. It provides the microcontroller, BLE radio, and embedded IMU. The IMU measures three-axis acceleration and angular velocity.  
> For feedback, the prototype uses a DRV2605L haptic driver and a coin vibration motor. It also includes a 500 mAh battery and a 3D-printed enclosure. The aim was to build a compact research prototype that could both collect data and later run the compact decision logic.

转场：

> To collect labelled data, I also built receiver-side logging and inspection tools.

---

## Slide 9. Objective 1 Method: Data Logging and Inspection Tools

建议时间：1:00

论文依据：

- Chapter 2, `Data Logging and Inspection Tools`
- Chapter 3 Results, Android and PC front-end outcome figures

建议图：

- `c4_mobile_discovery.jpg`
- `c4_mobile_label_controls.jpg`
- `c4_mobile_live_telemetry_clean.jpg`
- `c4_pc_receiver_gui.png`

页面文字：

```text
Receiver-side tools

Android logger:
- BLE discovery
- per-device label control
- live telemetry check
- row-level labels in CSV

PC receiver:
- stream inspection
- live plots
- export and recording checks
```

上台语言：

> The Android logger supported BLE device discovery, per-device label control, and live telemetry checking. During an active annotation, the selected label and segment identifier were written to each received XIAO row.  
> The PC receiver supported researcher-side inspection with numeric values, logs, live plots, recording controls, and export. These tools were important because the classifier evaluation depended on clean labelled XIAO segments.

转场：

> After building the prototype, Objective 2 compared its IMU signal trends with a Shimmer reference.

---

## Slide 10. Objective 2 Method: Shimmer/XIAO Signal Comparability

建议时间：1:15

论文依据：

- Chapter 2, `Reference IMU Comparison`
- `Co-Located Shimmer/XIAO Comparison`
- `Field-Worn Paired Recording Subset and Preprocessing`
- `Signal Alignment, Metrics, and Statistical Handling`

建议图：

- 重画论文 co-located setup diagram `fig:colocated_shimmer_xiao_setup`
- 右侧小框：field-worn paired subset P1/P2 only.

页面文字：

```text
Two comparison conditions

1. Co-located setup
   XIAO prototype fixed on top of Shimmer
   shared imposed movement input

2. Field-worn paired subset
   planned for five participants
   usable paired recordings: P1 and P2

Interpretation:
descriptive trend-level comparability only
```

上台语言：

> Objective 2 compared the XIAO-based prototype with a research-grade Shimmer IMU.  
> In the co-located setup, the XIAO prototype was placed on top of the Shimmer and secured with tape so that both sensors received the same imposed movement input.  
> In the field-worn comparison, paired Shimmer/XIAO recordings were planned for five participants, but only P1 and P2 produced usable overlapping recordings.  
> The analysis used alignment and descriptive metrics only. It was not intended as absolute calibration, strict synchronisation, anatomical pelvic-angle validation, or clinical pelvic-kinematics validation.

转场：

> Objective 3 then focused on the pilot field study and the XIAO-based detection task.

---

## Slide 11. Objective 3 Method: Pilot Field Protocol and Data-Use Boundary

建议时间：1:25

论文依据：

- Chapter 2, `Pilot Field Protocol and Wearing Setup`
- Figure `fig:pilot_field_setup`
- Table `tab:objective3_data_use_boundary`
- Ethics statement: PRET approval G-2025-10284-R2(MIN), issued 5 January 2026.

建议图：

- `field_equipment_overview.jpg`
- `field_wearing_setup.jpg`
- `field_train_environment_anon.jpg`

页面文字：

```text
Pilot field study

- 5 volunteers, informed consent
- wearable attached near sacrum/lower-back region
- dynamic public-transport seated context
- retained main dataset: clean labelled train-seated XIAO segments
- labels: static sitting vs instructed anterior-posterior pelvic rotation

Bus recordings:
appendix context only
```

上台语言：

> Five volunteers participated after informed consent. The prototype was attached near the sacrum or lower-back region using the carrier plate and adhesive fixation.  
> The broader route included train and bus recordings, but the main Objective 3 classifier dataset was restricted to clean labelled train-seated recordings. These provided complete usable labelled seated data for all five participants.  
> The two retained labels were static sitting and instructed anterior-posterior pelvic rotation. Bus recordings were organised separately as appendix context because vehicle vibration and reliability issues made them less suitable as the main classifier evidence.

边界提醒：

- 不要说 bus data 完全没用；论文中是 appendix context / supplementary analysis。

转场：

> The retained labelled segments were then converted into window-level features.

---

## Slide 12. Objective 3 Method: Windowing, Classifier Evaluation, and Compact KNN

建议时间：1:40

论文依据：

- Chapter 2, `Windowing and Feature Extraction`
- `Offline Pelvic Rotation Detection Evaluation`
- `Compact KNN Construction for Embedded Deployment`
- `Firmware Timing, Memory, and Haptic Trigger Evaluation`

建议画面：

- 流程图：segments → windows → features → P1-P4 training/internal checks → held-out P5 → compact KNN → firmware.

页面文字：

```text
Offline detection task

Binary classification:
static_sitting vs pelvic_rotation

Offline windows:
2 s windows, 1 s step
retained only if >= 50 samples
90 full offline features

Person-independent evaluation:
P1-P4 training/internal checks
P5 held out for final test

Embedded route:
12 features + 128 KMeans prototypes
non-overlapping 2 s firmware windows
```

上台语言：

> The retained labelled XIAO segments were converted into fixed-length windows. For offline evaluation, I used 2-second windows with a 1-second step, and kept only windows with at least 50 samples.  
> The full offline feature set used nine signal streams and ten time-domain features, giving 90 features per window.  
> The detection task was binary: static sitting versus pelvic rotation. Participants P1 to P4 were used for training and internal model checks, while P5 was held out for final testing. No P5 data were used for scaling, feature selection, hyperparameter setting, KNN configuration, or model fitting.  
> For embedded deployment, the model was simplified to 12 features and 128 KMeans prototypes. The firmware used non-overlapping 2-second decision windows.

转场：

> I will now present the results, starting with Objective 1.

---

## Slide 13. Result 1: Prototype Implementation Outcome

建议时间：0:55

论文依据：

- Chapter 3 Results, `Prototype Implementation Outcome`
- Figure `fig:prototype_views`

建议图：

- `c3_device_external.png`
- `c3_device_internal.png`

页面文字：

```text
Objective 1 outcome

Implemented:
- IMU sensing
- BLE streaming
- Android labelled logging
- PC-based inspection
- window-level feature extraction
- compact KNN inference
- 10 min inactivity timer
- DRV2605L + 1 s local vibration cue
```

上台语言：

> Objective 1 was achieved by implementing the complete sensing-to-cue pipeline. The final prototype combined the XIAO IMU node, BLE streaming, Android field logging with row-level labels, PC monitoring, compact KNN inference, a 10-minute inactivity timer, the DRV2605L haptic driver, and a 1-second coin-motor vibration cue.  
> This means the system integration requirement was met. The prototype was not only a sensor logger; it was a closed-loop research unit.

转场：

> Objective 2 then checked whether the low-cost IMU captured movement trends comparable with Shimmer.

---

## Slide 14. Result 2: Co-Located Shimmer/XIAO Agreement

建议时间：1:20

论文依据：

- Chapter 3 Results, `Co-Located Shimmer/XIAO Agreement`
- Figure `fig:shimmer_xiao_comparison`
- Table `tab:colocated_validation_results`

建议图：

- `shimmer_xiao_comparison.png`

页面文字：

```text
Co-located trend agreement

Acceleration axes:
r = 0.856-0.923

Gyroscope axes:
r = 0.816-0.864

Estimated lag:
-0.020 to 0 s

NRMSE:
0.425-0.613
```

上台语言：

> In the co-located recording, the XIAO and Shimmer signals showed the same main movement peaks across the three acceleration channels and the three gyroscope channels.  
> Pearson correlations ranged from 0.856 to 0.923 for acceleration axes, and from 0.816 to 0.864 for gyroscope axes. The estimated lag stayed between minus 0.020 and 0 seconds.  
> These results support trend-level agreement under shared imposed movement input.

边界提醒：

- 这里立刻说 trend-level，不能说 accuracy of pelvic angle。

转场：

> The field-worn comparison is more realistic but also more limited.

---

## Slide 15. Result 3: Field-Worn Trend Agreement

建议时间：1:20

论文依据：

- Chapter 3 Results, `Pilot Field-Worn Trend Agreement`
- Table `tab:field_recording_summary`
- Table `tab:field_trend_results`
- Figure `fig:field_trend_comparison`

建议图：

- `c5_field_trend_comparison.png`

页面文字：

```text
Usable paired field-worn recordings: P1 and P2

Acceleration motion magnitude:
r = 0.918 and 0.855

Gyroscope magnitude:
r = 0.908 and 0.864

Max cross-correlation:
0.915-0.981

Estimated best lag:
1.2-1.3 s
```

上台语言：

> In the field-worn comparison, only two participants produced usable paired Shimmer and XIAO recordings.  
> For these two recordings, acceleration motion magnitude correlations were 0.918 and 0.855, and gyroscope magnitude correlations were 0.908 and 0.864. After lag correction, maximum cross-correlations reached 0.915 to 0.981.  
> The estimated best lag was 1.2 to 1.3 seconds, which is more likely related to the logging chain, clocks, or timestamping than a true sensor-response delay.  
> Because the paired dataset was small, I report these as descriptive trend-level metrics only.

转场：

> With this signal-comparability evidence, the next result is the XIAO-only classifier dataset.

---

## Slide 16. Result 4: Retained Classifier Dataset

建议时间：0:55

论文依据：

- Chapter 3 Results, `Offline Pelvic Rotation Detection`
- Table `tab:results_window_counts`

建议画面：

- 简洁数字表 + class imbalance bar chart。

页面文字：

```text
Retained Objective 3 dataset

98 clean labelled segment files
66 static-sitting segments
32 pelvic-rotation segments

2 s window counts:
static sitting: 12,489
pelvic rotation: 564
total: 13,053

Held-out P5:
3,497 static
165 pelvic rotation
class ratio approx. 21:1
```

上台语言：

> The retained classifier dataset contained 98 clean labelled segment files: 66 static-sitting segments and 32 pelvic-rotation segments.  
> After 2-second windowing, there were 13,053 windows in total: 12,489 static-sitting windows and 564 pelvic-rotation windows.  
> The held-out P5 test set was strongly imbalanced, with 3,497 static-sitting windows and 165 pelvic-rotation windows. Because of this imbalance, F1-score, precision, recall, and balanced accuracy are more informative than accuracy alone.

转场：

> The held-out model performance is shown next.

---

## Slide 17. Result 5: Held-Out P5 Classification Performance

建议时间：1:25

论文依据：

- Chapter 3 Results, Table `tab:ch6_model_results`

建议画面：

- 简化表格或 bar chart，突出 KNN。

页面文字：

```text
Held-out P5 pelvic-rotation performance

Model | Acc. | Bal. acc. | Precision | Recall | F1
LR    | .909 | .912 | .320 | .915 | .474
SVM   | .964 | .970 | .557 | .976 | .709
DT    | .978 | .925 | .711 | .867 | .781
RF    | .993 | .921 | .993 | .842 | .911
KNN   | .996 | .969 | .975 | .939 | .957

Selected model: k = 7 KNN
```

上台语言：

> On the held-out P5 participant, the selected k equals 7 KNN achieved the highest pelvic-rotation F1-score.  
> Its accuracy was 0.996, balanced accuracy was 0.969, precision was 0.975, recall was 0.939, and F1-score was 0.957.  
> The model comparison also shows different precision-recall trade-offs. Random forest had very high precision but lower recall. LR and SVM had higher recall but lower precision, which would create more false movement detections.  
> Based on this trade-off, KNN was selected for compact embedded implementation.

边界提醒：

- 说 “held-out P5” 和 “pilot instructed task”，不要说 general daily-life accuracy。

转场：

> The confusion matrix gives a more concrete view of these errors.

---

## Slide 18. Result 6: Confusion Matrix for Selected KNN

建议时间：1:00

论文依据：

- Chapter 3 Results, Figure `fig:ch6_knn_confusion_matrix`

建议图：

- `ch6_person5_confusion_matrix_selected_knn.png`

页面文字：

```text
Selected k = 7 KNN on held-out P5

Pelvic rotation:
155 / 165 detected
10 missed

Static sitting:
3,493 / 3,497 correctly classified
4 false positives
```

上台语言：

> For the selected k equals 7 KNN, 155 of the 165 pelvic-rotation windows were correctly identified, and 10 were missed.  
> For static sitting, 3,493 of the 3,497 windows were correctly classified, with only 4 false positives.  
> This supports technical detectability of instructed pelvic rotation in the retained pilot dataset. It does not prove robust recognition of spontaneous daily-life movement.

转场：

> The next question was whether this detection logic could fit into the wearable firmware.

---

## Slide 19. Result 7: Compact Embedded KNN and Memory Feasibility

建议时间：1:35

论文依据：

- Chapter 3 Results, `Compact Model and Embedded Operation`
- Table `tab:results_compact_features`
- Figure `fig:full_vs_compact_knn`

建议图：

- `ch6_full_vs_compact_knn_comparison.png`

页面文字：

```text
Why compact KNN was needed

Full KNN:
90 features
9,391 reference windows
reference matrix alone: 3,380,760 bytes
isolated build: 235.50% of Zephyr FLASH region

Compact KNN:
12 features
128 KMeans prototypes
held-out P5 F1 = 0.959
```

上台语言：

> A direct full-KNN firmware implementation was not feasible because KNN stores reference examples. The full offline KNN used 90 features and 9,391 reference windows. Storing only the reference matrix would require over 3.38 MB before adding scaling values, labels, firmware code, and operating-system overhead.  
> In the isolated full-KNN build, the linker reported 235.50 percent of the Zephyr FLASH region and failed.  
> The compact KNN reduced the model to 12 features and 128 KMeans prototypes. On the same held-out P5 windows, it achieved an F1-score of 0.959. I interpret this as preserving the relevant decision behaviour while greatly reducing storage, not as proving that the compact model is generally superior.

转场：

> Finally, I measured whether the compact decision path could run fast enough on the device.

---

## Slide 20. Result 8: Firmware Timing, Memory, and Haptic Cue

建议时间：1:20

论文依据：

- Chapter 3 Results, Table `tab:knn_timing`
- Chapter 2, `Firmware Timing, Memory, and Haptic Trigger Evaluation`

建议画面：

- 大数字。
- 右下角小 prototype 图。

页面文字：

```text
Embedded feasibility on XIAO nRF54L15 Sense

KNN inference only:
2.70 ms mean

Features + KNN total:
2.73 ms mean per 2 s window
2.70-2.76 ms range

Memory:
56.3 KB flash
9.3 KB RAM

Feedback:
10 min inactivity timer
1 s DRV2605L-controlled vibration cue
```

上台语言：

> The compact firmware was evaluated on the XIAO nRF54L15 Sense. Across 24 consecutive non-overlapping 2-second windows, KNN inference-only time was 2.70 milliseconds on average. The full online decision path, including compact feature extraction and KNN distance computation, required 2.73 milliseconds on average.  
> This is below 0.15 percent of the 2,000 millisecond window period. The firmware used 56.3 KB flash and 9.3 KB RAM.  
> The deployed firmware also executed the 10-minute inactivity timer and the 1-second DRV2605L-controlled vibration trigger. This supports compute and memory feasibility of the compact sensing-to-cue path.

边界提醒：

- 明确没有测 current draw、battery lifetime、long-term reliability、user perception、behaviour change。

转场：

> These results answer the research question, but only within a clear evidence boundary.

---

## Slide 21. Discussion: What the Thesis Supports and What It Does Not Establish

建议时间：1:20

论文依据：

- Chapter 4 Discussion, `Overall Technical Feasibility and Literature Comparison`
- Chapter 4, `Reference Signal Comparability and Validity Boundary`
- Chapter 4, `Detection, Deployment, and Haptic Feedback Boundaries`
- Table `tab:discussion_literature_comparison`

建议画面：

- 两列：Supported / Not established。

页面文字：

```text
Supported by this thesis

- Integrated low-cost sensing-to-cue prototype
- Trend-level XIAO/Shimmer signal comparability
- Instructed pelvic-rotation detection in pilot data
- Compact embedded KNN within timing and memory limits
- Local haptic cue execution

Not established

- Clinical pelvic kinematics
- Anatomical pelvic-angle validity
- Robust spontaneous daily-use recognition
- Long-term comfort, attachment reliability, or battery life
- Behavioural or health effectiveness
```

上台语言：

> Taken together, the results support a cautious technical-feasibility answer. The thesis shows that a low-cost sacrum or lower-back wearable can be built as an integrated sensing-to-cue pipeline. It can stream IMU data, support labelled field logging, be checked against a research-grade IMU at trend level, detect instructed pelvic rotation in pilot data, run a compact detector on the wearable, and trigger a local haptic cue.  
> However, the thesis does not establish clinical pelvic kinematics, anatomical pelvic-angle validity, robust spontaneous daily-use recognition, long-term comfort, battery lifetime, or behavioural effectiveness.

转场：

> The limitations and future work follow directly from this evidence boundary.

---

## Slide 22. Limitations, Future Work, and Conclusion

建议时间：1:40

论文依据：

- Chapter 4, Table `tab:discussion_limitations_future_work`
- Chapter 5 Conclusion

建议画面：

- 上半页：5 theme rows, very short.
- 下半页：final conclusion sentence.

页面文字：

```text
Main limitations and future work

Dataset:
small sample, instructed rotations → larger spontaneous datasets

Validation:
final independent test on one held-out participant, no external dataset
→ stricter LOSO reporting, prospective testing, external validation

Reference:
limited usable Shimmer paired data, trend-level metrics only
→ more paired sessions and better synchronization

Hardware:
attachment, BLE reliability, comfort, battery life not fully evaluated
→ long-duration wearing and battery tests

Feedback:
cue delivery implemented, but perception and behaviour not tested
→ user study and intervention evaluation

Conclusion:
Technical feasibility was demonstrated; clinical and behavioural effectiveness remain future work.
```

上台语言：

> The main limitations are the small participant sample, the instructed nature of the pelvic rotations, limited seated contexts, and no external dataset. The Shimmer validation was also limited by only two usable paired field recordings and trend-level metrics. Hardware robustness, comfort, waterproofing, BLE reliability, attachment repeatability, and battery life were not fully evaluated. Finally, the haptic cue was implemented technically, but user perception and behavioural impact were not tested.  
> In conclusion, this thesis demonstrated the technical feasibility of a low-cost closed-loop sacrum/lower-back wearable system for monitoring pelvic-region movement during prolonged sitting and delivering detection-outcome-based haptic feedback in pilot seated contexts. The next step is robust daily-use validation and behavioural evaluation.

结束语：

> Thank you for your attention. I am happy to answer your questions.

---

# Backup Slides

## Backup 1. Full Research Question and Objective Mapping

用途：

- 老师问 scope、objective 与结果如何对应。

页面内容：

```text
RQ:
To what extent is it technically feasible to develop and implement
a closed-loop, sacrum-mounted wearable system...

Objective 1:
Prototype development
Evidence: hardware, BLE, Android, PC, embedded logic, haptic cue

Objective 2:
Signal comparability with Shimmer
Evidence: co-located and two usable field-worn paired recordings

Objective 3:
Detection and on-device feedback feasibility
Evidence: held-out P5 detection, compact KNN, firmware timing/memory, cue
```

回答语言：

> The key phrase is technically feasible. Each objective tests one part of the technical chain, and the conclusion is limited to this chain.

---

## Backup 2. Data Inclusion and Bus Recording Boundary

用途：

- 老师问为什么主模型不用 bus data。

论文依据：

- Chapter 2, Table `tab:objective3_data_use_boundary`
- Appendix, `Bus Recording Handling`

页面内容：

```text
Main Objective 3 classifier dataset:
- clean labelled train-seated XIAO segments
- complete usable labelled seated data for all five participants

Excluded from main classifier dataset:
- unlabelled or unclear rows
- non-dynamic seated contexts
- battery/contact disconnection
- missing BLE stream
- segments inconsistent with instructed sitting protocol

Bus recordings:
- appendix context only
- affected by vehicle vibration and reliability issues
- supplementary train-person/test-person bus analysis reported separately
```

回答语言：

> The main classifier evidence was scoped to clean labelled train-seated recordings because this was the complete usable dataset across all five participants. Bus episodes were not ignored; they were handled in the appendix because vibration and reliability issues made them less suitable for the main evidence.

---

## Backup 3. Shimmer/XIAO Validity Boundary and Lag

用途：

- 老师问 Shimmer comparison 是否证明设备准确。

页面内容：

```text
Supported:
- comparable waveform peaks in co-located setup
- trend-level acceleration and gyroscope agreement
- descriptive field-worn magnitude correlations for P1/P2

Not supported:
- anatomical pelvic angle
- clinical pelvic kinematics
- absolute calibration
- strict hardware synchronization

Field-worn lag:
1.2-1.3 s likely reflects logging chain, clocks, or timestamping
```

回答语言：

> The Shimmer comparison supports trend-level signal comparability. It does not validate anatomical pelvic angles because there was no anatomical reference system and no hardware synchronisation trigger.

---

## Backup 4. KNN Selection and Evaluation Strictness

用途：

- 老师问为什么选 KNN、为什么只 P5 held-out。

论文依据：

- Chapter 2, Table `tab:objective3_classifier_settings`
- Chapter 3, Table `tab:ch6_model_results`

页面内容：

```text
Models compared:
LR, SVM, DT, RF, KNN

KNN candidate set:
k = 3, 5, 7

Model selection:
P1-P4 internal leave-one-participant checks
k = 7 retained

Final independent test:
P5 held out from scaling, feature selection, hyperparameter setting,
KNN configuration, fitting, and final evaluation setup

Boundary:
one held-out participant is useful but not full external validation
```

回答语言：

> I used P1-P4 for internal checks and kept P5 completely held out for the final test. This is a person-independent check, but I still present it as pilot evidence, not strong generalisation. Full leave-one-subject-out reporting and external validation are future work.

---

## Backup 5. Full KNN vs Compact KNN Memory Calculation

用途：

- 老师问为什么需要 12 features / 128 prototypes。

页面内容：

```text
Full KNN:
90 features
9,391 reference windows

Reference matrix:
9,391 x 90 x 4 bytes
= 3,380,760 bytes

Isolated full-KNN build:
3,443,596 bytes FLASH
235.50% of 1,428 KB Zephyr FLASH region
overflow by 1,981,324 bytes

Compact KNN:
12 features
128 KMeans prototypes
K = 7
held-out P5 F1 = 0.959
```

回答语言：

> The compact KNN was necessary because direct KNN stores reference examples. The compact version reduces both feature dimension and stored reference count, making the model fit the wearable firmware constraints.

---

## Backup 6. Haptic Cue, Ethics, and User-Study Boundary

用途：

- 老师问震动是否能改变久坐行为，或伦理/隐私如何处理。

页面内容：

```text
Implemented:
- DRV2605L haptic driver
- coin vibration motor
- 10 min inactivity timer
- 1 s local vibration cue

Not evaluated:
- vibration perception
- comfort and acceptability
- adherence
- sitting-interruption behaviour
- health or discomfort outcomes

Ethics:
PRET approval G-2025-10284-R2(MIN)
SMEC favourable review
field environment images anonymised
```

回答语言：

> The haptic subsystem was evaluated as technical cue delivery only. It does not prove that users perceive the cue as comfortable or that it changes sitting behaviour. That requires a separate user and behavioural intervention study.

---

# 关键答辩句型

## 创新点

> The contribution is not a novel IMU sensor or a novel machine-learning algorithm. The contribution is the integration and technical evaluation of a pelvis-focused sensing-to-cue pipeline: low-cost wearable sensing, labelled field logging, reference trend comparison, pilot pelvic-rotation detection, compact embedded deployment, and local haptic cue execution.

## 为什么不是 clinical validation

> Clinical validation would require anatomical reference measurements, controlled kinematic ground truth, and a clinical protocol. This thesis used IMU signal comparison and labelled pilot field data, so the correct interpretation is technical feasibility and trend-level comparability.

## 为什么样本少还可以

> The sample size limits generalisation, and I acknowledge that clearly. The purpose was a pilot feasibility study. The results show that the pipeline can be built, the data can be collected, the instructed movement class can be detected in the pilot data, and the compact model can run on the target wearable.

## 为什么 P5 held-out 还不够严格

> P5 held-out testing provides one participant-independent final test, but it does not replace full leave-one-subject-out reporting, prospective testing, or external validation. That is why I describe the result as pilot technical detectability rather than robust generalisation.

## 能不能用于真实日常生活

> Not yet as a validated daily-use system. The current result supports technical feasibility in pilot seated contexts with instructed pelvic rotation. Daily-life use would require spontaneous seated movement data, long-term attachment and comfort testing, battery-life evaluation, and behavioural outcome evaluation.

---

# 制作 PPT 的执行建议

1. 每页只保留 1 个主信息，不把论文表格整张搬上去。
2. 结果页优先用论文中的真实图：prototype、field setup、Shimmer comparison、field trend、confusion matrix、full vs compact KNN。
3. 每次讲强结果时立刻加限定语：
   - `in pilot instructed data`
   - `trend-level only`
   - `not anatomical pelvic-angle validation`
   - `not behavioural effectiveness`
4. `AI` 不要讲太多。论文真正核心是 wearable pipeline + compact embedded detection。
5. 25 分钟练习时重点保留：
   - Slide 6 RQ/objectives
   - Slide 14-15 Shimmer/XIAO results
   - Slide 17-20 detection/embedded results
   - Slide 21-22 evidence boundary and conclusion

