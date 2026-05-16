# Master Thesis Defense Speaker Notes

## Slide 1. Title

Good morning/afternoon. My name is Ruyang Luo. Today I will present my master thesis, titled "AI-Enabled Wearable Device for Pelvic Motion Monitoring and Haptic Intervention During Prolonged Sitting".

The work focuses on a low-cost wearable prototype placed near the sacrum or lower-back region. The goal was not to prove a clinical or behavioural intervention, but to evaluate whether a complete technical sensing-to-cue pipeline can be built and tested.

## Slide 2. Motivation

Prolonged sitting is common in work, study, and daily transport. Many studies describe it by total sitting duration, bout duration, or the number of breaks.

However, two seated bouts can have the same duration but very different movement patterns. One may remain almost static, while another may include meaningful postural variation. This thesis focuses on that under-described part: whether pelvic-region movement occurs within a seated bout.

## Slide 3. Existing Monitoring Technologies

Existing technologies already monitor sitting and posture, but they usually target different outcomes. Camera systems can produce rich posture labels, smart chairs give a stable seating reference, and research-grade IMUs provide high-quality signals.

The gap for this thesis is more specific: low-cost pelvic-region sensing that can run locally and potentially trigger immediate feedback, while keeping the burden on the user low.

## Slide 4. Research Gap

The research gap is not that no one can detect sitting. The narrower gap is that current systems often do not combine low-cost pelvic-region sensing, local processing, and a feedback output in one wearable pipeline.

Research-grade systems are valuable for validation and analysis, but they are more expensive and often used for post-hoc processing. Prompt systems can interrupt sitting, but a reminder alone does not verify whether pelvic movement happened. This thesis therefore asks whether a low-cost technical pipeline can be built and evaluated.

## Slide 5. Research Question and Objectives

The main research question is whether a low-cost sacrum or lower-back IMU wearable can technically support seated pelvic-region movement monitoring and local haptic feedback.

I divided this into three objectives. First, build the prototype and pipeline. Second, compare the XIAO IMU signals with a Shimmer reference. Third, evaluate the field logging workflow, offline classification, compact embedded deployment, and haptic cue delivery.

## Slide 6. System Overview

The implemented system has five connected parts. The wearable node measures acceleration and angular velocity. The data can be streamed over BLE, logged and labelled on Android, inspected on a PC, and finally reduced into compact embedded detection logic.

The haptic output closes the loop locally. In this thesis, the loop was demonstrated as a technical function: sensing, decision logic, and vibration cue delivery.

## Slide 7. Prototype Hardware

This slide shows the implemented prototype. The main components are the XIAO nRF54L15 Sense IMU node, a DRV2605L haptic driver, and a coin vibration motor.

The prototype was designed for placement near the sacrum or lower-back region. At this stage, the evaluation focused on technical operation and signal handling, not on final enclosure comfort or long-term wearability.

## Slide 8. Logging and Inspection Tools

The system also includes software tools. The Android app supports device discovery, live telemetry, and manual labels during seated recordings. The PC receiver is used for signal inspection and quality checks.

This matters because the thesis is not only about a sensor board. It is about the complete data collection and inspection workflow that makes later evaluation possible.

## Slide 9. Objective 2 Method

For Objective 2, the XIAO and Shimmer IMUs were recorded in a co-located configuration. The purpose was to check whether the XIAO signals follow the same main movement trends as a research-grade reference IMU.

The important boundary is that this is trend-level signal comparability. It is not a validation of anatomical pelvic angle.

## Slide 10. Objective 3 Field Protocol

Objective 3 used a small labelled field pilot. Participants performed static sitting and instructed anterior-posterior pelvic rotation. The field recordings were designed to test whether the wearable and logging process could work outside a clean laboratory setting.

The field-worn Shimmer pairing was more difficult, and only part of those paired data were usable. That limitation is reflected later in the evidence boundary.

## Slide 11. Windowing and Classification Pipeline

The raw IMU streams were cleaned into labelled segments, then divided into two-second windows. Features were extracted from each window for offline KNN evaluation.

After evaluating the full model, a compact KNN version was created using fewer features and prototype reduction. This step is important because an embedded device cannot simply store a large full KNN reference set.

## Slide 12. Result 1

The first result is that the full prototype pipeline was implemented. It includes BLE streaming, labelled mobile logging, PC-based signal inspection, offline classification, compact embedded detection, and haptic cue delivery.

This result answers the basic feasibility question: the components can be connected into a working sensing-to-cue pipeline.

