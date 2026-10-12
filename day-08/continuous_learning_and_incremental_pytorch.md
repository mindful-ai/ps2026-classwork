# Working Examples: Continuous Learning and Incremental Training in PyTorch

We will build two runnable examples using PyTorch:

1. **Continuous learning with replay:** A neural network learns new data while retaining knowledge from previous data using a replay buffer.
2. **Incremental training:** A neural network is trained on one batch, saved, reloaded, and updated using a subsequent batch.

We will use a synthetic industrial defect-classification problem so the examples run without downloading datasets.

---

# 1. Continuous learning with replay on a neural network

## 1.1 Scenario

Imagine a factory inspecting manufactured components. The defect classifier initially learns from one production environment, then encounters data from a different environment.

- **Task A:** Classify components using the initial data distribution.
- **Task B:** Learn from a new production distribution.
- **Problem:** Training only on Task B may cause the model to forget Task A.
- **Solution:** Maintain a replay buffer containing selected Task A examples and mix them with Task B examples during training.

This is called *experience replay*.

### Workflow

1. Task A — Initial data: train the neural network.
2. Replay buffer: retain representative historical examples.
3. Task B — New data: combine new examples with replay examples.
4. Updated network: learn new patterns while retaining old capabilities.

## 1.2 Install dependencies

```bash
pip install torch matplotlib
```

## 1.3 Complete working program

Save as `continuous_learning_replay.py`.

The example deliberately uses two different data distributions, making it possible to compare learning with and without replay.

```python
import copy
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(42)

# --------------------------------------------------
# 1. Create two different production environments
# Input: [feature_1, feature_2, task_id]
# Task A learns from feature_1
# Task B learns from feature_2
# --------------------------------------------------

def make_data(task, n=1000):
    x = torch.randn(n, 2)
    task_id = torch.full((n, 1), float(task))
    X = torch.cat([x, task_id], dim=1)

    if task == 0:
        y = (x[:, 0] > 0).float()
    else:
        y = (x[:, 1] > 0).float()

    return X, y

XA, yA = make_data(task=0, n=1200)
XB, yB = make_data(task=1, n=1200)

# Independent evaluation sets
XAt, yAt = make_data(task=0, n=500)
XBt, yBt = make_data(task=1, n=500)

# --------------------------------------------------
# 2. Define the neural network
# --------------------------------------------------

class DefectNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(1)

def train(model, X, y, epochs=20):
    loader = DataLoader(
        TensorDataset(X, y),
        batch_size=64,
        shuffle=True
    )
    optimizer = torch.optim.Adam(
        model.parameters(), lr=0.005
    )
    criterion = nn.BCEWithLogitsLoss()

    model.train()
    for epoch in range(epochs):
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimizer.step()

def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        predictions = (model(X) >= 0).float()
        return (predictions == y).float().mean().item()

# --------------------------------------------------
# 3. Learn Task A
# --------------------------------------------------

initial_model = DefectNet()
train(initial_model, XA, yA, epochs=30)

print("After Task A:")
print("Task A accuracy:", round(
    accuracy(initial_model, XAt, yAt), 3
))

# Create two identical copies for a fair comparison
model_without_replay = copy.deepcopy(initial_model)
model_with_replay = copy.deepcopy(initial_model)

# --------------------------------------------------
# 4. Strategy 1: Train only on new Task B data
# --------------------------------------------------

train(model_without_replay, XB, yB, epochs=40)

print("\nAfter Task B — no replay:")
print("Task A accuracy:", round(
    accuracy(model_without_replay, XAt, yAt), 3
))
print("Task B accuracy:", round(
    accuracy(model_without_replay, XBt, yBt), 3
))

# --------------------------------------------------
# 5. Strategy 2: Train Task B with replay from Task A
# --------------------------------------------------

# Keep a subset of old examples in the replay buffer
buffer_size = 300
indices = torch.randperm(len(XA))[:buffer_size]
memory_X = XA[indices]
memory_y = yA[indices]

# Mix old examples with new examples
X_combined = torch.cat([XB, memory_X])
y_combined = torch.cat([yB, memory_y])

train(model_with_replay, X_combined, y_combined, epochs=40)

print("\nAfter Task B — with replay:")
print("Task A accuracy:", round(
    accuracy(model_with_replay, XAt, yAt), 3
))
print("Task B accuracy:", round(
    accuracy(model_with_replay, XBt, yBt), 3
))

# Save the updated model and replay buffer
torch.save({
    "model_state_dict": model_with_replay.state_dict(),
    "replay_X": memory_X,
    "replay_y": memory_y
}, "continuous_model.pt")

print("\nSaved continuous_model.pt")
```

