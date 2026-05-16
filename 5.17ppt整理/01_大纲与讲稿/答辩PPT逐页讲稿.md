# 答辩 PPT 逐页内容与台上讲稿

论文题目：AI-Enabled Wearable Device for Pelvic Motion Monitoring and Haptic Intervention During Prolonged Sitting

建议总时长：约 25 分钟  
建议页数：18 页  
节奏建议：前 4 页讲背景和问题，5-11 页讲系统和方法，12-17 页讲验证和结果，18 页收束结论与限制。

---

## Slide 1. Title

建议时间：0.5 min

### PPT 放什么

- 论文题目
- 姓名、导师、学院、日期
- 右侧或下方放原型图：`images/c3_device_external.png`

### 页面文字

- AI-Enabled Wearable Device for Pelvic Motion Monitoring and Haptic Intervention During Prolonged Sitting
- Ruyang Luo, Yonggui Yuan
- Master thesis, KU Leuven

### 台上说的话

Good morning/afternoon everyone. My thesis is titled **AI-Enabled Wearable Device for Pelvic Motion Monitoring and Haptic Intervention During Prolonged Sitting**.

The main idea is to build a small wearable device that can sense pelvic movement during sitting, run a simple movement detector on the device itself, and give local haptic feedback when the user has remained static for a configured period.

This work should be understood as a **technical feasibility study**. It is not a clinical posture-diagnosis system, and it does not yet prove behavioural change. My focus is whether the complete technical chain can work: sensing, data collection, classification, embedded deployment, and haptic actuation.

---

## Slide 2. Motivation: Why Prolonged Static Sitting?

建议时间：1 min

### PPT 放什么

- 一张久坐办公或通勤的简图
- 标出 lower back / pelvis 区域
- 可以用简单图标：desk work, study, commuting

### 页面文字

- Prolonged sitting is common in work, study, and commuting.
- This thesis focuses on **prolonged static sitting**, not all sedentary behaviour.
- Target movement: detectable pelvic motion during sitting.

### 台上说的话

Many daily activities involve prolonged sitting, for example desk work, studying, and commuting. In the literature, sedentary behaviour is often defined by low energy expenditure while sitting or reclining. However, my thesis focuses on a narrower problem: **prolonged static sitting**.

This distinction is important. A person can remain sedentary but still change posture or move the pelvis. For my system, the key question is not whether the person is seated in general, and not whether the posture is clinically correct. The key question is whether there has been a detectable movement around the pelvis during a recent sitting period.

So the system is designed around a practical feedback target: if no pelvic movement is detected for a period of time, the wearable can provide a local vibration cue.

---

## Slide 3. Existing Approaches and Gap

建议时间：1.2 min

### PPT 放什么

做一个四列对比表：

| Approach | Strength | Limitation |
|---|---|---|
| Camera | Rich posture information | Fixed room, privacy, line of sight |
| Smart chair/cushion | Seat-level pressure | Bound to one seat |
| Wrist wearable | Mobile | Indirect for pelvic motion |
| This work | Pelvis-focused and mobile | Preliminary prototype |

### 页面文字

- Cameras and instrumented chairs are environment-bound.
- Wrist sensors are mobile but not pelvis-specific.
- Gap: mobile, pelvis-focused sensing with local feedback.

### 台上说的话

There are already several ways to monitor sitting or posture. Camera-based systems can provide rich spatial information, but they depend on a prepared environment, line of sight, and they raise privacy concerns. Smart chairs or pressure cushions avoid cameras, but they only work on the instrumented seat.

Wrist wearables are mobile, but they measure the wrist rather than the pelvis. A smartwatch may detect typing or phone use, even when the pelvis remains static. This is not ideal for my target movement.

The research gap I address is therefore a mobile, body-worn system placed near the pelvis, which can sense the relevant segment and provide feedback locally. The novelty is not a new clinical posture metric. It is the integration of the full pipeline into a compact wearable prototype.

---

## Slide 4. Research Questions

建议时间：1 min

### PPT 放什么

- 三个 research questions，用 3 个图标表示：
  - Sensor validity
  - Field data collection
  - Embedded classification and feedback

### 页面文字

RQ1. Can the low-cost embedded IMU capture motion patterns consistent with Shimmer?  
RQ2. Can the system support real-time field data collection and annotation?  
RQ3. Can static sitting and pelvic rotation be classified and deployed on-device?

### 台上说的话

The thesis is organised around three research questions.

