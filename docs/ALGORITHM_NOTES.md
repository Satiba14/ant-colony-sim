# Algorithm Notes

Running log of what broke, why, and how it got fixed. Kept while building,
not reconstructed afterward — this is closer to what an interviewer
actually wants to hear than "I built an ant simulator and it worked."

## Phase 1: Core simulation logic (standalone Python)

### Attempt 1: naive pheromone following
Ants wandered randomly, biased toward pheromone. When an ant found food, it
walked back toward the nest using a distance heuristic and laid pheromone
along the way.

**Result: broken.** Average trip length got *worse* over time (climbing
past 500-1000 steps) instead of better.

**Diagnosis:** pheromone was piling up right around the nest, because every
returning ant's path converged there regardless of which route it took.
This created a "gravity well" that trapped searching ants near the nest
instead of letting them push out toward the food.

### Attempt 2: exact path retracing
Fixed by having each ant remember the exact sequence of cells it walked to
find food, then retrace that exact path home (reversed), depositing
pheromone only on cells it actually used - not a vague heuristic route.
Shorter trips deposit *more* pheromone per cell (`amount = DEPOSIT / trip_length`),
so efficient trips get rewarded more than long ones.

**Result: better, but still slow.** Very few trips completed - pure
pheromone-following before any trail exists is close to a blind random
walk, which takes a very long time to travel any real distance.

### Attempt 3: added a heuristic signal
Real Ant Colony Optimization doesn't rely on pheromone alone - it also uses
a heuristic (a weak, built-in pull toward the goal, like real ants having
a rough sense of direction). Added `heuristic_signal = (1 / distance_to_food) ^ POWER`,
multiplied together with the pheromone signal when choosing each move.

**Result: much faster convergence** - trip count went from ~20 completed
trips in 2000 ticks to 200+.

### Attempt 4: premature convergence (stagnation)
Once heuristic + pheromone were combined, a new problem appeared: one
lucky-but-mediocre path would get marked early, and because pheromone
values could grow large enough to override the heuristic pull, the whole
colony would pile onto that mediocre path instead of finding a better one.
Average trip length was unstable and sometimes climbed over time even with
these fixes in place.

**Fix:** capped pheromone strength relative to the heuristic's scale, and
increased pheromone decay rate so stale trails fade faster and can't
"lock in" a suboptimal path.

### Attempt 5: elitist reinforcement
Even after Attempt 4, average trip length plateaued well above the
theoretical minimum and didn't keep improving. Added elitist
reinforcement: the single best trip ever found gets a steady pheromone
top-up every tick, regardless of whether current ants are walking it. This
is a real, documented ACO technique - it stops a genuinely good path from
fading away just because the colony "moved on."

### Attempt 6: the open-field problem
Even with elitist reinforcement, the "average trip length" metric stayed
noisy and never cleanly converged. Root cause: in open, unobstructed 2D
space, there is no single shortest path - dozens of routes (one row up,
one row down) are equally good, so ants splitting across them looked like
"no convergence" even when the algorithm was working correctly.

**Fix:** rebuilt the environment around a fork - a wall with two gaps, one
leading to a short direct route and one forcing a long detour. This is the
same setup real ant researchers use (Deneubourg's "double bridge"
experiment, 1990) specifically because open space doesn't give a clean
signal. Switched the success metric from "average trip length" to "% of
trips using the short gap."

**Result:** clean convergence - 90-100% of trips used the short gap after
the first handful of successes, matching published results from real ant
experiments (which also don't always hit a perfect 100%).

**Key lesson:** the right *test setup* matters as much as the algorithm
itself. A vague test (open field, "average distance") produced a vague,
unconvincing result even when the underlying logic was correct. A sharper
test (binary choice between two known routes) gave an unambiguous answer.

## Phase 2: Canvas visualization (browser, JS)

Ported the Phase 1 Python logic 1:1 into JavaScript - same grid, same
fork, same elitist reinforcement, same pheromone math. No algorithm
changes, only rendering (canvas heatmap for pheromone, colored dots for
ants, live stat panel). Confirmed visually what Phase 1 proved numerically:
pheromone trail lights up strongly through the short gap, stays dark
through the long one.

## Phase 3: FastAPI backend + WebSocket streaming

Moved the simulation off the browser entirely. The backend (FastAPI) now
owns the simulation loop and streams state to the browser every tick over
a WebSocket; the frontend was stripped down to a pure renderer with zero
simulation logic - it only draws whatever state it's told about.

**Observation, not a bug:** shortly after starting a run, the stats panel
can show ants visually carrying food (red dots) while "Trips completed"
still reads 0. This is an honest side effect of separating simulation
state from a single-instant snapshot - the visual state and the "trip
counted" state update on slightly different signals (position update vs.
arrival-at-nest check). It resolves itself within a few ticks and isn't a
correctness issue, but it's a small, real example of a distributed-systems
concept: the state you can observe and the state that's canonically true
aren't always perfectly in sync the instant something changes.

## Summary

The recurring theme across all three phases: most of the actual debugging
wasn't "the code has a typo" - it was "the rules produce plausible-looking
but wrong emergent behavior, and the fix is a better rule, not a bug fix."
That's the real difference between this and a CRUD project - correctness
here is about system dynamics, not just logic errors.