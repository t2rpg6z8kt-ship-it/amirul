"""Utilities for representing and transforming square occupancy grids.

This module defines :class:`Grid`, a class that models an ``n x n`` grid in
which each block is either vacant or occupied.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

Coord = Tuple[int, int]


class Grid:
    """Represent an ``n x n`` grid of occupied/vacant blocks.

    Attributes:
        _n: Dimension of the square grid.
        _occupancies: List of occupied coordinates ``(x, y)``.
        _rows: Nested list storing occupancy booleans by row and column.
    """

    def __init__(self, n: int, occupancies: Iterable[Coord]):
        """Create a grid from a dimension and occupied coordinates.

        Args:
            n: Size of the grid (must be a positive integer).
            occupancies: Iterable of coordinate tuples ``(x, y)``.

        Raises:
            TypeError: If inputs are not of the expected data types.
            ValueError: If ``n`` is invalid or coordinates are out of range.
        """
        if not isinstance(n, int):
            raise TypeError("n must be an integer")
        if n <= 0:
            raise ValueError("n must be positive")

        validated: List[Coord] = []
        seen = set()
        for coord in occupancies:
            if not (isinstance(coord, tuple) and len(coord) == 2):
                raise TypeError("each occupancy must be a tuple of length 2")
            x, y = coord
            if not (isinstance(x, int) and isinstance(y, int)):
                raise TypeError("occupancy coordinates must be integers")
            if not (0 <= x < n and 0 <= y < n):
                raise ValueError("occupancy coordinates must be within grid bounds")
            if coord not in seen:
                seen.add(coord)
                validated.append(coord)

        self._n = n
        self._occupancies = validated
        self._rows = [[False for _ in range(self._n)] for _ in range(self._n)]
        for row, col in self._occupancies:
            self._rows[row][col] = True

    def __repr__(self) -> str:
        """Return an executable representation of the instance."""
        return f"Grid(n={self._n}, occupancies={self._occupancies})"

    def __str__(self) -> str:
        """Return a human-readable grid using occupied/vacant block symbols."""
        return "\n".join(
            " ".join("■" if occupied else "□" for occupied in row) for row in self._rows
        )

    def get_occupancies(self) -> List[Coord]:
        """Return a copy of occupied coordinates.

        Returns:
            A new list containing the occupied coordinate tuples.
        """
        return self._occupancies.copy()

    def get_row(self, i: int) -> List[bool]:
        """Return a copy of row ``i`` from the internal occupancy table.

        Args:
            i: Zero-based row index.

        Returns:
            A new list of booleans for row ``i``.

        Raises:
            TypeError: If ``i`` is not an integer.
            IndexError: If ``i`` is outside the grid range.
        """
        if not isinstance(i, int):
            raise TypeError("row index i must be an integer")
        if not (0 <= i < self._n):
            raise IndexError("row index out of range")
        return self._rows[i].copy()

    def add_occupancy(self, coords: Coord) -> None:
        """Mark a block as occupied if it is currently vacant.

        Args:
            coords: Coordinate tuple ``(x, y)``.

        Raises:
            TypeError: If ``coords`` is not a tuple of two integers.
            ValueError: If coordinates are outside the grid bounds.
        """
        x, y = self._validate_coords(coords)
        if not self._rows[x][y]:
            self._rows[x][y] = True
            self._occupancies.append((x, y))

    def del_occupancy(self, coords: Coord) -> None:
        """Mark a block as vacant if it is currently occupied.

        Args:
            coords: Coordinate tuple ``(x, y)``.

        Raises:
            TypeError: If ``coords`` is not a tuple of two integers.
            ValueError: If coordinates are outside the grid bounds.
        """
        x, y = self._validate_coords(coords)
        if self._rows[x][y]:
            self._rows[x][y] = False
            self._occupancies.remove((x, y))

    def copy(self) -> "Grid":
        """Return a deep copy of the current grid.

        Returns:
            A new :class:`Grid` with matching values and independent storage.
        """
        return Grid(self._n, self._occupancies.copy())

    def v_reflected(self) -> "Grid":
        """Return the vertical reflection (mirror left-right) of the grid."""
        reflected = [(x, self._n - 1 - y) for x, y in self._occupancies]
        return Grid(self._n, reflected)

    def h_reflected(self) -> "Grid":
        """Return the horizontal reflection (mirror top-bottom) of the grid."""
        reflected = [(self._n - 1 - x, y) for x, y in self._occupancies]
        return Grid(self._n, reflected)

    def rotated(self) -> "Grid":
        """Return a clockwise rotation of the grid by 90 degrees."""
        rotated_coords = [(y, self._n - 1 - x) for x, y in self._occupancies]
        return Grid(self._n, rotated_coords)

    def __add__(self, h: object):
        """Return the XOR-style sum of two grids of the same dimensions.

        If dimensions differ, prints the required coursework message and returns
        ``None``.
        """
        if not isinstance(h, Grid):
            return NotImplemented
        if self._n != h._n:
            print("Error: Grids must be of matching size")
            return None

        self_set = set(self._occupancies)
        h_set = set(h._occupancies)
        return Grid(self._n, list(self_set.symmetric_difference(h_set)))

    def __eq__(self, h: object) -> bool:
        """Check equality of occupancy patterns between two grids."""
        if not isinstance(h, Grid):
            return NotImplemented
        if self._n != h._n:
            return False
        return self._rows == h._rows

    def __le__(self, h: object) -> bool:
        """Check whether every occupied block of ``self`` is also in ``h``."""
        if not isinstance(h, Grid):
            return NotImplemented
        if self._n != h._n:
            return False
        return set(self._occupancies).issubset(h._occupancies)

    def __ge__(self, h: object) -> bool:
        """Check whether every occupied block of ``h`` is also in ``self``."""
        if not isinstance(h, Grid):
            return NotImplemented
        if self._n != h._n:
            return False
        return set(h._occupancies).issubset(self._occupancies)

    def _validate_coords(self, coords: Sequence[int]) -> Coord:
        """Validate and normalize an input coordinate pair.

        Args:
            coords: Candidate coordinate pair.

        Returns:
            A validated coordinate tuple ``(x, y)``.

        Raises:
            TypeError: If format or types are invalid.
            ValueError: If coordinates are out of bounds.
        """
        if not (isinstance(coords, tuple) and len(coords) == 2):
            raise TypeError("coords must be a tuple of length 2")
        x, y = coords
        if not (isinstance(x, int) and isinstance(y, int)):
            raise TypeError("coordinate values must be integers")
        if not (0 <= x < self._n and 0 <= y < self._n):
            raise ValueError("coordinate values must be within grid bounds")
        return x, y


if __name__ == "__main__":
    example = Grid(
        n=3,
        occupancies=[(0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (2, 2)],
    )

    print(example)
    print()
    print(example.v_reflected())
    print()
    print(example.rotated())
