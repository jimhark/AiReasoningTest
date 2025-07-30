# Solve Wizards Puzzle in pure Python (without using a solver library)
#
# Solution starts with a table of sets, uses logic rules to limit search space,
# then recursively searches remaining space, reapplying logic rules
# along the way.

import sys
import enum
from enum import Enum
import copy
import pprint

class Realm(Enum):
    AVALON = 0
    BRYNDOR = enum.auto()
    CELESTIA = enum.auto()
    DORNE = enum.auto()
    ELDORIA = enum.auto()
    FAELAND = enum.auto()
    GALORIA = enum.auto()

all_realms = frozenset( [e for e in Realm] )


class Artifact(Enum):
    AMULET = 0
    CRYSTAL = enum.auto()
    MIRROR = enum.auto()
    ORB = enum.auto()
    RING = enum.auto()
    STAFF = enum.auto()
    TOME = enum.auto()

all_artifacts = frozenset( [e for e in Artifact] )


class Field(Enum):
    ALCHEMY = 0
    DIVINATION = enum.auto()
    ELEMENTAL = enum.auto()
    ENCHANTMENT = enum.auto()
    HEALING = enum.auto()
    ILLUSION = enum.auto()
    NECROMANCY = enum.auto()

all_fields = frozenset( [e for e in Field] )


class Familiar(Enum):
    CHIMERA = 0
    DRAGON = enum.auto()
    GRIFFIN = enum.auto()
    PEGASUS = enum.auto()
    PHOENIX = enum.auto()
    SALAMANDER = enum.auto()
    UNICORN = enum.auto()

all_familiars = frozenset( [e for e in Familiar] )


class Catagory(Enum):
    REALM = 0
    ARTIFACT = enum.auto()
    FIELD = enum.auto()
    FAMILIAR = enum.auto()

module_vars = vars(sys.modules[__name__])

catagory_enum_lookup = {
    c.name: module_vars[c.name.capitalize()]
    for c in list(Catagory)
}


# get Category from enum member

def get_category(emember):
  emember_classname = emember.__class__.__name__
  category = Catagory[ emember_classname.upper() ]
  return category


# get state column index given enum member

def get_column(emember):
    cat = get_category(emember)
    icol = cat.value
    return icol


# put all enum element name abbreviations into one big dict

abbr_lookup = {
    'AVALON': 'A',
    'BRYNDOR': 'B',
    'CELESTIA': 'C',
    'DORNE': 'D',
    'ELDORIA': 'E',
    'FAELAND': 'F',
    'GALORIA': 'G',

    'AMULET': 'A',
    'CRYSTAL': 'C',
    'MIRROR': 'M',
    'ORB': 'O',
    'RING': 'R',
    'STAFF': 'S',
    'TOME': 'T',

    'ALCHEMY': 'A',
    'DIVINATION': 'D',
    'ELEMENTAL': 'L',   # 'LEMENTAL
    'ENCHANTMENT': 'E',
    'HEALING': 'H',
    'ILLUSION': 'I',
    'NECROMANCY': 'N',

    'CHIMERA': 'C',
    'DRAGON': 'D',
    'GRIFFIN': 'G',
    'PEGASUS': 'P',
    'PHOENIX': 'F',     # FOENIX
    'SALAMANDER': 'S',
    'UNICORN': 'U',

    'REALM': 'R',
    'ARTIFACT': 'A',
    'FIELD': 'F',
    'FAMILIAR': 'M',    # 'MILLIAR
}

# Get string representation of a set of enum members (emembers).
#
# verbose parameter:
#   True - use full name
#   False - use abbreviations for a short representation
#   'auto' = True if fromset is a single member set, else False
#
# Note: This function is overkill for final solution but useful for debugging

def get_set_str(fromset, verbose=False):
    if isinstance(verbose, str) and verbose.lower() == 'auto':
        verbose = (1 == len(fromset))

    element_names = [str(m).split('.')[1] for m in fromset]

    if verbose:
        separator = ', '
        prefix = ''
    else:
        separator = ''

        first_item = next(iter(fromset))
        classname = first_item.__class__.__name__
        short_classname = abbr_lookup[classname.upper()]
        prefix = short_classname + ':'

        element_names = [abbr_lookup[e] for e in element_names]

    set_str = prefix + separator.join( sorted(element_names) )

    return set_str


