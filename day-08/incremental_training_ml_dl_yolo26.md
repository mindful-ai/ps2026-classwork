# Incremental Training: Machine Learning, Deep Learning, and YOLO26

This topic can be developed as a technical learning module that progresses from classical machine learning to deep neural networks and finally to object detection using YOLO26.

The central question is:

**When new data becomes available, how can we improve an existing trained model without rebuilding everything from scratch?**

Consider an industrial rice-sorting system. Initially, a model is trained on 10,000 images of rice grains. After deployment, the system encounters new grain varieties, unusual defects, different lighting conditions, and previously unseen impurities. We want to use these new examples to improve the model while minimizing training time, computational cost, and production downtime.

This problem leads to incremental training, also called *continued training* or, in specific settings, *online learning*.

## 1. Learning objectives

By the end of this module, learners should be able to:

- Explain incremental learning versus retraining and online learning.
- Incrementally train classical ML models using new batches of data.
- Continue training deep learning models from saved checkpoints.
- Understand catastrophic forgetting, concept drift, and data replay.
- Fine-tune a pretrained YOLO26 model on new images and annotations.
- Design a repeatable training, evaluation, versioning, and deployment pipeline.
- Decide when incremental training is appropriate and when a complete retraining is preferable.

## 2. The three levels of incremental training

### Level 1 — Classical machine learning

**Examples:** Logistic Regression, SGDClassifier, Naive Bayes

Update a model using new observations, without necessarily repeating training over all historical data.

### Level 2 — Deep learning

**Examples:** MLPs, CNNs, Transformers

Load existing weights and continue gradient-based optimization using new or combined data.

### Level 3 — YOLO26 object detection

**Examples:** rice-grain detection, defect detection, industrial sorting

Fine-tune an existing detector using new images and bounding-box annotations, then validate detection quality and inference performance.

The important distinction is that incremental training does not always mean the same operation. Some algorithms explicitly support incremental updates; other models require continued optimization over batches of data; and object detectors additionally depend on annotation consistency, detection losses, and class definitions.

---

# Part I — Incremental training of classical machine learning models

## 3. What is incremental training?

Suppose we have an initial dataset:

\\[
D_0=\\{(x_i,y_i)\\}_{i=1}^{N_0}
\\]

We train an initial model:

\\[
M_0 = \\operatorname{Train}(D_0)
\\]

Later, a new dataset becomes available:

\\[
D_1=\\{(x_i,y_i)\\}_{i=N_0+1}^{N_0+N_1}
\\]

Incremental training attempts to update the existing model:

\\[
M_1 = \\operatorname{Update}(M_0,D_1)
\\]

Instead of always executing:

\\[
M_1=\\operatorname{Train}(D_0\\cup D_1)
\\]

The benefit can be lower computational cost and faster adaptation. However, the incremental model is not guaranteed to be equivalent to a model trained from scratch on all the data.

### Example: Manufacturing defect prediction

A factory predicts whether a manufactured component will pass quality inspection.

Initial training data:

| Feature | Description |
|---|---|
| Temperature | Machine operating temperature |
| Vibration | Measured vibration |
| Pressure | Operating pressure |
| Defect | 0 = acceptable, 1 = defective |

The initial model is trained on 20,000 historical components. One month later, 2,000 newly inspected components become available.

The system can use these new observations to update the model, provided the chosen algorithm supports the required update method.

## 4. Which classical ML algorithms support incremental training?

| Algorithm | Incremental support | Practical approach |
|---|---|---|
| `SGDClassifier` | Yes | `partial_fit()` |
| `SGDRegressor` | Yes | `partial_fit()` |
| `MultinomialNB` | Yes | `partial_fit()` |
| `GaussianNB` | Yes | `partial_fit()` |
| `PassiveAggressiveClassifier` | Yes | `partial_fit()` |
| `LogisticRegression` | No standard `partial_fit()` API in scikit-learn | Retrain, or use an SGD-based alternative |
| `RandomForestClassifier` | No standard incremental update of existing trees | Retrain or adopt another approach |
| `XGBoost` | Supported continuation in certain configurations | Continue from a compatible model using additional boosting rounds |

