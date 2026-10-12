# Adam Optimizer

## What is Adam?

**Adam (Adaptive Moment Estimation)** is an optimization algorithm used to train neural networks. It combines ideas from **Momentum** and **RMSprop** to adapt weight updates using estimates of both the gradient and the squared gradient.

## How Adam Works

1. **Calculate gradients:** Backpropagation calculates the gradient of the loss with respect to each model parameter.
2. **Estimate the first moment:** Adam maintains an exponentially weighted average of past gradients. This helps smooth the update direction, similar to Momentum.
3. **Estimate the second moment:** Adam maintains an exponentially weighted average of squared gradients. This helps adapt the update scale for each parameter, similar to RMSprop.
4. **Correct initialization bias:** Because the moving averages start at zero, Adam applies bias correction, especially important during early updates.
5. **Update parameters:** Adam uses the corrected averages to update the model weights.

## Key Equations

Let:

- \(g_t\) be the gradient at step \(t\)
- \(m_t\) be the first-moment estimate
- \(v_t\) be the second-moment estimate
- \(\beta_1\) and \(\beta_2\) be exponential-decay rates
- \(\eta\) be the learning rate
- \(\epsilon\) be a small constant for numerical stability

First-moment estimate:

\[
m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t
\]

Second-moment estimate:

\[
v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2
\]

Bias-corrected estimates:

\[
\hat m_t = \frac{m_t}{1-\beta_1^t}
\]

\[
\hat v_t = \frac{v_t}{1-\beta_2^t}
\]

Parameter update:

\[
\theta_{t+1} = \theta_t -
\eta \frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}
\]

The operations on gradients and parameters are applied element-wise.

## Why Adam Is Widely Used

- Adapts update sizes for individual parameters.
- Combines a smoothed gradient direction with adaptive scaling.
- Often converges quickly and works well across many deep-learning tasks.
- Usually requires less manual tuning than basic SGD, although tuning is still important.

## Common Starting Settings

Typical Adam defaults in many frameworks are:

- Learning rate: `0.001`
- `beta1`: `0.9`
- `beta2`: `0.999`
- `epsilon`: `1e-8`

These are starting points, not universal best settings. The appropriate learning rate and other parameters depend on the model, data, and training setup.

## Adam vs. SGD

| Feature | Adam | SGD |
|---|---|---|
| Update scale | Adapts per parameter | Usually uses a shared learning rate |
| Gradient history | Uses first and second moments | Basic SGD uses the current gradient |
| Initial tuning | Often convenient as a baseline | May require more learning-rate tuning |
| Common use | General deep learning and many transformer tasks | Computer vision and settings where it performs well after tuning |

## Important Industrial Considerations

- Monitor training and validation metrics; a falling training loss alone does not guarantee good generalization.
- Tune the learning rate if training is unstable or convergence is slow.
- Use gradient clipping when gradient explosions are a concern.
- Record optimizer settings to make experiments reproducible.
- Consider **AdamW** when decoupled weight decay is desired; AdamW is related to Adam but handles weight decay differently.

## Key Takeaway

**Momentum smooths the update direction, while RMSprop-like scaling adapts the update size. Adam combines both and applies bias correction to produce its parameter updates.**
