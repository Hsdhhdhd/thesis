# 25 分钟答辩 PPT 详尽大纲

依据版本：`D:\最终论文\5.12论文重写`

建议总页数：**21 页主讲 slides + 6 页 backup slides**

答辩核心定位：

> This thesis is a technical feasibility study of a low-cost closed-loop sacrum/lower-back wearable sensing-to-cue pipeline for pelvic-region movement monitoring during prolonged sitting.

最重要的表达边界：

- 可以说：technical feasibility, sensing-to-cue pipeline, trend-level signal comparability, instructed pelvic-rotation detection, compact embedded deployment, local haptic cue demonstration.
- 不要说：clinical validation, anatomical pelvic-angle validation, proven daily-use robustness, proven behavioural change, health benefit, commercial-ready wearable.

图片素材位置：

`D:\最终论文\5.12论文重写\images`

可直接使用的图片：

- `c3_device_external.png`
- `c3_device_internal.png`
- `c4_mobile_discovery.jpg`
- `c4_mobile_label_controls.jpg`
- `c4_mobile_live_telemetry_clean.jpg`
- `c4_pc_receiver_gui.png`
- `field_equipment_overview.jpg`
- `field_wearing_setup.jpg`
- `field_train_environment_anon.jpg`
- `shimmer_xiao_comparison.png`
- `c5_field_trend_comparison.png`
- `ch6_person5_confusion_matrix_selected_knn.png`
- `ch6_full_vs_compact_knn_comparison.png`

需要从论文 PDF 截图或在 PPT 中重画的图：

- System architecture: 论文 Figure 2.1
- Co-located Shimmer/XIAO setup: 论文 Figure 2.2
- 若需要简化流程图，建议在 PPT 中重画，不直接截全文图。

---

## 总体时间分配

| 部分 | Slides | 时间 |
|---|---:|---:|
| Opening and motivation | 1-4 | 4 min |
| Research question and objectives | 5 | 2 min |
| System and methods | 6-12 | 7 min |
| Results | 13-18 | 8 min |
| Discussion, limitations, conclusion | 19-21 | 4 min |

总时间约 25 min。

---

# 主讲 Slides

## Slide 1. Title

建议时间：0:30

页面目的：

- 开场，明确论文题目和主题。
- 让听众第一眼知道这是 wearable + pelvic motion + haptic feedback。

画面设计：

- 背景保持白色或 KU Leuven 模板风格。
- 左侧放题目，右侧放 prototype 外观图。
- 图片：`D:\最终论文\5.12论文重写\images\c3_device_external.png`
- 不要放太多文字。

页面文字：

```text
AI-Enabled Wearable Device for Pelvic Motion Monitoring
and Haptic Intervention During Prolonged Sitting

Ruyang Luo
Yonggui Yuan

Supervisor: Prof. Bart Vanrumste
Co-supervisors: Prof. Jean-Marie Aerts, Meixing Liao
```

上台语言：

> Good morning/afternoon. My name is Ruyang Luo. Today I will present my master thesis, titled "AI-Enabled Wearable Device for Pelvic Motion Monitoring and Haptic Intervention During Prolonged Sitting".  
> The work focuses on a low-cost wearable prototype placed near the sacrum or lower-back region. The goal was not to prove a clinical or behavioural intervention, but to evaluate whether a complete technical sensing-to-cue pipeline can be built and tested.

转场：

> I will start from the problem: why prolonged sitting is not fully described by total sitting time alone.

---

## Slide 2. Motivation: Prolonged Sitting Is Not Only Duration

建议时间：1:15

页面目的：

- 解释为什么论文关注 prolonged sitting。
- 从 total sitting time 引出 seated-bout movement variability。

画面设计：

- 左侧：简化示意图，两条时间线。
  - Timeline A: long static sitting bout
  - Timeline B: same sitting duration but with pelvic/lower-trunk movement
- 右侧：3 个 bullet。
- 这页建议自己在 PPT 中画，不需要论文图片。

页面文字：

```text
Same total sitting duration can hide different movement patterns

Key idea:
- Total sitting time describes exposure
- Bout duration and interruptions describe sitting pattern
- Movement within a seated bout is still under-described
```

上台语言：

> Prolonged sitting is common in work, study, and daily transport. Many studies describe it by total sitting duration, bout duration, or the number of breaks.  
> However, two seated bouts can have the same duration but very different movement patterns. One may remain almost static, while another may include meaningful postural variation.  
> This thesis focuses on that under-described part: whether pelvic-region movement occurs within a seated bout.

