# Wall Builder

This program simulates a robot building a masonry wall with various brick bond types. 

Currently, three bond types are supported:
- [Stretcher](https://www.google.com/search?sca_esv=1c1ef98477ec0ce2&q=halfsteensverband&udm=2&fbs=AEQNm0Aa4sjWe7Rqy32pFwRj0UkWmMClnB87PLxnNpK0r9zS9VO4HmMmOoNtqAZhES3CuI9RtgmKa_v5BYxEtnDGPO3tEUj20XedYrYUG6z4T7drS2k4UCOaQyRECQlfYXtr01iUXO0uAyA0QbZxSQqYQfshoI5-M3bh5PQPrSSpr7bpsEwfTi8&sa=X&ved=2ahUKEwioodeshpCJAxUJgP0HHXsJAy4QtKgLegQIFRAB&biw=1439&bih=1282&dpr=1)
- [English cross bond](https://www.google.com/search?sca_esv=d620e9c68447bd3d&q=english+cross+bond&udm=2&fbs=AEQNm0Aa4sjWe7Rqy32pFwRj0UkWd8nbOJfsBGGB5IQQO6L3J7pRxUp2pI1mXV9fBsfh39KRvAkf_RbLmqO8b2Na6CPIBLMA2-hsroqVtXn5etlxxwf68tQxJ2N2uG9qHFf3SeDUe-Q9UTbzyXHp_UgmMIZPJedoOQbXjnExXFviOh_YBSq89Os&sa=X&ved=2ahUKEwjyi7TdgPCKAxWgywIHHUfuNxoQtKgLegQIGhAB&biw=1554&bih=1060&dpr=2)
- [Wild](https://www.joostdevree.nl/shtmls/wildverband.shtml)
  
  The wild bond has not yet been fully implemented, see _Bond assumptions_

## Running

To run:

    pip install -r requirements.txt
    streamlit run app.py

Streamlit should open in your browser, hosted locally.

It should look like this:

<img width="1544" alt="image" src="https://github.com/user-attachments/assets/f600e114-fe3a-49be-9024-b92380c79158" />

## Operating

At the left, in the sidebar you can select the **bond** type:

<img width="205" alt="image" src="https://github.com/user-attachments/assets/63b14730-e377-43b7-a084-650006cca590" />

You can start building by pressing either button: _lay bricks until next move_ or _lay next brick_.

The first button lays a full **stride** (a 'set' of bricks), which is defined by all the bricks the robot will lay before moving the frame in either the x or y direction. Press the button again to move the frame to the next position. 
The latter places bricks per piece. When the next best step is to move the frame, this button will move the frame as well.

You will get information on where the frame will move, and how many bricks can be built from that position.

There are some experimental options as well: changing the width and height of the wall. These are experimental since the program is not fully tested for other values than the default values. Furthermore, the building algorithm is based on the default wall height.

## Build optimalisation algorithm

The general algorithm logic consists of the following steps:

1. Build bricks until no possible options exist
2. 
   a. Check if condition for vertical movement is met  
   b. If condition is met, move frame vertically
3. Search x-space for next optimal configuration
4. Move frame to next optimal configuration

After building in the current position until no bricks can be placed, the algorithm simply searches through the possible x positions of the frame, and selects the position where the most bricks can be placed. 

Since we assume a frame of 2000 mm height, we know that there is only need for one vertical movement of the frame for building te wall. The algorithm moves the frame to the position at 750 mm if the following condition holds: the height of the bottommost **fully** built row is higher than 750 mm. This method, while not guaranteed optimal, saves costly searching of a 2D space.

For the algorithm we have the following assumptions:

- It is always beneficial to place bricks in one position until no longer possible
- One 'movement' is defined as the step between placing a brick in the current position and placing a brick in the next position (the act of movement is penalized, but not the size of the movement)
- Bricks must be fully supported on the whole length of the brick for it to be able to be placed
- Only bricks that are fully within the robot frame can be placed
- The frame cannot move diagonally
- The frame always starts in the left bottom corner

### Improvements

The algorithm is designed to be intuitive to understand and efficient to compute. However, there could be improvements to efficacy, trading off simplicity:

- _Penalize movement size_

  Now, only the act of movement is penalized. In a realistic setting, this becomes less optimal time-wise the larger the wall to be built. Therefore, I suggest to include the distance as well within the cost of movement. A possible way could be to base this cost on the time it takes to lay one brick versus the time it takes to move the frame a certain distance.
- _Planning horizon_
  
  The algorithm only considers the next best step. However, what the **best** step is could be dependent on future positions as well. For instance, if step a allows for building 15 bricks now but 5 in the position after, and step b allows for building 5 bricks now and 20 after, step b is the best option considering this planning horizon of 2 steps. An improvement to the algorithm could be to add such a planning horizon, which captures possible options as a consequence of a choice. This would be at a cost of computational complexity.
- _Include vertical movement in planning_
  
  To reduce the search space, only horizontal movement is considered up until a specific condition is met. This possibly produces suboptimal results, so an improvement could be to more dynamically search the vertical space as well.

## Bond assumptions (bonus)
For the bonus exercise, I looked into different bonds, which require different assumptions.
- _English cross bond_
  
  This bond alternates between rows of full length bricks and half length bricks. Therefore, we simply assume that we start with a row of full length bricks. Additionally, to fit the default wall format, we assume that we always start the row (seen from the last) with a half brick.
- __Wild bond__
  
  The wild bond is more challenging, as it introduces various constraints. This bond is not fully complete yet; I noticed that this bond introduces a 3/4 brick; due to time constraints I was unable to implement this, as it would need rewriting of a good part of the code. Therefore, I could not implement the staggering pattern, as this is not possible without the 3/4th brick.

  In the code, you can find the checks for vertical alignment and for consequent half bricks. When both conditions are applied, there appeared to be no valid outcome without using a 3/4th brick, therefore the vertical alignment check has been disabled for now.
  
  
