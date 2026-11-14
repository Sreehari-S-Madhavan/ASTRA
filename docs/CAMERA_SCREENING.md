# ASTRA: Camera-Based Health & Visual Screening Guide

## 1. Primary Priority Implementation Overview
The camera-based health screening suite is a central, operational component of ASTRA. It provides non-invasive, objective functional visual observations and neuro-vestibular assessment without requiring wearable biosensors.

## 2. Implemented Computer Vision Capabilities

### A. Real-Time Face Detection & Tracking
- Detects the primary astronaut face in the video frame using multi-scale Haar feature cascades or neural face models.
- Establishes a spatial bounding box with HUD brackets and extracts morphological anchor points (eyes, nose bridge, nose tip, mouth corners, chin).

### B. Eye Landmark Tracking & Blink Detection (EAR)
- Computes the geometric **Eye Aspect Ratio (EAR)**:
  $$\text{EAR} = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 ||p_1 - p_4||}$$
- Normal baseline EAR ranges between $0.28$ and $0.35$.
- When eyes close during a blink, EAR rapidly drops below the threshold ($\le 0.22$).
- A rolling 60-second time window computes the astronaut's continuous **Blink Frequency (blinks/min)**. Normal baseline is 12-24 blinks/min; rates $> 35$ blinks/min correlate with ocular surface desiccation, cabin dry air, or acute cognitive fatigue.

### C. 3D Head Pose Estimation (Perspective-n-Point)
- Utilizes 3D facial model anchor points (Nose tip, Chin, Outer eye corners, Mouth corners) matched against 2D image coordinates.
- Solves the Perspective-n-Point problem (`cv2.solvePnP`) using iterative Levenberg-Marquardt optimization to obtain rotation vector $\mathbf{r}$ and translation vector $\mathbf{t}$.
- Converts $\mathbf{r}$ via Rodrigues' transform to extract Euler rotational angles:
  - **Pitch** (Nodding up/down, -90° to +90°)
  - **Yaw** (Turning left/right, -90° to +90°)
  - **Roll** (Lateral head tilt, -90° to +90°)
- Projects 3D orthogonal coordinate axes (Red: Pitch, Green: Yaw, Blue: Roll) extending from the nose tip.

### D. Bilateral Facial Landmark Symmetry
- Computes Euclidean distances from the central nasal bridge to bilateral facial landmarks (outer canthi, oral commissures).
- Determines Facial Asymmetry Percentage:
  $$\text{Asymmetry } \% = \frac{|d_{\text{left}} - d_{\text{right}}|}{\max(d_{\text{left}}, d_{\text{right}})} \times 100$$
- Symmetry $> 80\%$ is nominal. Marked asymmetry ($> 25\%$) triggers a clinical review to exclude acute cranial nerve deficit.

### E. Camera Quality & Illumination Diagnostics
- **Brightness**: Mean grayscale pixel intensity. Flags `LOW_LIGHT` ($< 40$) or `OVEREXPOSED` ($> 220$).
- **Contrast**: Standard deviation of pixel luminance.
- **Sharpness**: Laplacian operator variance ($\sigma^2_{\text{Laplacian}}$). Detects optical blurriness ($< 15$).
- **Quality Score**: Weighted composite metric (0-100%).

### F. Experimental Remote Photoplethysmography (rPPG)
- Extracts mean green-channel intensity from a stabilized forehead Region of Interest (ROI).
- Applies a temporal bandpass filter (0.75 Hz – 3.0 Hz / 45 – 180 bpm) to isolate capillary blood volume pulse oscillations.
- Identifies signal peaks to derive an estimated pulse rate in beats per minute.
- **Explicit Research Disclaimer**: Labeled on-screen as `[RESEARCH DEMONSTRATION ONLY - NOT FOR CLINICAL DIAGNOSIS]`.

---

## 3. Interactive Guided Visual Tests

### 1. Guided Visual Tracking Test (Smooth Pursuit)
- Displays a luminous moving cyan target traveling on a calibrated 2D Lissajous trajectory across the screen.
- The astronaut follows the target smoothly with eyes and head.
- Calculates instantaneous Euclidean tracking error:
  $$\text{Error} = \sqrt{(x_{\text{target}} - x_{\text{gaze}})^2 + (y_{\text{target}} - y_{\text{gaze}})^2}$$
- Reports average tracking error (in pixels) and a Smoothness Adherence Score (0-100%). Elevated error ($> 40$ px) indicates microgravity vestibular saccadic dysmetria.

### 2. Visual Reaction-Time Test
- Initiates a randomized preparation interval ($1.8 - 3.8$ seconds).
- Displays a high-contrast visual flash prompt (`REACT NOW!`).
- Measures elapsed response latency in milliseconds via touch, click, or blink.
- Normal baseline latency: $220 - 320$ ms. Latency $> 450$ ms flags cognitive exhaustion or psychomotor slowing.

### 3. Guided Head Coordination Test
- Directs astronaut through 5 sequential rotational stages: *Center Baseline, Pitch Up +15°, Yaw Left -20°, Yaw Right +20°, Return to Center*.
- Monitors rotational angular adherence and stability at each stage.