**Key concept:** Incremental learning is an algorithm capability, not simply a property of the model file. Saving a model and loading it later does not automatically make its algorithm incrementally trainable.

## 5. Example 1 — Incremental classification using SGDClassifier

We will create a synthetic industrial quality-control dataset and train a classifier in two stages.

Stage 1: Train using the initial batch.

Stage 2: Update the model using a new batch.

The example uses `partial_fit()`, which updates the model using the supplied batch.

### 5.1 Implementation

Install the required libraries:

```bash
pip install numpy scikit-learn joblib
```

Create `incremental_ml.py`:

```python
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

rng = np.random.default_rng(42)

def make_data(n):
    temperature = rng.normal(70, 8, n)
    vibration = rng.normal(4, 1.5, n)
    pressure = rng.normal(100, 10, n)

    # Synthetic relationship for demonstration
    score = (
        0.08 * (temperature - 70)
        + 0.8 * (vibration - 4)
        + 0.03 * (pressure - 100)
    )
    y = (score > 0.5).astype(int)

    X = np.column_stack([
        temperature, vibration, pressure
    ])
    return X, y

# Stage 1: Initial batch
X1, y1 = make_data(2000)

# Scale the features and train the model
scaler = StandardScaler()
X1_scaled = scaler.fit_transform(X1)

model = SGDClassifier(
    loss="log_loss",
    random_state=42
)

model.partial_fit(X1_scaled, y1, classes=[0, 1])

# Evaluate on a separate initial test set
X_test, y_test = make_data(500)
X_test_scaled = scaler.transform(X_test)

print("Initial accuracy:",
      accuracy_score(y_test, model.predict(X_test_scaled)))

# Stage 2: New observations arrive
X2, y2 = make_data(500)
X2_scaled = scaler.transform(X2)

# Update existing model, rather than creating a new one
model.partial_fit(X2_scaled, y2)

print("Updated accuracy:",
      accuracy_score(y_test, model.predict(X_test_scaled)))

# Save both preprocessing and model
joblib.dump(
    {"scaler": scaler, "model": model},
    "incremental_model.joblib"
)
```

The data is synthetic; the code demonstrates the update mechanism, not a validated industrial prediction system.

### 5.2 What happens internally?

The training process is:

1. **Batch 1 — 2,000 observations**
2. Fit scaler and initialize classifier.
3. Obtain model M₀.
4. **Batch 2 — 500 new observations**
5. `partial_fit()` updates existing coefficients.
6. Obtain updated model M₁.

`partial_fit()` performs another optimization update. It does not automatically retain or revisit all previous training examples.

**Important production considerations:**

1. **Preprocessing:** Use the same feature transformations during training and inference. The example freezes the initial scaler. If feature distributions change significantly, evaluate whether the scaler and model need coordinated updating.
2. **Evaluation:** Use an independent validation or test dataset. Do not assume that updating the model improves its accuracy.
3. **Class imbalance:** A new batch containing mostly acceptable components may fail to teach the model about rare defects.
4. **Data ordering:** SGD is sensitive to learning rate, batch order, and number of update passes.
5. **Reproducibility:** Save the model, scaler, feature schema, class definitions, training data version, and metrics together.

### 5.3 A crucial distinction: incremental versus online learning

| Approach | Description | Example |
|---|---|---|
| Batch learning | Train using the available dataset | Train every month on all collected records |
| Mini-batch incremental learning | Update using successive batches | Process 500 new inspection records daily |
| Online learning | Update as individual examples or very small batches arrive | Update after each labeled transaction |
| Periodic retraining | Train a new model on a refreshed historical dataset | Retrain every Sunday on the latest six months of data |

Online learning is a form of incremental learning. However, many production systems use periodic mini-batch updates because labels arrive with delays and model deployment requires validation.

---

# Part II — Incremental training of deep learning models

## 6. How deep learning incremental training works

Deep learning models contain large numbers of trainable parameters:

\\[
\\theta = \\{W_1,b_1,W_2,b_2,\\ldots,W_L,b_L\\}
\\]

During training, the model minimizes a loss function:

\\[
\\theta_{t+1} = \\theta_t - \\eta \\nabla_\\theta \\mathcal{L}(\\theta_t)
\\]