First, I ask whether the low-cost embedded IMU captures motion patterns that are sufficiently consistent with a research-grade Shimmer IMU. This is a sensor-validity question.

Second, I ask whether the wearable and the data-collection tools can support field recording and annotation in realistic contexts, especially during the pilot route and train journeys.

Third, I ask whether the collected IMU data can distinguish static sitting from pelvic rotation, and whether a compact model can run on the wearable efficiently enough to support haptic feedback.

Together, these three questions cover sensing, data collection, and embedded AI deployment.

---

## Slide 5. System Overview

建议时间：1.2 min

### PPT 放什么

- 放论文 Figure 2.1 系统架构图，或重新画流程：
  - IMU -> XIAO nRF54L15 -> classifier / inactivity logic -> DRV2605L -> vibration motor
  - BLE -> Android app / PC receiver

### 页面文字

- Pelvis-mounted IMU measures acceleration and gyroscope signals.
- BLE stream supports logging and labelling.
- On-device classifier resets inactivity timer when pelvic movement is detected.
- Haptic motor gives a local reminder after 10 min without detected movement.

### 台上说的话

This slide shows the system architecture. The XIAO nRF54L15 Sense contains the microcontroller, BLE radio, and IMU. It measures three-axis acceleration and three-axis angular velocity near the pelvis.

During experiments, the same six-channel signal is streamed over BLE to an Android application or a PC receiver. These tools are used for logging, annotation, and inspection.

For deployment, the important part is the local loop. The microcontroller extracts features from recent IMU windows, classifies whether pelvic rotation occurred, and updates an inactivity timer. If no pelvic rotation is detected for 10 minutes, the DRV2605L drives a coin vibration motor for one second.

So the phone and PC are useful for research collection, but the final feedback logic is designed to run locally on the wearable.

---

## Slide 6. Hardware Prototype

建议时间：1.3 min

### PPT 放什么

- `images/c3_device_external.png`
- `images/c3_device_internal.png`
- 小表格列出主要组件

### 页面文字

- XIAO nRF54L15 Sense: MCU + IMU + BLE
- DRV2605L haptic driver
- Coin vibration motor
- 500 mAh battery
- 3D-printed enclosure
- Prototype cost: below about EUR 30, excluding phone/PC/Shimmer

### 台上说的话

This is the physical prototype. The main board is the Seeed Studio XIAO nRF54L15 Sense. It integrates the microcontroller, BLE radio, and an LSM6DS3TR-C IMU, so the number of external components is small.

For haptic feedback, I use a DRV2605L haptic driver and a small coin vibration motor. The system is powered by a 500 mAh battery inside the enclosure. The orange part is a 3D-printed enclosure, and the electronics are mounted on the black carrier plate.

The prototype was designed for research feasibility, not as a final consumer product. It is low-cost and compact, but the mechanical reliability is still limited. In particular, battery contact stability later became one reason for recording gaps during field use.

---

## Slide 7. Wearing Position

建议时间：1 min

### PPT 放什么

- `images/c3_wearing_on_body.jpg`
- 标注 sacrum / lower-back / pelvic region

### 页面文字

- Worn near the sacrum / lower back.
- More directly related to pelvic movement than wrist placement.
- Same body location used for sensing and haptic cue.
- Attachment method: sterile island dressing for pilot sessions.

### 台上说的话

The device is worn near the sacrum, in the lower-back or pelvic region. This placement is chosen because the target movement is pelvic motion, not arm movement or general whole-body activity.

Compared with a wrist sensor, a sacral or lower-back IMU is more directly informative for anterior-posterior pelvic movement during sitting. It also means that the feedback cue is delivered close to the same body area being monitored.

For the pilot sessions, the device was attached using a sterile island dressing and double-sided tape. This method was simple and replaceable between participants, but it is still a temporary research attachment method, not the final solution for long-term daily wear.

---

## Slide 8. Android Field Collection

建议时间：1.3 min

### PPT 放什么

- 三张手机界面并排：
  - `images/c4_mobile_discovery.jpg`
  - `images/c4_mobile_label_controls.jpg`
  - `images/c4_mobile_live_telemetry_clean.jpg`

### 页面文字

- BLE scanning and connection
- Two-device live IMU telemetry
- Per-device activity labelling
- CSV logging with timestamps, IMU channels, GPS metadata, and labels

### 台上说的话

For field data collection, I developed an Android application. It scans for nearby wearable devices, connects through BLE, subscribes to IMU notifications, and records the converted acceleration and gyroscope values into CSV files.