转场：

> Existing technologies already monitor sitting and posture, but they usually target different outcomes.

---

## Slide 3. Existing Monitoring Technologies

建议时间：1:15

页面目的：

- 用一页概括 related work，不展开讲文献细节。
- 说明你不是重复做 sitting detection，而是切到 pelvis-focused movement monitoring。

画面设计：

- 做 4 列卡片或横向表：
  1. Camera-based pose systems
  2. Smart chairs / pressure cushions
  3. Research-grade wearable IMUs
  4. Microcontroller-based wearable prototype
- 最后一列用浅蓝色突出 “This direction”。
- 不建议直接截图 Table 1.1，太密。

页面文字：

```text
Existing directions

Camera systems:
pose classes, line-of-sight required

Smart chairs/cushions:
seat-based pressure/contact patterns

Research-grade IMUs:
high-quality motion recording, often offline

Microcontroller-based wearable:
local sensing + local cue delivery
```

上台语言：

> Existing technologies cover several directions. Camera-based systems can estimate posture, but they need line of sight and a prepared environment. Smart chairs and pressure cushions can infer sitting or posture from pressure patterns, but measurement is tied to a seat.  
> Research-grade IMUs provide high-quality recordings, but they are usually used for analysis or validation rather than a small local reminder system.  
> My work sits in the last direction: a low-cost microcontroller-based wearable that combines local sensing, embedded decision logic, and local haptic output.

转场：

> Based on this, the research gap is not simply "can we detect sitting", but whether a pelvis-focused wearable can close the loop from sensing to cue.

---

## Slide 4. Research Gap

建议时间：1:00

页面目的：

- 明确 gap。
- 为 RQ 做铺垫。

画面设计：

- 中间放标题：`Gap: pelvis-focused sensing-to-cue feasibility`
- 下方 4 个编号 bullet。

页面文字：

```text
Research gaps

1. Sitting duration does not describe movement within a seated bout
2. Pelvic/lower-trunk movement is less directly monitored in daily seated contexts
3. Many systems rely on offline or external processing
4. Feedback is often not directly triggered by pelvic-movement detection outcomes
```

上台语言：

> The reviewed work leaves four main gaps.  
> First, sitting duration alone does not describe whether the person remains static during the seated bout.  
> Second, pelvic or lower-trunk movement is not always directly monitored, especially in practical seated contexts.  
> Third, many systems still depend on offline or external processing.  
> Fourth, feedback may exist, but it is often not directly triggered by a local pelvic-movement detection outcome.

转场：

> These gaps lead to the main research question of this thesis.

---

## Slide 5. Research Question and Objectives

建议时间：2:00

页面目的：

- 正式展示 RQ 和 3 个 objectives。
- 后面 Methods/Results 都按这三个 objectives 对齐。

画面设计：

- 上半部分放 RQ，做成框。
- 下半部分放 3 个 objectives，每个 objective 一行。

页面文字：

```text
Research Question

To what extent is it technically feasible to develop and implement
a closed-loop, sacrum-mounted wearable system that monitors pelvic rotation
and provides real-time haptic feedback based on detection outcomes
to interrupt prolonged sitting in everyday seated contexts?

Objectives
1. Prototype development
2. Signal comparability with a Shimmer IMU
3. Pelvic-rotation detection and on-device feedback feasibility
```

上台语言：

> The main research question asks to what extent it is technically feasible to develop and implement a closed-loop sacrum-mounted wearable system.  
> The system should monitor pelvic rotation and provide real-time haptic feedback based on detection outcomes.  
> I addressed this through three objectives. Objective 1 was prototype development. Objective 2 was signal comparability against a research-grade Shimmer IMU. Objective 3 was to test pelvic-rotation detection and whether a compact model and haptic feedback logic can run on the wearable.

转场：

> I will now explain the system built for Objective 1.

---

## Slide 6. System Overview: Sensing-to-Cue Pipeline

建议时间：1:30

页面目的：

- 给出全系统大图。
- 让听众知道论文不是单一模型，而是完整 pipeline。

画面设计：

- 放 system architecture。
- 来源：论文 Figure 2.1，从 `thesis.pdf` 截图；或在 PPT 中重画简化版。
- 建议重画成横向流程：

```text
XIAO IMU wearable
→ BLE stream
→ Android labelled logging / PC inspection
→ offline feature extraction and model construction
→ compact KNN exported to firmware
→ inactivity timer
→ DRV2605L + coin vibration motor
```