Here:

- \\(\\theta_t\\): model parameters at the current optimization step.
- \\(\\mathcal{L}\\): loss computed from the current batch.
- \\(\\nabla_\\theta \\mathcal{L}\\): gradients of the loss with respect to parameters.
- \\(\\eta\\): learning rate.

In incremental deep learning, training continues from previously learned parameters rather than initializing the network from scratch.

The process is often called *continued training* or *fine-tuning*, depending on the objective.

## 7. Four ways to update a deep learning model

### Method A — Full-model fine-tuning

All or most network parameters remain trainable. New data updates the feature extractor and prediction layers.

**Best when:** The target domain differs meaningfully from the original domain.

### Method B — Freeze the backbone, train the head

Keep early feature-extraction layers fixed and update the final prediction layers.

**Useful when:** Labeled data is limited and the existing features are relevant.

### Method C — Parameter-efficient fine-tuning

Train a smaller set of added or selected parameters, such as adapters or LoRA modules, instead of all weights.

**Common in:** Large language models and some vision architectures.

### Method D — Continual learning with replay

Combine new examples with selected historical examples to preserve earlier capabilities while learning new patterns.

**Useful when:** The data distribution changes over time and old categories must remain supported.

These methods can be combined. For example, a CNN can initially freeze its backbone, then unfreeze selected layers and train with a lower learning rate.

## 8. The main challenge: catastrophic forgetting

Consider an industrial image classifier trained on:

- Class A: acceptable rice grains.
- Class B: broken rice grains.
- Class C: discolored grains.

A new dataset is then collected containing mostly a new impurity class, such as small stones.

If the model is trained only on the new examples, its performance on the original classes can deteriorate. This is called **catastrophic forgetting**.

### Why does it happen?

The parameters learned from the new dataset may overwrite parameter values that were useful for previous tasks. Gradient descent optimizes the current training objective; it does not inherently guarantee preservation of historical performance.

### Techniques to reduce forgetting

| Technique | Mechanism | Trade-off |
|---|---|---|
| Replay buffer | Mix selected historical examples into new training | Requires storing representative old data |
| Balanced sampling | Ensure old and new classes are adequately represented | Requires suitable sampling rules |
| Lower learning rate | Reduce the size of parameter updates | Adaptation may take longer |
| Freeze selected layers | Preserve useful representations | May limit learning of new features |
| Regularization | Penalize undesirable changes to parameters | Additional tuning and complexity |
| Knowledge distillation | Encourage the updated model to preserve old model outputs | Requires a teacher model and suitable objective |

For ordinary industrial fine-tuning, a balanced training dataset containing old and new examples is often the simplest first approach.

## 9. Example 2 — Incremental training of a PyTorch neural network

We will use an MLP for binary defect classification. The example demonstrates loading the existing weights, training on new data, and saving the updated model.

Install:

```bash
pip install torch scikit-learn
```

### Implementation

```python
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

torch.manual_seed(42)

class DefectNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.network(x)

def train_epochs(model, loader, optimizer, epochs=5):
    criterion = nn.BCEWithLogitsLoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0

        for X, y in loader:
            optimizer.zero_grad()
            logits = model(X).squeeze(1)
            loss = criterion(logits, y)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1}: loss={total_loss / len(loader):.4f}")

def make_loader(n=1000):
    X = torch.randn(n, 10)
    # Synthetic labels based on a simple relationship
    y = (X[:, 0] + X[:, 1] > 0).float()
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=64, shuffle=True)

# Stage 1: initial training
model = DefectNet()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

train_epochs(model, make_loader(1000), optimizer, epochs=5)

# Save model weights and optimizer state
torch.save({
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict()
}, "checkpoint.pt")

# Stage 2: load the existing model
checkpoint = torch.load("checkpoint.pt", weights_only=True)

model2 = DefectNet()
model2.load_state_dict(checkpoint["model"])

optimizer2 = torch.optim.Adam(model2.parameters(), lr=2e-4)
optimizer2.load_state_dict(checkpoint["optimizer"])

# Optional: override the learning rate for fine-tuning
for group in optimizer2.param_groups:
    group["lr"] = 2e-4

# Continue training using a new batch
train_epochs(model2, make_loader(300), optimizer2, epochs=3)

torch.save(model2.state_dict(), "updated_model.pt")
```