The app can connect to two wearable devices simultaneously, which was useful during field sessions. It also supports per-device activity labelling. When a label is active, the label and segment ID are written into every row received from that device.

This design is important because later processing can recover labelled time segments from the raw log. The labels are not automatically inferred by the phone; they are entered during the session and then used to select clean static-sitting and pelvic-rotation segments.

---

## Slide 9. PC Receiver and Debugging

建议时间：1 min

### PPT 放什么

- `images/c4_pc_receiver_gui.png`

### 页面文字

- Same BLE interface as Android app
- Live acceleration and gyroscope plots
- Researcher-side inspection
- CSV and Excel export

### 台上说的话

In addition to the Android app, I also developed a PC receiver. It uses the same BLE notification format, but the purpose is different.

The PC tool is mainly for bench testing, debugging, and signal inspection before and after field sessions. It shows live acceleration, angular velocity, motion acceleration, and other derived signals. This makes it easier to detect connection problems, unexpected axis behaviour, or sensor saturation.

So the Android app is mainly for mobile field collection, while the PC receiver is mainly for researcher-side monitoring and development. Together, they support the same data pipeline.

---

## Slide 10. Data Processing Pipeline

建议时间：1.3 min

### PPT 放什么

画流程图：

Raw IMU CSV -> clean labelled seated segments -> 2 s windows / 1 s step -> 90 features -> model comparison -> compact KNN

### 页面文字

- Clean labelled train-sitting segments only
- 2 s sliding windows, 1 s step
- 6 raw IMU channels + 3 magnitude signals
- 10 time-domain statistics per signal
- 90-dimensional feature vector

### 台上说的话

After data collection, I selected clean labelled seated segments from train journeys. Segments with battery-disconnection gaps, non-seated activity, or unlabelled rows were excluded from the classifier dataset.

The retained IMU data were divided into 2 second windows with a 1 second step. For each window, I used the six raw IMU channels: acceleration x, y, z and gyroscope x, y, z. I also derived three magnitude signals: acceleration magnitude, gravity-removed acceleration motion magnitude, and gyroscope magnitude.

For each of these nine signals, I calculated ten time-domain statistics, such as mean, standard deviation, range, RMS, median, interquartile range, and first-difference features. This gives a 90-dimensional feature vector per window.

The goal is not anatomical angle estimation. It is binary detection: static sitting versus pelvic rotation.

---

## Slide 11. Compact KNN for Embedded AI

建议时间：1.3 min

### PPT 放什么

对比图或表：

| Offline full KNN | Compact deployed KNN |
|---|---|
| 90 features | 12 features |
| 9,391 training windows | 128 prototypes |
| PC/offline baseline | Runs on XIAO |

可以加 `Table 3.5` 的 12 features 简化版。

### 页面文字

- Full KNN is memory-heavy.
- Compact model uses 12 selected features.
- KMeans creates 64 prototypes per class.
- Distance-weighted KNN, k = 7.

### 台上说的话

The full KNN baseline stores all training windows, so it is not ideal for a small microcontroller. To make KNN deployable, I used two reductions.

First, I selected a compact subset of 12 features. These are mainly gyroscope and acceleration-range features, which are interpretable for the expected difference between static sitting and deliberate pelvic movement.

Second, I used KMeans prototype compression. Instead of storing all 9,391 training windows, the compact model stores 64 prototypes for each class, so 128 prototypes in total.

The deployed classifier is still a KNN model with k equals 7 and distance-weighted voting, but it is much smaller. This step is central because it connects the offline classifier to TinyML-style embedded deployment.

---

## Slide 12. Shimmer Co-Located Validation

建议时间：1.5 min

### PPT 放什么

- `images/shimmer_placement.png`
- `images/shimmer_xiao_comparison.png`
- 小数字框：Pearson r = 0.816-0.923, lag within 20 ms

### 页面文字

- XIAO and Shimmer fixed to the same mounting surface
- Resampled and aligned by cross-correlation
- Co-located correlations: 0.816-0.923
- Estimated lag: -0.020 to 0 s

### 台上说的话

To check whether the low-cost embedded IMU captures comparable movement trends, I first performed a co-located comparison with a Shimmer reference sensor.

The XIAO-based wearable and the Shimmer were fixed to the same mounting surface and moved together as one rigid setup. The signals were resampled to a common time base and aligned by cross-correlation.

The waveform comparison shows that the main movement peaks are visible in both devices across acceleration and gyroscope channels. Across all axes, Pearson correlations ranged from 0.816 to 0.923. The estimated lag was between minus 0.020 seconds and 0 seconds.