页面文字：

```text
Closed-loop pipeline

IMU sensing → BLE logging → feature extraction → compact KNN
→ inactivity timer → local haptic cue
```

上台语言：

> This slide shows the full system pipeline.  
> The wearable collects six-axis IMU data and streams it through BLE. During field collection, the Android logger records labelled data, and the PC receiver supports signal inspection.  
> The labelled data are then used for offline feature extraction and model construction. A compact KNN model is exported to firmware. On the device, the movement decision updates an inactivity timer, and the timer triggers a local vibration cue through the haptic driver and coin motor.

转场：

> The physical prototype used for this pipeline is shown on the next slide.

---

## Slide 7. Prototype Hardware

建议时间：1:00

页面目的：

- 展示真实做出来的硬件。
- 建立可信度：不是只做了代码或模型。

画面设计：

- 左图：`c3_device_external.png`
- 右图：`c3_device_internal.png`
- 图下标注：
  - External view
  - Internal battery layout
- 右下角放 5 个短 bullet。

页面文字：

```text
Prototype components

- XIAO nRF54L15 Sense IMU node
- BLE streaming
- DRV2605L haptic driver
- Coin vibration motor
- 500 mAh battery and 3D-printed enclosure
```

上台语言：

> This is the implemented prototype.  
> It uses the XIAO nRF54L15 Sense as the microcontroller and IMU node. It streams IMU data by BLE and includes a DRV2605L haptic driver and a coin vibration motor for local tactile feedback.  
> The orange enclosure contains the battery and provides the attachment surface. This prototype was used both for data collection and for the firmware-level feedback demonstration.

转场：

> To collect labelled field data, I also developed Android and PC-side tools.

---

## Slide 8. Logging and Inspection Tools

建议时间：1:00

页面目的：

- 解释为什么需要 Android/PC 工具。
- 展示数据采集是可控的、有标签的。

画面设计：

- 上排三张手机图：
  - `c4_mobile_discovery.jpg`
  - `c4_mobile_label_controls.jpg`
  - `c4_mobile_live_telemetry_clean.jpg`
- 下方放 PC 图：
  - `c4_pc_receiver_gui.png`
- 如果一页太满，手机三图放一页，PC 图缩小放右下。

页面文字：

```text
Data collection tools

- BLE device discovery
- Per-device label control
- Live telemetry check
- PC receiver for stream inspection and export
```

上台语言：

> The Android app was used for field logging. It supports BLE device discovery, per-device label control, and live telemetry checking.  
> The PC receiver provided a researcher-side tool for inspecting the stream, plotting signals, and exporting data.  
> These tools were important because the classifier dataset depends on clean labelled segments, not just raw sensor recordings.

转场：

> After the prototype was built, Objective 2 checked whether its IMU signals were broadly comparable with a Shimmer reference.

---

## Slide 9. Objective 2 Method: Shimmer/XIAO Comparison

建议时间：1:15

页面目的：

- 解释 reference comparison 的设计。
- 强调 validity boundary：trend-level only。

画面设计：

- 左侧放论文 Figure 2.2：Co-located Shimmer/XIAO setup，从 PDF 截图或在 PPT 中重画。
- 右侧放简化 field-worn paired setup：
  - 可用文字框表示：P1 and P2 usable paired recordings only。
- 下方红色或灰色提示框：
  - `Trend-level comparability, not anatomical pelvic-angle validation`

页面文字：

```text
Two comparison conditions

1. Co-located setup
   XIAO fixed on top of Shimmer

2. Field-worn paired subset
   usable paired recordings: P1 and P2

Interpretation:
trend-level signal comparability only
```

上台语言：

> Objective 2 compared the low-cost XIAO-based prototype with a research-grade Shimmer IMU.  
> There were two conditions. First, in the co-located setup, the XIAO prototype was fixed on top of the Shimmer so that both sensors received the same imposed movement.  
> Second, I analysed the usable field-worn paired recordings. Although paired recordings were planned for five participants, only P1 and P2 produced usable overlapping Shimmer and XIAO data.  
> Importantly, this comparison was treated as trend-level signal comparability, not strict synchronization, absolute calibration, or anatomical pelvic-angle validation.

转场：

> Objective 3 then used labelled XIAO field data to evaluate pelvic-rotation detection.

---

## Slide 10. Objective 3 Field Protocol

建议时间：1:15

页面目的：