# Encode the rules from the definition of the problem. Provided clues can be
# in a more complex form requiring multiple (usually two, seperated by 'and')
# simple rules to represent.
#
# Note: The clues are not if A then B (implication), but A AND B (which commute).
#
# Note: Where clue says 'not' ('does not have', 'is not versed', etc.), we
# encode the set of remaining possible values (as if the clue was written
# 'does have one of {set}' , or 'is versed in one of {set}')

raw_rules = (

# 1.  The wizard from Celestia studies Illusion magic and does not have the Amulet of Dreams.
#       The wizard from "Celestia" (=realm) studies [AND] "Illusion magic" (=field)
#       The wizard from "Celestia" (=realm) does [AND] not have the "Amulet of Dreams" (!=artifact)

    ( Realm.CELESTIA, {Field.ILLUSION} ),
    ( Realm.CELESTIA, all_artifacts.difference(frozenset([Artifact.AMULET])) ),

# 2.  Eldoria's wizard holds the Orb of Shadows and is not versed in Necromancy or Alchemy.
#       "Eldoria's" (=realm) wizard holds [AND] the "Orb of Shadows" (=artifact)
#       "Eldoria's" (=realm) wizard is [AND] not versed in "Necromancy" or "Alchemy" (!=field)

    ( Realm.ELDORIA, {Artifact.ORB} ),
    ( Realm.ELDORIA, all_fields.difference(frozenset([Field.ALCHEMY])) ),

# 3.  The wizard who owns the Crystal of Time has a Phoenix as a familiar and is not from Dorne or Galoria.
#       The wizard who owns the "Crystal of Time" (=artifact) has [AND] a "Phoenix" (=familiar)
#       The wizard who owns the "Crystal of Time" (=artifact) is  [AND] not from "Dorne" or "Galoria" (!=realm)

    ( Artifact.CRYSTAL, {Familiar.PHOENIX} ),
    ( Artifact.CRYSTAL, all_realms.difference(frozenset([Realm.DORNE, Realm.GALORIA])) ),

# 4.  The Enchantment wizard is from Avalon and does not possess the Staff of Elements.
#       The "Enchantment" (=field) wizard is [AND] from "Avalon" (=realm)
#       The "Enchantment" (=field) wizard does [AND] not possess the "Staff of Elements" (!=artifact)

    ( Field.ENCHANTMENT, {Realm.AVALON} ),
    ( Field.ENCHANTMENT, all_artifacts.difference(frozenset([Artifact.STAFF])) ),

# 5.  The wizard with the Griffin studies Healing magic
#       The wizard with the "Griffin" (=familiar) studies [AND] "Healing magic" (=field)

    ( Familiar.GRIFFIN, {Field.HEALING} ),

# 6.  Faeland's wizard has the Ring of Realms but does not have a Salamander familiar.
#       "Faeland's" (realm) wizard has [AND] the "Ring of Realms" (artifact)
#       "Faeland's" (realm) wizard does [AND] not have a "Salamander" (!=familiar)

    ( Realm.FAELAND, {Artifact.RING} ),
    ( Realm.FAELAND, all_familiars.difference(frozenset([Familiar.SALAMANDER])) ),

# 7.  The Necromancy wizard holds the Mirror of Truth and is not from Bryndor.
#       The "Necromancy" (=field) wizard [AND] holds the "Mirror of Truth" (=artifact)
#       The "Necromancy" (=field) wizard is [AND] not from "Bryndor" (!=realm)

    ( Field.NECROMANCY, {Artifact.MIRROR} ),
    ( Field.NECROMANCY, all_realms.difference(frozenset([Realm.BRYNDOR])) ),

# 8.  The wizard from Dorne has a Unicorn familiar and does not study Divination
#       The wizard from "Dorne" (=realm) has [AND] a "Unicorn" (=familiar)
#       The wizard from "Dorne" (=realm) does [AND] not study "Divination" (!=field)

    ( Realm.DORNE, {Familiar.UNICORN} ),
    ( Realm.DORNE, all_realms.difference(frozenset([Field.DIVINATION])) ),

# 9.  The Alchemy wizard is from Galoria and does not possess the Tome of Secrets.
#       The "Alchemy" (=field) wizard is [AND] from "Galoria" (=realm)
#       The "Alchemy" (=field)  wizard does [AND] not possess the "Tome of Secrets" (!=artifact)

    ( Field.ALCHEMY, {Realm.GALORIA} ),
    ( Field.ALCHEMY, all_artifacts.difference(frozenset([Artifact.TOME])) ),

# 10. The wizard who studies Divination has a Salamander familiar.
#       The wizard who studies "Divination" (=field) has [AND] a "Salamander" (=familiar)

    ( Field.DIVINATION, {Familiar.SALAMANDER} ),

# 11. The Staff of Elements artifact is held by the wizard whose (familiar) is a Dragon.
#       The "Staff of Elements" (=artifact) is [AND] held by the wizard with a "Dragon" (=familiar)

    ( Artifact.STAFF, {Familiar.DRAGON} ),

# 12. The wizard from Bryndor does not study Healing magic.
#       The wizard from "Bryndor" (=realm) does [AND] not study "Healing magic" (!=field)

    ( Realm.BRYNDOR, all_fields.difference(frozenset([Field.HEALING])) ),

# 13. The wizard with the Pegasus familiar studies Elemental Magic.
#       The wizard with the "Pegasus" (=familiar) studies [AND] "Elemental Magic" (=field)

    ( Familiar.PEGASUS, {Field.ELEMENTAL} ),

# 14. The Tome of Secrets is not held by the wizard from Avalon.
#       The "Tome of Secrets" (=artifact) is [AND] not held by the wizard from "Avalon" (!=realm)

    ( Artifact.TOME, all_realms.difference(frozenset([Realm.AVALON])) ),

# 15. The wizard who owns the Amulet of Dreams is from Bryndor.
#       The wizard who owns the "Amulet of Dreams" (=artifact) is [AND] from "Bryndor" (=realm)

    ( Artifact.AMULET, {Realm.BRYNDOR} ),
)


