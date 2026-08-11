Basic pheromone-following ants — broke because pheromone piled up near the nest
Fixed by having ants retrace their exact path home, rewarding shorter trips
Still too slow to find food — added a distance-based "instinct" alongside pheromone (real ACO combines both)
Colony got stuck reinforcing a mediocre lucky path (stagnation) — added elitist reinforcement so the best-ever path keeps getting topped up
Realized open space has too many equally-good paths to show real convergence — added a fork (short vs. long branch) matching the actual classic ant experiment
Result: clean, reliable convergence on the short path