- 交代 field study 如何收集。
- 说明为什么用 train-seated data。

画面设计：

- 三张图横排：
  - `field_equipment_overview.jpg`
  - `field_wearing_setup.jpg`
  - `field_train_environment_anon.jpg`
- 图下分别写：
  - Equipment before route
  - Sacrum/lower-back attachment
  - Train-seated recording context

页面文字：

```text
Pilot field protocol

- 5 participants
- XIAO worn near sacrum/lower-back region
- Labelled train-seated recordings
- Classes: static sitting vs instructed anterior-posterior pelvic rotation
- Bus data kept supplementary due to vibration and reliability issues
```

上台语言：

> For Objective 3, five participants were recorded in a pilot field study.  
> The XIAO-based prototype was attached near the sacrum or lower-back region, close to the pelvis.  
> The main classifier dataset was restricted to clean labelled train-seated recordings, because these recordings provided usable labelled segments for all five participants.  
> The two classes were static sitting and instructed anterior-posterior pelvic rotation. Bus data were organised separately as supplementary material because vehicle vibration and recording reliability made them less suitable as the main classifier evidence.

转场：

> The retained data were then converted into window-level features for classifier evaluation.

---

## Slide 11. Windowing and Classification Pipeline

建议时间：1:15

页面目的：

- 展示从 labelled segment 到 model 的流程。
- 清楚说明 held-out P5 test。

画面设计：

- 用流程图：

```text
Labelled XIAO segments
→ 2 s windows, 1 s step
→ feature extraction
→ P1-P4 training/internal checks
→ held-out P5 final test
→ compact KNN firmware deployment
```

- 右侧小表：

```text
Models: LR, SVM, DT, RF, KNN
Positive class: pelvic_rotation
Selected KNN: k = 7
```

页面文字：

```text
Detection task

Binary window-level classification:
static_sitting vs pelvic_rotation

Final test:
P5 held out from scaling, selection, fitting, and evaluation setup
```

上台语言：

> The detection task was defined as a binary window-level classification problem: static sitting versus pelvic rotation.  
> The labelled XIAO segments were split into 2-second windows, and time-domain features were extracted.  
> Participants P1 to P4 were used for training and internal checks. Participant P5 was held out for final testing. No P5 data were used for feature scaling, feature selection, KNN setting, or model fitting.  
> Five baseline classifiers were compared: logistic regression, SVM, decision tree, random forest, and KNN. The selected KNN used k equals 7.

转场：

> I will now move to the results, starting with the implemented prototype.

---

## Slide 12. Result 1: Prototype Implementation Outcome

建议时间：1:00

页面目的：

- 回答 Objective 1。
- 强调完整 pipeline 已实现。

画面设计：

- 左侧放 prototype 外观图：`c3_device_external.png`
- 右侧放 sensing-to-cue checklist，每一项打勾。

页面文字：

```text
Objective 1 outcome

Implemented:
✓ IMU sensing
✓ BLE streaming
✓ Android labelled logging
✓ PC inspection
✓ compact embedded detection
✓ 10 min inactivity timer
✓ 1 s local vibration cue
```

上台语言：

> Objective 1 was achieved by implementing the complete sensing-to-cue pipeline.  
> The prototype supported IMU sensing, BLE streaming, Android labelled logging, PC signal inspection, compact embedded detection, an inactivity timer, and local vibration feedback.  
> This result means the system integration requirement was met. The device was not only a sensor logger, but a closed-loop research prototype.

转场：

> The next question was whether the low-cost IMU signal was comparable with a research-grade reference at trend level.

---

## Slide 13. Result 2: Co-Located Shimmer/XIAO Agreement

建议时间：1:30

页面目的：

- 展示 co-located comparison 的核心结果。
- 用图 + 关键数字说服听众。

画面设计：

- 放 `shimmer_xiao_comparison.png`
- 右侧放 key numbers：

```text
Acceleration axes:
r = 0.856-0.923

Gyroscope axes:
r = 0.816-0.864

Lag:
-0.020 to 0 s
```

页面文字：

```text
Co-located trend agreement

Shared movement input produced similar main peaks
```

上台语言：

> In the co-located recording, the XIAO and Shimmer signals showed the same main movement peaks across acceleration and gyroscope channels.  
> The acceleration-axis correlations ranged from 0.856 to 0.923, and the gyroscope-axis correlations ranged from 0.816 to 0.864.  
> The estimated lag was between minus 0.020 and 0 seconds.  
> This supports trend-level agreement when the two sensors receive the same imposed movement input.