# items in a rule are: rule_num, rule_match, rule_target

# The rule_num is only used to identify the rule.
# Number the rules starting at 1 because we negate rule numbers
# to indicate commutation (and -0 would be ambiguous).

rules = tuple(
    (rule_num+1, raw_rules[rule_num][0], raw_rules[rule_num][1])
    for rule_num in range(len(raw_rules))
)


# printing rules can be useful for debugging

def print_rules(rules):
    for rule in rules:
        rule_num, rule_match, rule_target = rule
        print( f"{rule_num}. {rule_match.name}: {get_set_str(rule_target, 'auto')}" )


# verify rules are followed, return list of broken rules

def check_rules(cur_state, rules):
    broken_rules = []

    for rule in rules:
        rule_num, rule_match, rule_target = rule
        rule_match_set = {rule_match}

        icol_match = get_column(rule_match)

        first_target_emember = next(iter(rule_target))
        icol_target = get_column(first_target_emember)

        matched_rows = [
            row
            for row in cur_state
            if not rule_match_set.isdisjoint(row[icol_match])
        ]

        candidate_target_rows = [
            row
            for row in matched_rows
            if not rule_target.isdisjoint(row[icol_target])
        ]

        if (not candidate_target_rows):
            broken_rules += [rule]
            pprint.pprint(f"BROKEN RULE: {rule_num}. Match: {repr(rule_match)}, Target: {repr(rule_target)}")

    return broken_rules


# For a catagory (column), where a value is a single set, the item in that set
# should be removed from other values (because items must be unique).

def eliminate_singles(cur_state, icol):
    elim_count = 0
    old_count = -1

    # Each iteration may create new singles, so loop until no changes.
    while old_count < elim_count:
        old_count = elim_count
        found_single = False
        for row in cur_state:
            if 1 == len(row[icol]):
                for r in cur_state:
                    if (
                        1 < len(r[icol])
                        and not r[icol].isdisjoint(row[icol])
                    ):
                        elim_count += 1
                        r[icol].difference_update(row[icol])

    return elim_count


# Implement the rule application. May be called multiple times for a single rule
# because if the target set is a single value, the rule is valid forward and
# backwards (due to commutation). When a rule is run commutated, negation is
# used to pass the rule_num as a negative number.