## Slide 13. Result 2

In the co-located comparison, XIAO and Shimmer showed strong trend-level agreement. The acceleration-axis correlations ranged from 0.856 to 0.923, and the gyroscope-axis correlations ranged from 0.816 to 0.864.

The estimated lag was approximately between minus 0.020 seconds and zero seconds. This supports the use of the XIAO signal for trend-level movement monitoring in this technical context.

## Slide 14. Result 3

For the field-worn paired recordings, the usable data came from P1 and P2. The acceleration motion magnitude correlations were 0.918 and 0.855, and the gyroscope magnitude correlations were 0.908 and 0.864.

This supports trend-level field agreement, but the usable paired dataset is small, so this should not be over-interpreted.

## Slide 15. Result 4

The clean labelled dataset contained 98 segments and 13,053 windows. Most windows were static sitting: 12,489 static windows compared with 564 pelvic-rotation windows.

Because the classes are imbalanced, accuracy alone is not enough. The held-out P5 test contained 3,497 static windows and 165 pelvic-rotation windows, so recall and false negatives are important.

## Slide 16. Result 5

On held-out participant P5, the selected full KNN achieved an F1 score of 0.957 for pelvic-rotation detection. Accuracy was 0.996, balanced accuracy was 0.969, precision was 0.975, and recall was 0.939.

The result is strong for this instructed detection task. However, it does not yet prove spontaneous daily-use detection or clinical movement assessment.

## Slide 17. Result 6

The confusion matrix shows the window-level behaviour behind the metrics. Out of 165 pelvic-rotation windows, 155 were detected and 10 were missed. Out of 3,497 static windows, 3,493 were correctly classified and 4 were false positives.

This is why I report F1, recall, and the confusion matrix rather than relying only on accuracy.

## Slide 18. Result 7

The full KNN was not suitable for embedded deployment because it required too much memory. The compact version reduced the model to 12 features and 128 KMeans prototypes.

Importantly, the compact KNN achieved an F1 score of 0.959, which is comparable to the full model in this evaluation. This makes embedded real-time detection technically feasible.

## Slide 19. Result 8

Firmware timing measurements showed a mean online decision time of 2.73 milliseconds per two-second window. The compact firmware used 56.3 KB of flash and 9.3 KB of RAM.

The haptic cue was implemented as a 10-minute inactivity timer with a one-second local vibration cue. This demonstrates cue delivery, but it does not yet test whether users perceive it as comfortable or whether it changes behaviour.

## Slide 20. Evidence Boundary

This slide is important for the defence. The evidence supports technical feasibility: the pipeline can sense, log, classify, run compactly on embedded hardware, and deliver a haptic cue.

But the evidence does not establish clinical pelvic kinematics, anatomical pelvic-angle validation, spontaneous daily-use robustness, long-term comfort, battery lifetime, or behavioural effectiveness. I keep this boundary explicit throughout the thesis.

## Slide 21. Limitations and Future Work

The limitations follow directly from the feasibility boundary. The participant sample is small, the rotations were instructed, and the seated contexts were limited. The paired Shimmer field data were also limited by synchronization and placement differences.

Future work should therefore collect larger and more diverse datasets, test spontaneous seated movement, improve synchronization, evaluate comfort and battery life, and study whether haptic feedback is detectable, acceptable, and behaviourally useful.

## Slide 22. Conclusion

To conclude, this thesis developed and technically evaluated a low-cost closed-loop wearable pipeline for pelvic-region movement monitoring during prolonged sitting.

The XIAO IMU showed trend-level agreement with Shimmer, the compact embedded KNN made real-time local detection feasible, and the firmware demonstrated local haptic cue delivery. The contribution is therefore a feasible technical pipeline and a clear evidence boundary for future validation.

## Slide 23. Backup Slides

Backup section divider.

## Slide 24. Backup A: Key Terms

Use this backup slide only if the committee asks for this detail.

## Slide 25. Backup B: Hardware Cost and Components

Use this backup slide only if the committee asks for this detail.

## Slide 26. Backup C: Classifier Reproducibility

Use this backup slide only if the committee asks for this detail.

## Slide 27. Backup D: Shimmer/XIAO Interpretation

Use this backup slide only if the committee asks for this detail.

## Slide 28. Backup E: Field Protocol Detail

Use this backup slide only if the committee asks for this detail.

## Slide 29. Backup F: Ethics and Privacy

Use this backup slide only if the committee asks for this detail.