转场：

> The field-worn case is more challenging because the sensors are worn and the recordings are much longer.

---

## Slide 14. Result 3: Field-Worn Trend Agreement

建议时间：1:30

页面目的：

- 展示 field-worn comparison。
- 主动说明只保留 2 个 paired recordings。

画面设计：

- 放 `c5_field_trend_comparison.png`
- 右侧放 key values：

```text
Usable paired recordings:
P1 and P2

Acceleration motion magnitude:
r = 0.918, 0.855

Gyroscope magnitude:
r = 0.908, 0.864

Max cross-correlation:
0.915-0.981
```

页面文字：

```text
Field-worn trend agreement

Descriptive metrics only
No inferential statistical comparison
```

上台语言：

> In the field-worn comparison, only two participants produced usable paired Shimmer and XIAO recordings.  
> For these recordings, acceleration motion magnitude correlations were 0.918 and 0.855. Gyroscope magnitude correlations were 0.908 and 0.864.  
> After lag correction, maximum cross-correlations reached between 0.915 and 0.981.  
> Because the paired dataset was small, I did not perform inferential statistics. These values support descriptive trend-level comparability only.

转场：

> With this signal-comparability evidence, I then evaluated whether the XIAO data could distinguish static sitting from instructed pelvic rotation.

---

## Slide 15. Result 4: Classifier Dataset

建议时间：1:00

页面目的：

- 先交代数据规模和不平衡，再讲模型结果。
- 避免老师问“数据多少、正负样本多少”。

画面设计：

- 做简洁表格：

```text
Total windows: 13,053
Static sitting: 12,489
Pelvic rotation: 564

Held-out P5:
Static sitting: 3,497
Pelvic rotation: 165
Class ratio: about 21:1
```

- 可以用小条形图显示 imbalance。

页面文字：

```text
Retained labelled dataset

98 clean labelled segment files
2 s windows
Positive class: pelvic_rotation
Strong class imbalance
```

上台语言：

> The retained classifier dataset contained 98 clean labelled segment files.  
> After 2-second windowing, the dataset contained 13,053 windows in total: 12,489 static-sitting windows and 564 pelvic-rotation windows.  
> The held-out P5 test set was strongly imbalanced, with 3,497 static-sitting windows and 165 pelvic-rotation windows.  
> Therefore, I report precision, recall, F1-score, and balanced accuracy, not only overall accuracy.

转场：

> The held-out P5 performance is shown on the next slide.

---

## Slide 16. Result 5: Held-Out P5 Detection Performance

建议时间：1:45

页面目的：

- 展示五个模型结果。
- 强调 KNN 最终选择和 F1。

画面设计：

- 左侧放简化结果表：

```text
Model | Accuracy | Bal. acc. | Precision | Recall | F1
LR    | 0.909 | 0.912 | 0.320 | 0.915 | 0.474
SVM   | 0.964 | 0.970 | 0.557 | 0.976 | 0.709
DT    | 0.978 | 0.925 | 0.711 | 0.867 | 0.781
RF    | 0.993 | 0.921 | 0.993 | 0.842 | 0.911
KNN   | 0.996 | 0.969 | 0.975 | 0.939 | 0.957
```

- 右侧高亮：
  - Selected KNN
  - F1 = 0.957

页面文字：

```text
Best held-out pelvic-rotation F1:
KNN, F1 = 0.957
```

上台语言：

> On the held-out P5 participant, the KNN model achieved the highest pelvic-rotation F1-score.  
> Its accuracy was 0.996, balanced accuracy was 0.969, precision was 0.975, recall was 0.939, and F1-score was 0.957.  
> Random forest had very high precision but lower recall. Logistic regression and SVM detected more pelvic-rotation windows but produced many more false positives.  
> Based on this trade-off, KNN was selected for the compact embedded implementation.

转场：

> The confusion matrix gives a more concrete view of these errors.

---

## Slide 17. Result 6: Confusion Matrix

建议时间：1:15

页面目的：

- 让结果更直观。
- 说明误报和漏检数量。

画面设计：

- 放 `ch6_person5_confusion_matrix_selected_knn.png`
- 右侧写：

```text
Pelvic rotation:
155 / 165 correctly detected
10 missed

Static sitting:
3493 / 3497 correctly detected
4 false positives
```

页面文字：

```text
Selected k = 7 KNN on held-out P5
```

上台语言：

