import Grasshopper as ghc
import ghpythonlib.components as gh


"""

Description:
This script generates a parametric weaving pattern using:
- Alternating point deformation
- Curve smoothing (fillet)
- Tween interpolation along curves
- DataTree shifting and branch connection

"""


# -----------------------------------------------------------
# 1. GENERATE BASE CURVES
# -----------------------------------------------------------
def generate_curves(len_ln, height, array_num):
    """
    Generate a set of parallel base curves using a linear array.

    Parameters:
    len_ln (float): Length of the base curve
    height (float): Distance between curves (Z direction)
    array_num (int): Number of curves

    Returns:
    list: List of generated curves
    """
    line = gh.LineSDL(gh.ConstructPoint(12, 12, 0), gh.UnitX(1), len_ln)
    return gh.LinearArray(line, gh.UnitZ(height), array_num)[0]


crvs = generate_curves(len_ln, height, array_num)


# -----------------------------------------------------------
# 2. DIVIDE + DEFORM POINTS
# -----------------------------------------------------------
def move_points(crvs, array_num, div_count, amplitude, invert):
    """
    Divide curves and apply alternating deformation to points.

    Logic:
    - Even/odd curves have opposite deformation patterns
    - 'invert' flips the entire system globally

    Returns:
    DataTree: Deformed points organized by curve index {i}
    """
    new_pts = ghc.DataTree[object]()

    for i in range(array_num):
        path = ghc.Kernel.Data.GH_Path(i)

        # Divide curve into points
        division_pts = gh.DivideCurve(crvs[i], div_count, False)[0]

        # Determine alternating pattern per curve
        invert_row = (i % 2 != 0)

        # Global inversion switch
        if invert:
            invert_row = not invert_row

        for k in range(len(division_pts)):

            # Alternate movement per point index
            if invert_row:
                move_condition = (k % 2 != 0)
            else:
                move_condition = (k % 2 == 0)

            # Apply deformation
            if move_condition:
                new_pts.Add(gh.Move(division_pts[k], gh.UnitY(-amplitude))[0], path)
            else:
                new_pts.Add(division_pts[k], path)

    return new_pts


deformed_pts = move_points(crvs, array_num, div_count, amplitude, invert)


# -----------------------------------------------------------
# 3. BUILD FILLET CURVES
# -----------------------------------------------------------
def build_curves(deformed_pts, rad_fillet):
    """
    Create smooth curves from deformed points using polyline + fillet.

    Returns:
    DataTree: Fillet curves per branch {i}
    """
    f_crvs = ghc.DataTree[object]()

    for i in range(deformed_pts.BranchCount):
        path = deformed_pts.Path(i)

        # Build polyline and apply fillet

        f_crvs.Add(gh.FilletDistance(gh.PolyLine(deformed_pts.Branch(i), False), rad_fillet), path)

    return f_crvs


fillet_crvs = build_curves(deformed_pts, rad_fillet)


# -----------------------------------------------------------
# 4. GENERATE TWEEN POINTS
# -----------------------------------------------------------
def tween_points(fillet_crvs, deformed_pts, tween_factor):
    """
    Generate interpolated (tween) points along each curve.

    Process:
    - Project points onto curve
    - Interpolate between selected pairs
    - Store in {i;j} structure:
        i = curve index
        j = segment index

    Returns:
    DataTree: Tween points
    """
    tween_tree = ghc.DataTree[object]()

    for i in range(fillet_crvs.BranchCount):
        branch_pts = deformed_pts.Branch(i)

        # Each branch contains ONE curve → extract it
        branch_crv = fillet_crvs.Branch(i)[0]

        # Project points onto curve
        projected_pts = gh.PullPoint(branch_pts, branch_crv)[0]

        sub_ind = 0

        for j in range(len(projected_pts) - 1):

            # Use only alternating segments
            if j % 2 != 0:
                new_path = ghc.Kernel.Data.GH_Path(i, sub_ind)

                # Generate tween points
                tw_pts = gh.Pufferfish.TweenTwoPointsOnCurve(
                    projected_pts[j],
                    projected_pts[j + 1],
                    branch_crv,
                    tween_factor,
                    False
                )

                for pt in tw_pts:
                    tween_tree.Add(pt, new_path)

                sub_ind += 1

    return tween_tree


points = tween_points(fillet_crvs, deformed_pts, tween_factor)


# -----------------------------------------------------------
# 5. SHIFT DATA TREES
# -----------------------------------------------------------
def shift_tree(points):
    """
    Create two shifted trees:

    - Tree A → skips first branch
    - Tree B → skips last branch

    This creates an offset relationship used for weaving.

    Returns:
    tuple: (tree_A, tree_B)
    """
    max_first = max(points.Path(i)[0] for i in range(points.BranchCount))

    tr_A = ghc.DataTree[object]()
    tr_B = ghc.DataTree[object]()

    for i in range(points.BranchCount):
        path = points.Path(i)

        for item in points.Branch(i):

            # Remove first branch
            if path[0] != 0:
                tr_A.Add(item, path)

            # Remove last branch
            if path[0] != max_first:
                tr_B.Add(item, path)

    return tr_A, tr_B


shifted_trees = shift_tree(points)
tree_A = shifted_trees[0]
tree_B = shifted_trees[1]


# -----------------------------------------------------------
# 6. CONNECT BRANCHES (WEAVING LOGIC)
# -----------------------------------------------------------
def connect_branches(tree_A, tree_B):
    """
    Connect corresponding branches from two shifted trees.

    Logic:
    - Branch i in tree_B connects to branch i in tree_A
    - This creates the weaving pattern

    Returns:
    DataTree: Line connections
    """
    tw_lines = ghc.DataTree[object]()

    for i in range(tree_B.BranchCount):
        path = tree_B.Path(i)

        # Index-based alignment (trees are shifted)
        branch_A = tree_A.Branch(i)
        branch_B = tree_B.Branch(i)

        for j in range(min(len(branch_A), len(branch_B))):
            tw_lines.Add(gh.Line(branch_A[j], branch_B[j]), path)

    return tw_lines


tween_lines = connect_branches(tree_A, tree_B)