This example is intended to demonstrate the mechanics of continued training. For production work, save and evaluate the complete model checkpoint, use a fixed independent validation set, and include old examples if preserving earlier performance is important.

### 9.1 What is actually preserved?

The model checkpoint contains learned network weights. The optimizer checkpoint contains optimizer state, such as Adam's moving averages.

These are different:

- **Weights only:** The model can make predictions and can continue training, but the optimizer starts with fresh state.
- **Weights plus optimizer state:** Training can continue more closely from the previous optimization state.
- **Full training state:** Weights, optimizer, scheduler, epoch, random-number states, and configuration provide a more reproducible continuation.

The correct choice depends on whether you are resuming an interrupted run or starting a new fine-tuning stage.

## 10. Checkpoint resumption versus new-data fine-tuning

This distinction is especially important in technical discussions.

| Scenario | Correct approach |
|---|---|
| Training stopped unexpectedly | Restore the checkpoint and resume training |
| Need additional epochs on the same dataset | Resume or continue training |
| New labeled data arrives | Fine-tune with the new data and, preferably, representative old data |
| Need to preserve performance across old classes | Use replay, balanced sampling, or a continual-learning strategy |
| Feature schema or output classes change | Adapt the architecture and training pipeline carefully |
| Model has degraded significantly | Consider retraining using the refreshed historical dataset |

Resuming an interrupted run is not automatically the same as incremental learning on new data. In particular, resuming restores the prior training state, whereas fine-tuning on new data is a new training stage with an intentionally selected dataset and training configuration.

---

# Part III — Incremental training of YOLO26

## 11. Understanding the YOLO26 training problem

For an industrial object-detection system, incremental training involves more than updating a classifier. The model must learn to predict:

- **Object location:** Bounding-box coordinates.
- **Object category:** Rice grain, broken grain, stone, discolored grain, and so on.
- **Detection confidence:** How strongly a detection is supported.
- **Multiple objects:** Several instances can appear in one image.