> For the selected k equals 7 KNN, 155 of 165 pelvic-rotation windows were correctly detected, and 10 were missed.  
> For static sitting, 3,493 of 3,497 windows were correctly classified, with only 4 false positives.  
> This shows that instructed pelvic rotation was technically detectable in the retained pilot field dataset.  
> However, this is still a window-level result on instructed movement, not proof of robust spontaneous daily-life movement recognition.

转场：

> The next step was to make this detection logic fit into the wearable firmware.

---

## Slide 18. Result 7: Compact Embedded KNN

建议时间：2:00

页面目的：

- 解释为什么 compact model necessary。
- 展示 full vs compact。

画面设计：

- 放 `ch6_full_vs_compact_knn_comparison.png`
- 右侧放对比：

```text
Full KNN:
90 features
9,391 reference windows
FLASH overflow: 235.50% of region

Compact KNN:
12 features
128 KMeans prototypes
F1 = 0.959 on held-out P5
```

页面文字：

```text
Compact model preserved decision behaviour
while reducing reference storage
```

上台语言：

> A direct full-KNN firmware implementation was not feasible because KNN stores reference examples.  
> The full offline KNN used 90 features and 9,391 reference windows. Storing only the reference matrix would already exceed the target flash budget. In the isolated full-KNN build, the linker reported 235.50 percent of the Zephyr flash region and failed.  
> The compact model reduced the feature set to 12 features and compressed the reference set to 128 KMeans prototypes.  
> On the same held-out participant, it achieved an F1-score of 0.959. I interpret this not as proving that the compact model is generally better, but as showing that the relevant decision behaviour was preserved while storage was greatly reduced.

转场：

> Finally, I measured whether this compact decision path could run fast enough on the wearable.

---

## Slide 19. Result 8: Firmware Timing, Memory, and Haptic Cue

建议时间：1:30

页面目的：

- 展示 embedded feasibility 的硬指标。
- 连接到 haptic cue。

画面设计：

- 大数字风格：

```text
2.73 ms
mean online decision time per 2 s window

56.3 KB FLASH
9.3 KB RAM

10 min inactivity timer
1 s local vibration cue
```

- 可以右下角放小 prototype 图。

页面文字：

```text
Embedded feasibility

The online decision path used less than 0.15% of the 2,000 ms window period
```

上台语言：

> The compact firmware was then evaluated on the XIAO nRF54L15 Sense.  
> The mean KNN inference-only time was 2.70 ms, and the full online decision path, including feature extraction and KNN computation, was 2.73 ms per 2-second window.  
> This is less than 0.15 percent of the 2,000 ms window period. The firmware used 56.3 KB flash and 9.3 KB RAM.  
> The firmware also executed the 10-minute inactivity timer and the 1-second local vibration cue. This supports compute and memory feasibility of the compact sensing-to-cue path.

转场：

> These results answer the research question, but only within a clear evidence boundary.

---

## Slide 20. Discussion: What This Proves and What It Does Not Prove

建议时间：1:45

页面目的：

- 主动界定结果，显得严谨。
- 防止老师追问临床/行为效果。

画面设计：

- 两列：
  - Supported by this thesis
  - Not established by this thesis

页面文字：

```text
Supported
- Integrated low-cost sensing-to-cue prototype
- Trend-level comparability with Shimmer
- Instructed pelvic-rotation detection in pilot data
- Compact embedded KNN timing and memory feasibility
- Local haptic cue execution

Not established
- Clinical pelvic kinematics
- Anatomical pelvic-angle validity
- Spontaneous daily-use robustness
- Long-term comfort or battery life
- Behavioural or health effectiveness
```

上台语言：

> Overall, the results support a cautious technical-feasibility answer.  
> The thesis supports that a low-cost sacrum or lower-back wearable can be integrated as a sensing-to-cue prototype. It can produce trend-level comparable IMU signals, detect instructed pelvic rotation in pilot data, run a compact KNN on the target wearable, and trigger a local haptic cue.  
> But the thesis does not establish clinical pelvic kinematics, anatomical pelvic-angle validity, robust spontaneous daily-use performance, long-term comfort, battery lifetime, or behavioural effectiveness. Those require separate studies.

转场：

> The limitations and future work follow directly from this boundary.

---

## Slide 21. Limitations and Future Work

建议时间：1:45

页面目的：

- 用简化版 limitation 表收束。
- 不要把论文完整 Table 4.2 贴上去，太密。

画面设计：

- 5 行简化表：