def apply_rule_base(cur_state, rule_num, rule_match, rule_target):
    rule_match_count = 0
    rule_match_set = {rule_match}
    icol_match = get_column(rule_match)

    first_target_emember = next(iter(rule_target))
    icol_target = get_column(first_target_emember)

    state_matched_rows = [s for s in cur_state if s[icol_match] == rule_match_set]

    if state_matched_rows:
        if len(state_matched_rows) != 1:
            raise ValueError(
                f"While processing rule {rule_num}, found multiple matching state rows."
            )

        # we know we have a list of exactly 1 item, pull that out now
        state_row = state_matched_rows[0]

        old_target_set = state_row[icol_target].copy()
        state_row[icol_target] = state_row[icol_target].intersection(rule_target)

        if old_target_set != state_row[icol_target]:
            rule_match_count += 1

            # The first column is different, it starts out as a single set. We
            # use this as a row identifier.

            rowid = repr(next(iter(state_row[0])))
            target_str = get_set_str(state_row[icol_target], verbose=True)
            print(f"Rule {rule_num} changed target state row {rowid}: {target_str}")

            # if new target set contains 1 object, remove that object from all
            # other rows

            _ = eliminate_singles(cur_state, icol_target)

    # apply the contrapositive (if not rule_target then not rule_match)

    # If state_row is a possible match (rule_match insersects state_row[icol_match])
    #   And rule_target is disjoint state_row[icol_target] (no actual match)
    #   Then remove rule_match from state_row[icol_match]

    state_matched_rows = [
        state_row for state_row in cur_state
        if 1 < len(state_row[icol_match])
            and not rule_match_set.isdisjoint(state_row[icol_match])
            and rule_target.isdisjoint(state_row[icol_target])
    ]

    for state_row in state_matched_rows:
        rule_match_count += 1

        state_row[icol_match].difference_update( rule_match_set )

        # The first column is different, it starts out with one value. We
        # use this as a row identifier.

        rowid = repr(next(iter(state_row[0])))
        match_str = get_set_str(state_row[icol_match], verbose=True)
        print(f"Rule {rule_num} changed match state row {rowid}: {match_str}")

        # if new match state set contains 1 object, remove that object
        # (state_row[icol_match]) from all other rows

        _ = eliminate_singles(cur_state, icol_match)

    return rule_match_count

# Apply rule and (if applicable) it's commuted version. Uses apply_rule_base
# for the actual work.

def apply_rule(cur_state, rule):
    rule_num, rule_match, rule_target = rule

    rule_match_count = apply_rule_base(
        cur_state,
        rule_num,
        rule_match,
        rule_target
    )


    # If the target is a single item, we match the rule commuted (with
    # match and target swapped).

    if 1 == len(rule_target):
        rule_match_count += apply_rule_base(
            cur_state,
            -rule_num,
            next(iter(rule_target)),
            {rule_match}
        )

    return rule_match_count


# Search state by applying rules iterativly then trying remaining possibilities
# recursively.

def search_state(cur_state, istart=0):
    solution_list = []

    dim0 = len(cur_state)
    imax = dim0 * len(cur_state[0])


    # apply rules iteratively until progress stops

    total_rule_match_count = 0
    old_count = -1

    while (old_count < total_rule_match_count):
        old_count = total_rule_match_count
        for r in rules:
            rule_match_count = apply_rule(cur_state, r)
            total_rule_match_count += rule_match_count

    # At this point the logic rules have been applied. We expect many
    # cells to be solved (contain a singleton set), but some unsolved
    # cells (multi sets) may remain. We iterate through the remaining
    # states by trying in turn each value remaining for the first multiset
    # found. This is done recursively.

    # find the first non-single

    found_nonsingle = False

    for icur in range(istart, imax):
        c, r = divmod(icur, dim0)
        found_nonsingle = 1 < len(cur_state[r][c])
        if found_nonsingle:
            break

    if found_nonsingle:
        trial_set = cur_state[r][c].copy()

        # Try each possibility in turn. This is a smart search:
        #
        #   * eliminate_singles is called to eliminate e from other rows
        #   * the recursive call applies rules to possibly limit search space

        for e in trial_set:
            trial_state = copy.deepcopy(cur_state)
            trial_state[r][c] = { e }
            eliminate_singles(trial_state, c)
            solution = search_state(trial_state, icur+1)

            solution_list += solution
    else:
        # No multi set found. This is a full solution

        # There should be no broken rules, unless there's a bug. Better check.

        broken_rules = check_rules(cur_state, rules)

        if broken_rules:
            print()
            pprint.pprint(broken_rules)
            print()
            print('--------------------------------------------------------------')
        else:
            solution_list += [ copy.deepcopy(cur_state) ]

    return solution_list


start_state = [
    [ {r}, set(all_artifacts), set(all_fields), set(all_familiars) ]
    for r in Realm
]

cur_state = copy.deepcopy(start_state)
istart = 0

solution_list = search_state(cur_state)

for solution in solution_list:
    pprint.pprint( [
        [get_set_str(c, 'auto').ljust(11) for c in r]
        for r in solution
    ] )