YOLO26 is supported by the Ultralytics training API. Its official pretrained checkpoints are already trained on large datasets, and you can fine-tune them on your own annotated data. [Ultralytics YOLO26 training documentation](https://docs.ultralytics.com/modes/train/).

### 11.1 An industrial rice-sorting scenario

Assume you are building a rice-grain inspection system using a camera and an ejector mechanism.

**Stage 1 — Initial training**

- 10,000 annotated images.
- Train a YOLO26 detector for acceptable grains, broken grains, and visible impurities.

**Stage 2 — New data collection**

- 2,000 new annotated images.
- New rice varieties, different illumination, additional defect types, or changes in camera settings.

**Stage 3 — Incremental update**

Fine-tune the existing weights using a curated mixture of new images and selected historical images.

**Stage 4 — Validate and deploy**

Compare detection quality, false rejections, missed defects, inference latency, and ejector timing before replacing the production model.

The objective is to improve performance on the new conditions without significantly degrading detection of previously learned defects.

## 12. Three distinct YOLO26 training operations

It is important to distinguish these operations because they are frequently confused.

| Operation | Starting point | Dataset | Main purpose |
|---|---|---|---|
| Training from scratch | Model architecture with random initialization | Full training dataset | Learn all features from the beginning |
| Fine-tuning / incremental update | Existing pretrained or custom-trained weights | New data, preferably with representative old data | Adapt to a new domain or additional examples |
| Resume training | An interrupted training checkpoint | Continue the previous run, or explicitly configure a changed dataset | Continue the same training run |

**Practical recommendation:** If a working rice detector already exists and new annotated images arrive, start by fine-tuning the existing `.pt` model. Do not restart from a YAML architecture unless you specifically intend to train from scratch.

## 13. Dataset preparation for incremental YOLO26 training

Before training, establish a consistent annotation and dataset strategy.

A typical directory structure is:

```text
rice_dataset/
├── images/
│   ├── train/
│   │   ├── batch1_001.jpg
│   │   ├── batch1_002.jpg
│   │   └── batch2_001.jpg
│   ├── val/
│   │   └── val_001.jpg
│   └── test/
│       └── test_001.jpg
└── labels/
    ├── train/
    │   ├── batch1_001.txt
    │   ├── batch1_002.txt
    │   └── batch2_001.txt
    ├── val/
    └── test/
```

Each image has a corresponding label file. YOLO detection annotations generally contain one line per object:

```text
class_id x_center y_center width height
```

Coordinates are normalized relative to the image dimensions.

Example:

```text
0 0.512 0.440 0.080 0.035
1 0.620 0.520 0.060 0.030
```

This indicates two objects, with class IDs 0 and 1.

### Define the class mapping

For example:

```yaml
path: rice_dataset

train: images/train
val: images/val
test: images/test

names:
  0: good_grain
  1: broken_grain
  2: discolored_grain
  3: stone
```

All old and new annotations must use the intended class mapping consistently.

If a new class is introduced, ensure that every training and evaluation annotation uses the correct class ID. A changed class definition or class ordering can cause serious errors even when the training process completes successfully.

### Should you train only on new images?

Suppose the original dataset contains 10,000 images and the new batch contains 2,000.

- **New data only:** 2,000 images.
- **Combined dataset:** 12,000 images.
- **Replay dataset:** 2,000 new images plus, for example, 2,000 carefully selected historical images.

Training on new data alone can be faster, but it can also cause catastrophic forgetting. A replay dataset can reduce this risk while keeping training manageable.

These quantities are illustrative; the right mixture depends on the diversity, rarity, and difficulty of the objects.

## 14. Example 3 — Fine-tuning YOLO26 on a new batch

Install the library:

```bash
pip install -U ultralytics
```

Assume an existing model is stored at:

```text
runs/detect/rice_v1/weights/best.pt
```

This is the starting model from the initial training stage.

### 14.1 Fine-tuning using a combined dataset

```python
from ultralytics import YOLO

# Load the previously trained rice detector
model = YOLO("runs/detect/rice_v1/weights/best.pt")

# Fine-tune using a dataset containing:
# - representative historical images
# - newly collected and annotated images
results = model.train(
    data="rice_combined.yaml",
    epochs=30,
    imgsz=640,
    batch=16,
    device=0,
    project="runs/detect",
    name="rice_v2",
    patience=10,
    seed=42
)

print("Training completed.")
```

The model starts from existing learned weights. The training process then updates the parameters using the combined training dataset.

The values above are starting points for experimentation, not guaranteed optimal settings. Adjust image size, batch size, epochs, and augmentation to match your hardware and data.

The expected outputs include:

```text
runs/detect/rice_v2/
├── weights/
│   ├── best.pt
│   └── last.pt
├── results.csv
├── results.png
└── ...
```

- `best.pt` is the best checkpoint according to the configured validation fitness.
- `last.pt` is the final checkpoint of the run.
- `results.csv` contains epoch-level training and validation metrics.

The `best.pt` checkpoint is normally the candidate to evaluate for deployment.

### 14.2 What if the new data adds a class?

Suppose version 1 detects three classes and version 2 must detect four.

1. Update the dataset YAML with the new class.
2. Add correct bounding-box annotations for the new class.
3. Ensure old classes remain correctly mapped.
4. Fine-tune from the previous model.
5. Evaluate the old classes and the new class separately.

Ultralytics supports transfer of compatible pretrained weights when the detection head changes, but incompatible output layers may be reinitialized. The result is therefore a fine-tuning process, not a guarantee that every old class retains its previous performance. See the [Ultralytics fine-tuning guide](https://docs.ultralytics.com/guides/finetuning-guide/).

## 15. Using a lower learning rate for incremental updates

A useful technique is to lower the learning rate when fine-tuning an already-trained detector.

For example:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/rice_v1/weights/best.pt")

results = model.train(
    data="rice_combined.yaml",
    epochs=20,
    imgsz=640,
    batch=16,
    optimizer="AdamW",
    lr0=0.001,
    patience=8,
    project="runs/detect",
    name="rice_v2_low_lr"
)
```

Here, `lr0=0.001` is an explicitly selected initial learning rate. The scheduler will adjust the learning rate during training.

A lower learning rate can help preserve useful existing features, but it does not guarantee protection against forgetting. The dataset composition and the training schedule matter too.

Ultralytics documents fine-tuning settings and dataset-size considerations in its [YOLO26 training recipe](https://docs.ultralytics.com/guides/yolo26-training-recipe/).

## 16. Fine-tuning versus freezing layers

YOLO26 can also be fine-tuned with some layers frozen.

For example:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/rice_v1/weights/best.pt")

model.train(
    data="rice_combined.yaml",
    epochs=30,
    imgsz=640,
    freeze=10,
    project="runs/detect",
    name="rice_v2_frozen"
)
```

`freeze=10` requests freezing the first ten layers according to the framework's layer-freezing behavior.

This can reduce the number of trainable parameters, but the optimal setting depends on the architecture and how different the new images are from the original training images.

| Situation | Possible approach |
|---|---|
| New images under slightly different lighting | Fine-tune with a lower learning rate |
| New rice varieties with similar visual features | Fine-tune the model, potentially freezing early layers |
| New defect patterns requiring different features | Unfreeze more layers and fine-tune |
| Major camera or image-domain change | Fine-tune more broadly and evaluate carefully |
| New detection classes | Fine-tune with a compatible class mapping and validate all classes |

Do not assume that freezing more layers is always better. Compare the results empirically.

## 17. Resuming an interrupted YOLO26 run

If training stops because of a power failure, system crash, or time limit, resume from the last checkpoint:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/rice_v2/weights/last.pt")

results = model.train(resume=True)
```

When supported by the saved checkpoint, resuming restores training state such as the optimizer, learning-rate scheduler, and epoch progress.

This is appropriate when continuing the interrupted run. It is not the same as beginning a new incremental update with a newly curated dataset.

For a new data batch, use the previous model weights and a deliberate fine-tuning configuration. See the official [training and resumption documentation](https://docs.ultralytics.com/modes/train/).

---

# Part IV — Making incremental training production-ready

## 18. The complete industrial pipeline

For your rice-sorting application, the production pipeline should separate image acquisition, annotation, training, validation, and deployment.

1. **Image acquisition:** Line-scan camera, conveyor images, production batches.
2. **Dataset versioning:** Store images, labels, timestamps, batch IDs and camera settings.
3. **Label quality control:** Review annotations, class mapping, duplicates and rare defects.
4. **Incremental training:** Load previous checkpoint; train on new and replay data.
5. **Validation gates:** Compare accuracy, missed defects, false positives and latency.
6. **Model registry and deployment:** Version model; deploy only after passing acceptance criteria.

## 19. How do we decide whether to update the model?

A model should not be retrained simply because new images are available. First determine whether the new images represent a meaningful change.

Useful triggers include:

- A new defect class has been identified.
- A new rice variety is introduced.
- Lighting or camera configuration changes.
- The rate of missed defects increases.
- False-rejection rates increase.
- Performance on a recent validation dataset declines.
- A sufficient quantity of verified new labels has accumulated.

A practical system may monitor these signals and trigger a retraining workflow when a threshold is crossed.

## 20. Evaluation metrics for incremental training

For YOLO26, compare the previous model and the candidate model on the same held-out evaluation sets.

| Metric | What it tells us |
|---|---|
| Precision | What fraction of predicted detections are correct |
| Recall | What fraction of ground-truth objects are detected |
| mAP@0.5 | Mean average precision at an IoU threshold of 0.5 |
| mAP@0.5:0.95 | Average performance over a range of IoU thresholds |
| Per-class recall | Whether specific defect classes are being missed |
| False positives per image | How frequently unwanted detections occur |
| Inference latency | How long the model takes to produce predictions |
| Ejector timing accuracy | Whether detections lead to correctly timed physical rejection |

The last metric is especially important in an industrial sorter. A model can have good mAP and still be unsuitable for production if detection latency, object tracking, or ejector timing is incorrect.

### Example acceptance gates

The following are illustrative criteria, not universal standards:

- New-class recall must exceed 95%.
- Recall on critical existing defect classes must not drop by more than one percentage point.
- False-rejection rate must remain below the factory's agreed threshold.
- Inference and actuation must meet the real-time latency budget.
- All safety-critical and operational tests must pass.

The thresholds should be derived from the business cost of missed defects, false rejections, and production downtime.

## 21. Recommended experiment: compare three strategies

A strong technical workshop should compare the following methods using the same initial model and held-out test sets.

| Experiment | Training data | Question answered |
|---|---|---|
| A — New data only | New images | How well does the model adapt, and how much forgetting occurs? |
| B — Combined data | Old and new images | Does replay preserve earlier capabilities? |
| C — Combined data + lower learning rate | Old and new images, smaller updates | Does a conservative update improve the balance between old and new performance? |

Record the results:

| Metric | Model v1 | Experiment A | Experiment B | Experiment C |
|---|---:|---:|---:|---:|
| Old-class recall | Measure | Measure | Measure | Measure |
| New-class recall | Measure | Measure | Measure | Measure |
| mAP@0.5:0.95 | Measure | Measure | Measure | Measure |
| False positives per image | Measure | Measure | Measure | Measure |
| Inference latency | Measure | Measure | Measure | Measure |

This experiment makes the trade-offs visible. Do not assume that one strategy will always win; the outcome depends on data diversity, annotation quality, model capacity, and training settings.

---

# Part V — Advanced technical discussion

## 22. Important questions for deeper discussion

**Q1. Does incremental training always require less compute?**

No. An update using only a small new batch may require less compute, but repeatedly training on old and new data can approach the cost of full retraining. The appropriate comparison is the total cost of training, evaluation, data preparation, and deployment.

**Q2. Can we train on unlabeled images?**

Not directly with the standard supervised detection pipeline in the same way as labeled data. Unlabeled images can support semi-supervised methods, pseudo-labeling, or teacher–student training. Pseudo-labels must be reviewed or quality-controlled because incorrect labels can reinforce errors.

**Q3. Can the production model update itself continuously?**

Technically, some systems can. However, automatic updates should not replace a validated production model without evaluation. A safer pattern is to train a candidate model offline, test it, and promote it only after passing acceptance gates.

**Q4. How should we handle concept drift?**

Concept drift occurs when the relationship between input features and target outcomes changes. Examples include new manufacturing conditions or a change in the distribution of defects. Monitor recent performance, collect verified labels, and compare periodic updates against a stable evaluation set.

**Q5. Does incremental training preserve the previous model automatically?**

No. Preserve the previous checkpoint independently, version the data and training configuration, and deploy the candidate separately. This makes rollback possible if the new model performs poorly.

## 23. Final comparison of the three approaches

| Aspect | Classical ML | Deep learning | YOLO26 |
|---|---|---|---|
| Typical update | `partial_fit()` where supported | Continue gradient optimization | Fine-tune an existing detector |
| Input | Structured features | Tensors, images, sequences or text | Images plus object annotations |
| Main concern | Feature drift and update stability | Catastrophic forgetting and optimization | Forgetting, annotation quality, detection performance and latency |
| Old data needed? | Depends on algorithm and drift | Often beneficial | Often beneficial, especially for retaining old classes |
| Main evaluation | Classification/regression metrics | Task-specific validation metrics | mAP, per-class recall, false positives and inference latency |
| Deployment concern | Schema and preprocessing consistency | Checkpoint compatibility | Real-time performance, model export, tracking and actuation |

## 24. Suggested teaching sequence

For a detailed technical workshop, I recommend this progression:

1. **Theory:** Incremental learning, online learning, fine-tuning, and retraining.
2. **Classical ML lab:** Implement `partial_fit()` and compare successive updates.
3. **Deep learning lab:** Save and restore checkpoints, continue optimization, and observe forgetting.
4. **YOLO26 lab:** Fine-tune on a new batch and compare new-data-only versus combined-data training.
5. **Industrial deployment lab:** Implement validation gates, model versioning, rollback, and performance monitoring.

The most important lesson across all three levels is that incremental training is not just a way to save training time. It is a controlled model-lifecycle strategy: **update the model, verify that it has improved where needed, confirm that previous capabilities remain acceptable, and only then deploy it.**