```text
Theme | Limitation | Future work

Dataset | small sample, instructed movement | larger spontaneous daily-life dataset
Validation | P5 held-out only, no external dataset | stricter LOSO + external validation
Reference | only 2 usable paired Shimmer field recordings | more paired sessions + better synchronization
Hardware | comfort, attachment, battery life not fully tested | long-duration wearing and battery tests
Feedback | perception and behaviour impact not tested | user study and intervention evaluation
```

页面文字：

```text
Main future direction:
from technical feasibility to robust daily-use and behavioural evaluation
```

上台语言：

> The main limitations are the small sample size, the instructed nature of the pelvic movement, the limited paired Shimmer field recordings, and the lack of long-term hardware and behavioural evaluation.  
> Future work should collect larger spontaneous seated-behaviour datasets across office, home, study, and commuting contexts. It should use stronger participant-level and external validation, improve hardware synchronization for reference comparison, and evaluate long-duration wearing, battery life, and user acceptance.  
> Finally, a separate behavioural study is needed to test whether the haptic cue actually changes sitting behaviour.

转场：

> I will close with the final conclusion.

---

## Slide 22. Conclusion

建议时间：1:00

页面目的：

- 用非常清楚的一句话回答 RQ。
- 结束前给老师留下“我知道自己做到了什么，也知道没做到什么”的印象。

画面设计：

- 中间大句：

```text
Technical feasibility was demonstrated,
but clinical and behavioural effectiveness remain future work.
```

- 下方 3 个小点：

```text
1. Prototype implemented
2. Signals and detection technically evaluated
3. Compact embedded sensing-to-cue path demonstrated
```

上台语言：

> In conclusion, this thesis demonstrated the technical feasibility of a low-cost closed-loop sacrum or lower-back wearable system for pelvic-region movement monitoring during prolonged sitting.  
> The prototype integrated sensing, labelled logging, compact embedded detection, an inactivity timer, and local haptic cue delivery.  
> The results support the feasibility of the sensing-to-cue pipeline, but they do not yet prove clinical validity, daily-use robustness, long-term comfort, battery lifetime, or behavioural effectiveness.  
> Thank you for your attention. I am happy to answer your questions.

---

# Backup Slides

以下 backup slides 不一定主讲，但建议放在 PPT 最后，以便问答时调用。

---

## Backup 1. Full Research Question and Objectives

用途：

- 如果老师问 “你的 thesis scope 到底是什么？”

页面内容：

```text
RQ:
To what extent is it technically feasible to develop and implement
a closed-loop, sacrum-mounted wearable system...

Objectives:
1. Prototype development
2. Signal comparability
3. Detection and embedded feedback feasibility
```

回答语言：

> The key word is technically feasible. The thesis was designed as a system-level feasibility study, not as a clinical validation study or behavioural intervention trial.

---

## Backup 2. Data Inclusion and Exclusion Boundary

用途：

- 如果老师问 “为什么不用 bus data？” 或 “为什么只用 train-seated data？”

页面内容：

```text
Main classifier dataset:
- clean labelled train-seated XIAO segments
- all five participants available

Excluded from main classifier dataset:
- unlabelled or unclear rows
- non-dynamic seated contexts
- bus data with strong vibration or reliability problems
- missing BLE stream or battery/contact issues

Bus data:
supplementary only
```

回答语言：

> The main dataset was scoped to clean labelled train-seated recordings because it provided complete usable data for all five participants. Bus recordings were more strongly affected by vehicle vibration and reliability issues, so I treated them as supplementary rather than the main evidence.

---

## Backup 3. Why KNN?

用途：

- 如果老师问 “为什么不用 deep learning / 为什么选 KNN？”

页面内容：

```text
Reason for KNN:
- strong held-out F1 in pilot data
- transparent baseline
- simple inference logic
- compatible with prototype compression
- practical for feasibility-focused embedded deployment

Not claimed:
- KNN is globally optimal
- model novelty
```

回答语言：

> The goal was not to propose a novel machine-learning model. The goal was to evaluate whether a practical detector could be compressed and deployed on the wearable. KNN performed best in the held-out pilot result and was simple enough to analyse and compress using prototypes.

---

## Backup 4. Full vs Compact KNN Memory

用途：

- 如果老师问 “为什么需要 128 prototypes？”

页面内容：

```text
Full KNN:
9,391 windows × 90 features × 4 bytes
= 3,380,760 bytes before overhead

Build check:
3,443,596 bytes FLASH
235.50% of Zephyr region
overflow by 1,981,324 bytes

Compact KNN:
12 features × 128 prototypes
```

