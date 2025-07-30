from constraint import Problem, AllDifferentConstraint
from itertools import groupby
import operator as op
from functools import partial

problem = Problem()

# define all (cell) values, grouped by attributes (columns)

realm = 'Avalon', 'Bryndor', 'Celestia', 'Dorne', 'Eldoria', 'Faeland', 'Galoria'
artifact = 'Amulet', 'Crystal', 'Mirror', 'Orb', 'Ring', 'Staff', 'Tome'
field = 'Alchemy', 'Divination', 'Elemental', 'Enchantment', 'Healing', 'Illusion', 'Necromancy'
familiar = 'Chimera', 'Dragon', 'Griffin', 'Pegasus', 'Phoenix', 'Salamander', 'Unicorn'

# Our approach makes each value (cell name) a constraint variable. The solution
# sets each variable to a valid realm. Here we use realm, but any of the
# attributes would work as the, "primary key".

all_vars = realm + artifact + field + familiar

problem.addVariables(all_vars, realm)

# attributes (columns) must contain unique values

problem.addConstraint( AllDifferentConstraint(), realm )
problem.addConstraint( AllDifferentConstraint(), artifact )
problem.addConstraint( AllDifferentConstraint(), field )
problem.addConstraint( AllDifferentConstraint(), familiar )

# Pin the realm values (first column)

for r in realm:
    problem.addConstraint( partial(op.eq, r), [r] )

# Create constraints for each clue (rule).
# Break up each clue into simple constraints.

# 1.  The wizard from Celestia studies Illusion magic and does not have the Amulet of Dreams.
problem.addConstraint( op.eq, ('Celestia', 'Illusion') )
problem.addConstraint( op.ne, ('Celestia', 'Amulet') )

# 2.  Eldoria's wizard holds the Orb of Shadows and is not versed in Necromancy or Alchemy.
problem.addConstraint( op.eq, ('Eldoria', 'Orb') )
problem.addConstraint( op.ne, ('Eldoria', 'Alchemy') )

# 3.  The wizard who owns the Crystal of Time has a Phoenix as a familiar and is not from Dorne or Galoria.
problem.addConstraint( op.eq, ('Crystal', 'Phoenix') )
problem.addConstraint( op.ne, ('Crystal', 'Dorne') )
problem.addConstraint( op.ne, ('Crystal', 'Galoria') )

# 4.  The Enchantment wizard is from Avalon and does not possess the Staff of Elements.
problem.addConstraint( op.eq, ('Enchantment', 'Avalon') )
problem.addConstraint( op.ne, ('Enchantment', 'Staff') )

# 5.  The wizard with the Griffin studies Healing magic
problem.addConstraint( op.eq, ('Griffin', 'Healing') )

# 6.  Faeland's wizard has the Ring of Realms but does not have a Salamander familiar.
problem.addConstraint( op.eq, ('Faeland', 'Ring') )
problem.addConstraint( op.ne, ('Faeland', 'Salamander') )

# 7.  The Necromancy wizard holds the Mirror of Truth and is not from Bryndor.
problem.addConstraint( op.eq, ('Necromancy', 'Mirror') )
problem.addConstraint( op.ne, ('Necromancy', 'Bryndor') )

# 8.  The wizard from Dorne has a Unicorn familiar and does not study Divination
problem.addConstraint( op.eq, ('Dorne', 'Unicorn') )
problem.addConstraint( op.ne, ('Dorne', 'Divination') )

# 9.  The Alchemy wizard is from Galoria and does not possess the Tome of Secrets.
problem.addConstraint( op.eq, ('Alchemy', 'Galoria') )
problem.addConstraint( op.ne, ('Alchemy', 'Tome') )

# 10. The wizard who studies Divination has a Salamander familiar.
problem.addConstraint( op.eq, ('Divination', 'Salamander') )

# 11. The Staff of Elements artifact is held by the wizard whose (familiar) is a Dragon.
problem.addConstraint( op.eq, ('Staff', 'Dragon') )

# 12. The wizard from Bryndor does not study Healing magic.
problem.addConstraint( op.ne, ('Bryndor', 'Healing') )

# 13. The wizard with the Pegasus familiar studies Elemental Magic.
problem.addConstraint( op.eq, ('Pegasus', 'Elemental') )

# 14. The Tome of Secrets is not held by the wizard from Avalon.
problem.addConstraint( op.ne, ('Tome', 'Avalon') )

# 15. The wizard who owns the Amulet of Dreams is from Bryndor.
problem.addConstraint( op.eq, ('Amulet', 'Bryndor') )


solutions = problem.getSolutions()


# Store solutions with cells accessable as [solution_index][row_index][col_index]
solution_tables = []

# extract solutions in table form

for solution in solutions:

    # sort by realm index (row), column index
    sorted_solution = sorted(
        [
            ( realm.index(r), all_vars.index(v)//len(realm), r, v )
            for v, r in list(solution.items())
        ]
    )

    solution_group = [
        list(g)
        for k, g in groupby(sorted_solution, lambda s: s[0])
    ]

    solution_table = [
        [value for row, col, realm, value in g ]
        for g in solution_group
    ]

    solution_tables += [solution_table]

# print solutions

solnum = 0

for solution_table in solution_tables:
    solnum += 1

    print(f"Solution: {solnum}")
    print()

    for solrow in solution_table:
        formatted_row = ' '.join( [c.ljust(11) for c in solrow] )
        print(formatted_row)

    print()

