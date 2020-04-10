# Snake-Game-and-Decision-Tree-based-Auto-play-Algorithm
Created in Python 3 using Pygame 1.9.6.
-----------------------------------------

Snake\Scores.txt automatically stores scores of every playing Snake, along with the timestamp, through a score_save() helper function in the code, any time the Game is Restarted(R) or Quit(Q).

Changeable in-game parameters:
1. Whether human plays or not.
2. Number of total Snakes. 
    Number of AI Snakes = Total Snakes - (Is Human playing)
3. Number of available food for Snakes.
4. Speed of the Game.

The implemented auto-play algorithm does not use any kind of Deep learning or Artificial Intelligence modelling.
It does not use any Search or traversal algorithms.

It is only implemented using if-else decision trees and performs satisfactorily, even when a large number of automated snakes are involved.


Scroll down to main() at the bottom of the Snake\Snake+Algo.py code for checking and changing game parameters.


-----------------------------------------------------------------------------------------------------------------------------------------------


Suggested commits:
1. Further improvements to the algorithm of the Snake (if possible, without implementing techniques like Learning)
2. Collision detection between snakes
3. Inclusion of traits like competitiveness, aggression to the automatic solving algorithm