回答语言：

> The full KNN was not feasible because KNN stores the reference set. The compact model reduces both the feature dimension and the number of stored prototypes, making the implementation fit within flash and RAM constraints.

---

## Backup 5. Validity Boundary of Shimmer Comparison

用途：

- 如果老师问 “Shimmer comparison 是否证明你的设备准确？”

页面内容：

```text
Supported:
- trend-level waveform similarity
- comparable main movement peaks
- descriptive correlations

Not supported:
- anatomical pelvic angle
- clinical kinematics
- strict synchronization
- absolute calibration
```

回答语言：

> The Shimmer comparison supports trend-level signal comparability, not anatomical validity. The sensors were not synchronized with hardware triggers and there was no anatomical reference system. Therefore I do not claim pelvic-angle validation.

---

## Backup 6. Haptic Feedback Boundary

用途：

- 如果老师问 “这个震动真的能改变久坐行为吗？”

页面内容：

```text
Implemented:
- DRV2605L driver
- coin vibration motor
- 10 min inactivity timer
- 1 s local cue

Not evaluated:
- vibration perception
- comfort and acceptance
- adherence
- behavioural change
- health or discomfort outcomes
```

回答语言：

> This thesis demonstrates cue delivery technically. It does not evaluate whether users perceive the cue as comfortable or whether it changes sitting behaviour. That requires a separate user and behavioural intervention study.

---

# 关键答辩表达模板

## 1. 如果老师问“你的创新点是什么？”

建议回答：

> The contribution is not a novel IMU sensor or a novel machine-learning algorithm. The contribution is the integration and technical evaluation of a pelvis-focused sensing-to-cue pipeline: low-cost wearable sensing, labelled field logging, reference trend comparison, pilot pelvic-rotation detection, compact embedded deployment, and local haptic cue execution.

中文理解：

> 创新点不是发明了新传感器或新算法，而是把 pelvis-focused sensing 到 haptic cue 的完整链路做出来，并验证它在技术上可行。

## 2. 如果老师问“为什么不是 clinical validation？”

建议回答：

> Clinical validation would require anatomical reference measurements, controlled kinematic ground truth, and a clinical protocol. This thesis used IMU signal comparison and labelled pilot field data, so the correct interpretation is technical feasibility and trend-level comparability.

## 3. 如果老师问“为什么样本这么少还可以写？”

建议回答：

> The sample size limits generalisation, and I acknowledge that clearly. The purpose was a pilot feasibility study. The results show that the pipeline can be built, the data can be collected, the instructed movement class can be detected in the pilot data, and the compact model can run on the target wearable. Larger spontaneous datasets are future work.

## 4. 如果老师问“为什么只 held-out P5，不够严格？”

建议回答：

> It is a limitation. P5 held-out testing provides one participant-independent check, but it does not replace full leave-one-subject-out reporting or external validation. That is why I describe the result as pilot technical detectability rather than robust generalisation.

## 5. 如果老师问“能不能用于真实日常生活？”

建议回答：

> Not yet as a validated daily-use system. The current result supports technical feasibility in pilot seated contexts with instructed pelvic rotation. Daily-life use would require spontaneous seated movement data, long-term attachment and comfort testing, battery-life evaluation, and behavioural outcome evaluation.

---

# 制作 PPT 时的具体建议

1. 每页最多 3-5 个 bullet，不要把论文段落搬上去。
2. 图比文字重要，尤其是 prototype、field setup、Shimmer comparison、confusion matrix、compact KNN。
3. Results 部分不要过度解释每个 metric，只讲最关键的数字。
4. 每次讲高结果时立刻加 evidence boundary，例如：
   - "in pilot instructed data"
   - "trend-level only"
   - "not clinical validation"
5. 不要用 “AI” 讲太多。论文真正核心是 wearable pipeline + compact embedded detection，不是复杂 AI 模型。

---

# 25 分钟练习节奏

建议练习时这样分段计时：

```text
Slides 1-5: 5 min
Slides 6-11: 7 min
Slides 12-19: 9 min
Slides 20-22: 4 min
```

如果超时，优先压缩：

- Slide 3 related work
- Slide 8 logging tools
- Slide 15 dataset details

不要压缩：

- Slide 5 RQ/objectives
- Slide 16 detection results
- Slide 18 compact embedded KNN
- Slide 20 evidence boundary
- Slide 22 conclusion