This does not mean the device estimates clinical pelvic angles. It means that for this movement-detection task, the low-cost IMU captures timing and trend information that is sufficiently consistent with the Shimmer reference.

---

## Slide 13. Pilot Field Study

建议时间：1.3 min

### PPT 放什么

- `images/c6_equipment_overview_rotated.jpg`
- `images/c6_train_environment_1_anon.jpg`
- `images/c6_train_environment_2_anon.jpg`

### 页面文字

- Five volunteers
- Urban route including walking, train travel, meal period, and return journey
- Paired Shimmer/XIAO field recordings intended for all five
- Only two valid paired Shimmer logs
- Labelled classifier data use XIAO train-sitting segments

### 台上说的话

The pilot field study involved five volunteers. Participants wore the prototype near the sacrum during an extended route that included walking, train travel, a meal period, the return journey, and walking back.

The study had two roles. First, it provided paired Shimmer and XIAO recordings for field-worn trend comparison. This was intended for all five participants, but only two produced usable paired Shimmer logs. The other Shimmer logs failed and were excluded from the field-worn Shimmer comparison.

Second, the pilot study provided labelled XIAO data for the classifier. For the classification experiment, I used clean labelled seated segments from train journeys, where participants alternated between static sitting and instructed anterior-posterior pelvic rotation.

---

## Slide 14. Field-Worn Shimmer/XIAO Trend Agreement

建议时间：1.3 min

### PPT 放什么

- `images/c5_field_trend_comparison.png`
- 小表格：
  - Accel magnitude r: 0.918, 0.855
  - Gyro magnitude r: 0.908, 0.864
  - Max cross-correlation up to 0.981
  - Lag: 1.2-1.3 s

### 页面文字

- Two usable paired recordings from the pilot outing
- Field signals resampled to 10 Hz
- Compared acceleration motion magnitude and gyroscope magnitude
- Max cross-correlations: 0.915-0.981

### 台上说的话

For the field-worn Shimmer comparison, I used the two usable paired recordings from the pilot outing.

In these recordings, the XIAO samples were timestamped by the Android receiver, while the Shimmer used its own logger clock. Therefore, epoch timestamps define the overlap, but they do not guarantee perfect clock synchronisation.

To make the comparison less sensitive to small orientation differences, I compared acceleration motion magnitude and gyroscope magnitude after resampling to 10 Hz.

The field results show similar long-term trends. After lag correction, maximum cross-correlations reached between 0.915 and 0.981. The best lag was around 1.2 to 1.3 seconds. Because the co-located lag was near zero, this field lag is most likely related to clock and timestamping-chain differences rather than a real delay in the inertial sensors.

---

## Slide 15. Detection Dataset

建议时间：1.2 min

### PPT 放什么

- 把 Table 4.4 做成简单柱状图：P1-P5 static windows vs pelvic-rotation windows
- 或直接放简化表格

### 页面文字

- 98 clean labelled segment files
- 66 static-sitting segments
- 32 pelvic-rotation segments
- P1-P4: training and internal checks
- P5: final held-out test

### 台上说的话

The classification dataset uses only XIAO data. The target is the presence or absence of pelvic motion, not anatomical pelvic-angle estimation.

After cleaning, the dataset contained 98 labelled segment files: 66 static-sitting segments and 32 pelvic-rotation segments. The window counts were highly imbalanced, because static sitting naturally lasts longer than instructed pelvic rotations.

Participants 1 to 4 were used for training and internal model checks. Participant 5 was held out for the final test. This means participant 5 was not used for feature selection, scaling, KNN k selection, or prototype-count selection.

Because of the imbalance, I report balanced accuracy and especially F1-score for pelvic rotation, rather than relying only on overall accuracy.

---

## Slide 16. Classifier Comparison

建议时间：1.5 min

### PPT 放什么

- 用柱状图显示 LR, SVM, DT, RF, KNN 的 F1：
  - LR 0.474
  - SVM 0.709
  - DT 0.781
  - RF 0.911
  - KNN 0.957
- 旁边放 `images/ch6_person5_confusion_matrix_selected_knn.png`

### 页面文字

- Selected model: KNN, k = 7
- F1 = 0.957 on held-out participant 5
- 155 / 165 pelvic-rotation windows detected
- 4 false positives among 3,497 static windows

### 台上说的话

I compared five classical machine-learning classifiers: logistic regression, SVM, decision tree, random forest, and KNN.