## 1.4 Run the example

```bash
python continuous_learning_replay.py
```

## 1.5 What should you observe?

The program prints Task A accuracy after initial training, then Task A and Task B accuracy for both update strategies.

| Strategy | Task A | Task B |
|---|---|---|
| Initial model | Should be high | Not trained for Task B |
| Train on B only | May decrease due to forgetting | Should improve |
| Train on B + replay | Often retains more A performance | Should improve |

Exact results depend on initialization, training duration, and replay-buffer composition. Replay reduces the risk of forgetting; it does not guarantee that every metric will improve.

**Technical points to discuss:**

- `memory_X` and `memory_y` form the replay buffer.
- The model trained without replay receives only new Task B examples.
- The model trained with replay receives both old and new examples.
- Both updated models start from the same initial weights, making the comparison more meaningful.
- The `task_id` feature indicates which production environment an observation came from. In a real application, this feature should only be used if it is available and meaningful at inference time.
- The replay buffer should represent important historical conditions, not merely store arbitrary old records.

The replay buffer can be persisted and extended over multiple training rounds. For large datasets, use a fixed-size reservoir, class-balanced sampling, or a representative subset rather than keeping every historical example.

---

# 2. Incremental training of a PyTorch network

Now consider a different scenario.

A neural network has already been trained on 2,000 industrial observations. A new batch of 500 observations arrives. We want to load the existing model, continue optimization on the new batch, and save the updated checkpoint.

This example focuses on the mechanics of **checkpoint-based incremental training**. Unlike the first example, it does not use replay.

## 2.1 Workflow

1. Batch 1 — 2,000 observations.
2. Train the PyTorch network.
3. Save the model and optimizer checkpoint.
4. Load the checkpoint and lower the learning rate.
5. Batch 2 — 500 new observations.
6. Continue training and save the updated model.

## 2.2 Complete working program

Save as `incremental_pytorch.py`.

This example uses a synthetic dataset with ten input features and a binary target.

```python
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(42)

# --------------------------------------------------
# 1. Generate synthetic industrial data
# --------------------------------------------------

def make_data(n):
    X = torch.randn(n, 10)

    # Simulated relationship between features and defect
    score = (
        X[:, 0]
        + 0.7 * X[:, 1]
        - 0.3 * X[:, 2]
    )
    y = (score > 0).float()

    return X, y

X1, y1 = make_data(2000)   # Initial training batch
X2, y2 = make_data(500)    # New incremental batch
X_test, y_test = make_data(1000)

# --------------------------------------------------
# 2. Define the network
# --------------------------------------------------

class DefectNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x).squeeze(1)

# --------------------------------------------------
# 3. Reusable training function
# --------------------------------------------------

def train_epochs(model, loader, optimizer, epochs):
    criterion = nn.BCEWithLogitsLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0

        for xb, yb in loader:
            optimizer.zero_grad()

            logits = model(xb)
            loss = criterion(logits, yb)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(
            f"Epoch {epoch + 1}: "
            f"loss={total_loss / len(loader):.4f}"
        )

def make_loader(X, y):
    return DataLoader(
        TensorDataset(X, y),
        batch_size=64,
        shuffle=True
    )

def evaluate(model, X, y):
    model.eval()
    with torch.no_grad():
        predictions = (model(X) >= 0).float()
        return (predictions == y).float().mean().item()

# --------------------------------------------------
# 4. Stage 1: Initial training
# --------------------------------------------------

model = DefectNet()
optimizer = torch.optim.Adam(
    model.parameters(), lr=0.001
)

print("INITIAL TRAINING")
train_epochs(
    model,
    make_loader(X1, y1),
    optimizer,
    epochs=10
)

print("Accuracy after initial training:",
      round(evaluate(model, X_test, y_test), 4))

# --------------------------------------------------
# 5. Save checkpoint
# --------------------------------------------------

torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict()
}, "checkpoint_v1.pt")

# --------------------------------------------------
# 6. Stage 2: Load existing model and optimizer
# --------------------------------------------------

checkpoint = torch.load(
    "checkpoint_v1.pt",
    map_location="cpu",
    weights_only=True
)

updated_model = DefectNet()
updated_model.load_state_dict(
    checkpoint["model_state_dict"]
)

updated_optimizer = torch.optim.Adam(
    updated_model.parameters(), lr=0.0002
)
updated_optimizer.load_state_dict(
    checkpoint["optimizer_state_dict"]
)

# Override the learning rate for fine-tuning
for group in updated_optimizer.param_groups:
    group["lr"] = 0.0002

# --------------------------------------------------
# 7. Incremental training using new observations
# --------------------------------------------------

print("\nINCREMENTAL TRAINING")
train_epochs(
    updated_model,
    make_loader(X2, y2),
    updated_optimizer,
    epochs=5
)

print("Accuracy after incremental training:",
      round(evaluate(updated_model, X_test, y_test), 4))

# --------------------------------------------------
# 8. Save updated checkpoint
# --------------------------------------------------

torch.save({
    "model_state_dict": updated_model.state_dict(),
    "optimizer_state_dict": updated_optimizer.state_dict()
}, "checkpoint_v2.pt")

print("\nSaved checkpoint_v2.pt")
```

