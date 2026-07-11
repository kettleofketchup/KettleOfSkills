# Harmonica — spring animation

Module: `github.com/charmbracelet/harmonica` (still on the `github.com` path). A tiny,
physics-based animation library. Instead of scripting keyframes, you define a spring and let it
ease a value toward a moving target with natural motion. Framerate-independent.

## Spring API

```go
import "github.com/charmbracelet/harmonica"

// NewSpring(timeDelta, angularFrequency, dampingRatio float64) Spring  (value, not *Spring)
spring := harmonica.NewSpring(harmonica.FPS(60), 6.0, 0.5)

// Each frame, advance a (position, velocity) pair toward target.
// Update(pos, vel, target float64) (newPos, newVel float64)
pos, vel = spring.Update(pos, vel, target)
```

Parameters:

- **timeDelta** — seconds per frame. Use the `harmonica.FPS(n)` helper for a fixed framerate
  (e.g. `FPS(60)` == `1.0/60`). Must match how often you call `Update`.
- **angularFrequency** — stiffness / speed. Higher = snappier, reaches the target faster.
- **dampingRatio** — oscillation behavior:
  - `< 1.0` — underdamped: overshoots then settles (bouncy).
  - `= 1.0` — critically damped: fastest settle with no overshoot.
  - `> 1.0` — overdamped: slow, no overshoot.

Track `position` and `velocity` as your own state; the spring is stateless between calls.

## Integrating with Bubble Tea

Drive `Update` from a repeating `tea.Tick` at the same rate you passed to `NewSpring`:

```go
type frameMsg time.Time

const fps = 60

func animate() tea.Cmd {
	return tea.Tick(time.Second/fps, func(t time.Time) tea.Msg { return frameMsg(t) })
}

type model struct {
	spring         harmonica.Spring
	x, xVel, target float64
}

func initial() model {
	return model{spring: harmonica.NewSpring(harmonica.FPS(fps), 8.0, 0.4)}
}

func (m model) Init() tea.Cmd { return animate() }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyPressMsg:
		switch msg.String() {
		case "right":
			m.target += 10
		case "left":
			m.target -= 10
		case "q", "ctrl+c":
			return m, tea.Quit
		}
	case frameMsg:
		m.x, m.xVel = m.spring.Update(m.x, m.xVel, m.target)
		return m, animate() // re-issue the tick to keep the loop going
	}
	return m, nil
}

func (m model) View() tea.View {
	col := int(m.x)
	if col < 0 { col = 0 }
	return tea.NewView(strings.Repeat(" ", col) + "●\n\n←/→ to move · q to quit\n")
}
```

## Tips

- **Store the spring in the model** and reuse it — don't rebuild it each frame.
- Round `position` to an `int` column/row only at render time; keep the float in state so motion
  stays smooth.
- Animate anything numeric: a cursor's X/Y, a scroll offset, a progress ratio, a gauge value —
  set `target` and the spring handles the in-between frames.
- To animate two axes, keep two `(pos, vel)` pairs (they can share one `Spring`).
- Stop re-issuing the tick once `position` is within an epsilon of `target` **and** velocity is
  near zero, to avoid spinning the CPU on a settled animation.