The selected k=7 KNN achieved an F1-score of 0.957 on the held-out participant. Out of 165 pelvic-rotation windows, it correctly detected 155 and missed 10. Out of 3,497 static-sitting windows, only 4 were misclassified as pelvic rotation.

This false-positive count is important for the reminder logic. If the system falsely detects pelvic rotation, it would reset the inactivity timer and may suppress a reminder even when the user did not actually move. So precision matters, not just recall.

The results show that the instructed static-sitting and pelvic-rotation classes are clearly separable in this pilot dataset. However, this does not yet prove robustness to all spontaneous daily seated movements.

---

## Slide 17. Embedded Deployment and Timing

建议时间：1.5 min

### PPT 放什么

- `images/ch6_full_vs_compact_knn_comparison.png`
- 小 timing 表：
  - KNN inference only: 2.70 ms
  - Features + KNN total: 2.73 ms
  - 2 s window period
  - 56.3 KB flash, 9.3 KB RAM

### 页面文字

- Compact KNN: 12 features, 128 prototypes
- F1 = 0.959 on same held-out participant
- Runtime: 2.73 ms per 2 s window
- Compute time below 0.15% of window period

### 台上说的话

After the offline comparison, I deployed the compact prototype-based KNN model on the XIAO nRF54L15 Sense.

The compact model uses 12 features and 128 KMeans prototypes. On the same held-out participant, it achieved F1 equal to 0.959, which is very close to the full KNN baseline.

For timing, I measured the deployed firmware using the hardware cycle counter. The total time for feature extraction plus KNN inference was 2.73 milliseconds per 2 second window. This is below 0.15 percent of the window period.

The deployed firmware used 56.3 KB of flash and 9.3 KB of RAM. Therefore, the result supports compute and memory feasibility on the target wearable. However, I did not measure power consumption, so timing feasibility does not yet mean confirmed battery-life feasibility.

---

## Slide 18. Conclusion, Limitations, and Future Work

建议时间：2 min

### PPT 放什么

左侧：Main findings  
右侧：Limitations / Future work

Main findings:

- Full technical chain demonstrated.
- XIAO captures movement trends consistent with Shimmer for detection.
- KNN detects instructed pelvic rotation with F1 = 0.957.
- Compact KNN runs on-device in 2.73 ms per 2 s window.

Limitations:

- Small sample size, single held-out test participant.
- Instructed movement, not spontaneous daily behaviour.
- Train-sitting classifier context only.
- Hardware reliability and battery life not fully validated.
- Haptic reminder not evaluated as behavioural intervention.

### 台上说的话

To conclude, this thesis demonstrates the full technical chain required for a local wearable reminder system. The prototype can sense motion near the pelvis, stream and label field data, compare trends with a Shimmer reference, classify static sitting versus pelvic rotation, compress the model for embedded deployment, run inference on the device, and trigger a local haptic cue.

For the research questions, the answer is cautiously positive. The low-cost IMU captured motion trends sufficiently consistent with Shimmer for this detection task. The platform supported field collection and annotation. The KNN classifier performed well on the held-out participant, and the compact version was efficient enough to run on the XIAO.

But the boundaries are important. This is a feasibility and preliminary validation study. The dataset is small, the movement is instructed, the classifier data come from train-sitting segments, hardware reliability needs improvement, battery life was not measured, and the haptic reminder was not tested for user acceptance or behavioural effectiveness.

Future work should collect more natural seated movement from more participants, improve mechanical attachment and power reliability, measure battery life, and then conduct a dedicated user study to test whether the haptic cue actually changes sitting behaviour.

Overall, the main value of this thesis is turning the idea of local pelvic-motion feedback into a measurable working prototype, with clear next steps for the next iteration.

---

# 25 分钟时间分配建议

| Part | Slides | Time |
|---|---:|---:|
| Opening and motivation | 1-4 | 3.5-4 min |
| System and implementation | 5-11 | 8-9 min |
| Evaluation and results | 12-17 | 10-11 min |
| Conclusion | 18 | 2 min |
| Buffer | - | 1 min |

---

# 答辩时需要避免的过度表述

不要说：

- The system improves posture.
- The system reduces sedentary behaviour.
- The system is clinically validated.
- The system works in daily free-living use.
- The haptic reminder is behaviourally effective.

建议说：

- The system detects instructed pelvic rotation in a labelled pilot dataset.
- The Shimmer results support trend-level use for this detection task.
- The result demonstrates technical feasibility.
- Behavioural effectiveness and daily-use robustness require future studies.