## 2.3 Run the example

```bash
python incremental_pytorch.py
```

The program prints the training loss for each epoch, test accuracy before the update, test accuracy after the update, and saves two checkpoints.

- `checkpoint_v1.pt`: Initial model and optimizer state.
- `checkpoint_v2.pt`: Updated model and optimizer state.

The synthetic dataset makes this example self-contained. You do not need a CSV file or an external dataset.

## 2.4 What is happening internally?

| Step | Operation | Explanation |
|---|---|---|
| 1 | Initialize model | Create the network architecture |
| 2 | Train on Batch 1 | Learn initial model parameters |
| 3 | Save checkpoint | Preserve weights and Adam optimizer state |
| 4 | Load checkpoint | Restore previously learned parameters |
| 5 | Lower learning rate | Make smaller parameter updates during fine-tuning |
| 6 | Train on Batch 2 | Update the existing model using new observations |
| 7 | Evaluate | Compare test accuracy before and after updating |
| 8 | Save updated checkpoint | Preserve the new model and optimizer state |

## 2.5 Important distinction: this is not replay

The second example uses only the new batch during incremental training. The previous weights provide the starting point, but the old training examples are not revisited.

This can cause **catastrophic forgetting** if the new batch has a different distribution. The first example addresses that risk by explicitly mixing historical examples with new data.

Also, the second example's test data comes from the same synthetic distribution as the training batches. It demonstrates checkpoint-based updating, but does not by itself demonstrate adaptation to a changing production environment.

---

# 3. Comparing both implementations

| Feature | Continuous learning with replay | Incremental PyTorch training |
|---|---|---|
| Initial model | Trained on Task A | Trained on Batch 1 |
| New training data | Task B | Batch 2 |
| Old examples reused? | Yes, via replay buffer | No |
| Optimizer state restored? | No; optimizer is recreated for each training stage | Yes |
| Main purpose | Reduce forgetting across tasks | Demonstrate continued training from a checkpoint |
| Typical use case | Evolving data distributions or tasks | Periodic model updates and continued optimization |

**Production recommendation:** Combine the two approaches when appropriate. Restore the existing model checkpoint, assemble a training dataset containing new examples and representative historical examples, continue optimization with a suitable learning rate, evaluate against fixed old and new test sets, and deploy only if the acceptance criteria are met.

One subtle but important point: in a production pipeline, you should also version the data, preprocessing, model architecture, class definitions, optimizer configuration, and evaluation results. A checkpoint alone is not a complete record of a reproducible model update.

## 4. Suggested exercise

Modify the replay-buffer size and compare how it affects old-task and new-task accuracy. Try buffer sizes of 50, 300, and 800 examples. Keep the initial model and test sets fixed so that the comparison is meaningful.
