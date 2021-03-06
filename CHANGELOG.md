# Changelog

I didn't start versioning until late in the project, so the version numbers
starting with '0.0.0' are just a reference.

This project adheres to [Semantic Versioning](http://semver.org/).

## 0.6.1 - 2015-09-16
### Added
- Usage examples.
- More documentation.
### Changed
- Some refactoring in general.

## 0.6.0a - 2015-08-12
### Changed
- Refactoring.

### Removed
- A lot of unused code. Mostly old algorithms and ideas for algorithms.

## 0.6.0 - 2015-08-10
### Changed
- Some changes.

## 0.5.0 - 2015-06-29
### Changed
- New causal learning algorithm.

## 0.4.0 - 2015-06-10
### Changed
- Some implementation of the causal learning algorithm.
- Small changes related to layout etc.

## 0.3.0 - 2015-06-03
### Added
- Functionality to change how the entities are connected.
- A way to run multiple simulations in succession.

## 0.2.0 - 2015-05-27
### Added
- RouletteWheelSelection algorithm for SimpleController action selection.
- Mobile with direction.
- Functionality to change whether the infant is connected to the mobile.

### Changed
- Separate count updating and action selection from LearningRule into ActionSelection.
- Make visualization of operant conditioning more general (multiple reinforcers).
- Internal representation of Graph and usage of it in the causal learning algorithm (more efficient).

### Fixed
- Fix mix-up of demerit(r, 0) and merit(r, 0) definitions.

## 0.1.0 - 2015-05-25
### Added
- More SimpleController-related documentation.
- Rows Visualization so that it is easier to see what's going on.
- More controls for the PyGame simulator.
  + Increase/decrease simulation speed.

### Changed
- Simplified action selection for SimpleController.
- Removed decrementing other actions in BetterLearningRule.
- Implement the last step of the OperantConditioningController's predictor deletion and update some documentation.
- Simplify PyGame simulation loop.

## 0.0.1 - 2015-05-25
### Added
- Controls for the PyGame-based simulator to step through the simulation.
- Visualizations for Entities and Controllers.
 + Sliders for the infant's limbs.
 + An expanding circle for the mobile's velocity.
- Started versioning and adopting "git-flow".
- This Changelog.

### Fixed
- Many bugfixes.

## 0.0.0e - 2015-05-06
### Changed
- Rewrite and debug several implementations including the `graph` and `probability` utilities.

## 0.0.0d - 2015-05-05
### Added
- A basic OperantConditioningAgent.

## 0.0.0c - 2015-05-03
### Added
- A basic RandomAgent.
- A basic CausalLearningAgent.

## 0.0.0b - 2015-05-01
### Added
- A basic World functionality.
- A basic Agent functionality.
- A basic Entity functionality.

## 0.0.0a - 2015-04-17
### Added
- Basic architecture outline, no real functionality yet.
