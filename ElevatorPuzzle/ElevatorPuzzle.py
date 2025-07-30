#!/usr/bin/env python3

import typing
from abc import ABC, abstractmethod

STARTING_FLOOR: int = 0
MAX_FLOOR: int = 30
TARGET_FLOOR: int = MAX_FLOOR

class Elevator:
    def __init__(self, floor: int = 0) -> None:
        self.set_floor(floor)

    def set_floor(self, floor: int) -> None:
        self.floor = floor

    def get_floor(self) -> int:
        return self.floor

    def clone(self) -> typing.Self:
        elevator = Elevator( self.get_floor() )
        return elevator

class Action(ABC):
    # set of all primes less than 100
    primes100: set[int] = {
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
        71, 73, 79, 83, 89, 97
    }

    @abstractmethod
    def __init__(self) -> None:
        self._name: typing.Optional[str] = None

    def get_name(self):
        name = self._name
        return name

    def Activate(self, elevator: Elevator) -> None:
        okay = self._pre_check(elevator)

        if (okay):
            self._push_button(elevator)
            self._post_process


    def _pre_check(self, elevator: Elevator) -> bool:
        # Trap Floor 13: You cannot press any button other than Button D.
        okay: bool = elevator.floor != 13 or self.get_name() == 'D'

        return okay


    def _post_process(self, elevator: Elevator) -> None:
        # Trap Floor 22: You are forced to go back to Floor 10.

        floor: int = elevator.get_floor()

        if (22 == floor):
            floor = 10
            elevator.set_floor(floor)

    @abstractmethod
    def _push_button(self, elevator: Elevator):
        pass


class AButtonAction(Action):
    def __init__(self) -> None:
        self._name: typing.Optional[str] = 'A'

    def _push_button(self, elevator: Elevator) -> None:
        # Moves you up n+1 floors, where n is the current floor number.
        # If this action lands you on a floor divisible by 5, the elevator
        # sends you back to n/2.

        floor = elevator.get_floor()
        floor = floor + floor + 1

        if floor <= MAX_FLOOR:
            if 0 == floor % 5:
                floor //= 2

            elevator.set_floor(floor)


class BButtonAction(Action):
    def __init__(self) -> None:
        self._name: typing.Optional[str] = 'B'

    def _push_button(self, elevator: Elevator) -> None:
        # Moves you up 4 floors but subtracts 3 from the new floor if the
        # resulting floor is even.

        floor = elevator.get_floor()
        floor += 4

        if floor <= MAX_FLOOR:
            if 0 == floor % 2:
                floor -= 3

            elevator.set_floor(floor)


class CButtonAction(Action):
    def __init__(self) -> None:
        self._name: typing.Optional[str] = 'C'

    def _push_button(self, elevator: Elevator) -> None:
        # Moves you down 7 floors, but if the floor you land on is a prime
        # number, you immediately bounce back up 10 floors.

        floor = elevator.get_floor()

        floor -= 7

        if 0 <= floor:
            if floor in Action.primes100:
                floor += 10

            if floor <= MAX_FLOOR:
                elevator.set_floor(floor)


class DButtonAction(Action):
    def __init__(self) -> None:
        self._name: typing.Optional[str] = 'D'

    def _push_button(self, elevator: Elevator) -> None:
        # Moves you to the next floor that is a multiple of 3 (always up).

        floor = elevator.get_floor()
        floor = floor + 3 - (floor % 3)

        if floor <= MAX_FLOOR:
            elevator.set_floor(floor)


class EButtonAction(Action):
    def __init__(self) -> None:
        self._name: typing.Optional[str] = 'E'

    def _push_button(self, elevator: Elevator) -> None:
        # Moves you up 2 floors and doubles the number of floors moved if
        # the current floor number is odd.

        floor = elevator.get_floor()

        floor += 2

        if floor <= MAX_FLOOR:
            if (1 == floor%2 and floor + 2 <= MAX_FLOOR):
                floor += 2

            elevator.set_floor(floor)


button_actions: tuple[Action] = (
    AButtonAction(),
    BButtonAction(),
    CButtonAction(),
    DButtonAction(),
    EButtonAction()
)

class ElevatorAction:
    def __init__(self, elevator: Elevator) -> None:
        self.elevator = elevator.clone()

    def press_button(self, button_action: Action) -> int:
        button_action.Activate(self.elevator)
        floor = self.get_floor()
        return floor

    def get_floor(self) -> int:
        floor = self.elevator.get_floor()
        return floor

    def clone(self) -> typing.Self:
        elevator_action = ElevatorAction( self.elevator.clone() )
        return elevator_action


# set of floors we've seen
seen_floors: set[int] = { 0 }

# Above we've implemented reasonable state representation and transitions.
# We need to implement a Breath first Search that tracks uses seen_floors.

# The total search space is 5^6 = 15,625 (we happen to know the shortest
# path is 6 buttons).


#  Build the elevator move table using a depth first search.

class ElevatorMove(typing.NamedTuple):
    step: int           # how many buttons have been pressed
    start_floor: int
    action_sequence: str         # Action name, 'A'-'F' or 'S' for start.
    end_floor: int


elevator_move_table: typing.List[ElevatorMove] = [
    ElevatorMove(0, 0, '', 0)
]

def search_elevator_paths(move_elevator_start: ElevatorMove):
    elevator_action_start = ElevatorAction(
        Elevator(move_elevator_start.end_floor)
    )

    next_moves: typing.List[ElevatorMove] = []

    for button_action in button_actions:
        cur_elevator_action = elevator_action_start.clone()

        floor = cur_elevator_action.press_button(button_action)

        elevator_move = ElevatorMove(
            move_elevator_start.step + 1,
            move_elevator_start.end_floor,
            move_elevator_start.action_sequence + button_action.get_name(),
            floor
        )

        if (floor not in seen_floors):
            seen_floors.add(floor)
            elevator_move_table.append( elevator_move )
            next_moves.append( elevator_move )

            print(f'new: {elevator_move}')

        else:
            print( f'  old: {elevator_move}' )

        if floor == TARGET_FLOOR:
            print( f'Hit target in {elevator_move.step} steps' )
            break

    fcontinue = floor != TARGET_FLOOR

    # TODO: make this iterate instead of recurse.

    if (fcontinue):
        for move in next_moves:
            fcontinue = search_elevator_paths( move )
            if not fcontinue:
                break

    return fcontinue

fcontinue = search_elevator_paths( elevator_move_table[0] )

# elevator_move_table

# elevator_move_table is ordered and the last entry ends on the target

solution_sequence = elevator_move_table[-1].action_sequence

sol_seq_set = set(
    [solution_sequence[:i+1] for i in range(len(solution_sequence))]
)

solution_moves = [
    e for e in elevator_move_table if
    e.action_sequence in sol_seq_set
]

for sm in solution_moves:
    print(
        f'{sm.step}. {sm.start_floor:02} -- '
        f'{sm.action_sequence[-1]} --> {sm.end_floor:02}'
    )


