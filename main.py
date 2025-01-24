from ortools.sat.python import cp_model

def solve_stickers_layout(
    stickers,
    max_layouts=5,
    layout_capacity=48,
    max_x_bound=100000,
    time_limit_sec=300
):
    """
    Solve the optimization problem where we have 'sticker_demands' that must be met or exceeded.
    We can define up to 'max_layouts' layouts (each with 'layout_capacity' spots),
    decide how many stickers of each type go into each layout, and print each layout some integer number of times.

    :param stickers: A list of (sticker_name, demand) tuples. Example: [(13, 29100), (16, 24300), ...]
    :param max_layouts: Maximum number of distinct layouts. (Default = 5)
    :param layout_capacity: Number of sticker spots in each layout. (Default = 48)
    :param max_x_bound: Upper bound for how many times each layout can be printed. (Default = 100000)
    :param time_limit_sec: Solver time limit in seconds. (Default = 300)
    :return: A dictionary with:
        - status: Solver status name (e.g., "OPTIMAL", "FEASIBLE")
        - used_layouts: List of layout indices actually used
        - layout_prints: Dict {layout_index -> number_of_times_printed}
        - total_pages: Sum of prints over all used layouts
        - layout_distributions: Dict {layout_index -> {sticker_name -> copies_per_page}}
        - demand_checks: Dict {sticker_name -> {"printed": int, "required": int, "met": bool}}
        - message: Optional, if no solution is found
    """

    # Separate sticker names and demands
    sticker_names = [s[0] for s in stickers]
    sticker_demands = [s[1] for s in stickers]
    N = len(sticker_names)

    # Create the CP-SAT model
    model = cp_model.CpModel()

    # We have max_layouts possible layouts
    layouts = range(max_layouts)

    # x[k] = number of times layout k is printed
    x = [model.NewIntVar(0, max_x_bound, f"x[{k}]") for k in layouts]

    # z[k] = boolean indicating if layout k is used
    z = [model.NewBoolVar(f"z[{k}]") for k in layouts]

    # y[k, i] = number of copies of sticker i in layout k (per single page)
    y = {}
    for k in layouts:
        for i in range(N):
            y[(k, i)] = model.NewIntVar(0, layout_capacity, f"y[{k},{i}]")

    # w[k, i] = total number of sticker i printed from layout k => x[k] * y[k, i]
    w = {}
    for k in layouts:
        for i in range(N):
            w[(k, i)] = model.NewIntVar(0, max_x_bound * layout_capacity, f"w[{k},{i}]")

    # 1) Link w[k, i] = x[k] * y[k, i]
    for k in layouts:
        for i in range(N):
            model.AddMultiplicationEquality(w[(k, i)], x[k], y[(k, i)])

    # 2) Layout capacity: sum of y[k, i] <= layout_capacity if z[k] = 1, else 0
    for k in layouts:
        model.Add(sum(y[(k, i)] for i in range(N)) <= layout_capacity).OnlyEnforceIf(z[k])
        model.Add(sum(y[(k, i)] for i in range(N)) == 0).OnlyEnforceIf(z[k].Not())

    # 3) Demand constraints: sum of w[k, i] >= sticker_demands[i]
    for i in range(N):
        model.Add(sum(w[(k, i)] for k in layouts) >= sticker_demands[i])

    # 4) At most max_layouts used
    model.Add(sum(z[k] for k in layouts) <= max_layouts)

    # 5) Each sticker must appear in at least one layout
    for i in range(N):
        model.Add(sum(y[(k, i)] for k in layouts) >= 1)

    # Objective: Minimize the sum of x[k]
    model.Minimize(sum(x[k] for k in layouts))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_sec

    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        used_layouts = [k for k in layouts if solver.Value(z[k]) == 1]
        total_pages = sum(solver.Value(x[k]) for k in used_layouts)

        # Build layout distributions
        layout_distributions = {}
        for k in used_layouts:
            single_layout = {}
            for i in range(N):
                copies_per_page = solver.Value(y[(k, i)])
                if copies_per_page > 0:
                    st_name = sticker_names[i]
                    single_layout[st_name] = copies_per_page
            layout_distributions[k] = single_layout

        # Demand checks for each sticker
        demand_checks = {}
        for i in range(N):
            name_i = sticker_names[i]
            required = sticker_demands[i]
            printed = sum(solver.Value(w[(k, i)]) for k in layouts)
            demand_checks[name_i] = {
                "printed": printed,
                "required": required,
                "met": (printed >= required)
            }

        return {
            "status": solver.StatusName(status),
            "used_layouts": used_layouts,
            "layout_prints": {k: solver.Value(x[k]) for k in used_layouts},
            "total_pages": total_pages,
            "layout_distributions": layout_distributions,
            "demand_checks": demand_checks,
        }
    else:
        return {
            "status": solver.StatusName(status),
            "message": "No feasible solution found or time limit reached."
        }


if __name__ == "__main__":
    # Example usage with a list of (sticker_name, demand) tuples
    stickers_example = [
        (13, 29100),
        (16, 24300),
        (19, 20100),
        (7, 17100),
        (11, 17000),
        (8, 16100),
        (22, 14800),
        (24, 14800),
        (4, 14100),
        (25, 13100),
        (3, 11900),
        (10, 10500),
        (17, 7600),
        (26, 7100),
        (30, 7100),
        (28, 5700),
        (2, 5300),
        (23, 5200),
        (6, 5100),
        (12, 5100),
        (5, 4600),
        (29, 4100),
        (21, 3600),
        (27, 3500),
        (9, 3100),
        (15, 2100),
        (14, 1600),
        (18, 1600),
        (20, 1100),
        (1, 600),
    ]

    result = solve_stickers_layout(stickers_example)

    print("Solver status:", result["status"])
    if "used_layouts" in result:
        print("Used layouts:", result["used_layouts"])
        print("Total pages (layouts printed):", result["total_pages"])

        # Layout distributions
        for k in result["used_layouts"]:
            count_prints = result["layout_prints"][k]
            dist = result["layout_distributions"][k]
            print(f"\nLayout {k}: printed {count_prints} times.")
            if dist:
                print("  Distribution (sticker_name -> copies_per_page):")
                for sticker, copies in dist.items():
                    print(f"    Sticker {sticker} => {copies}")

        print("\nDemand checks:")
        for sticker_name, info in result["demand_checks"].items():
            print(f"  Sticker {sticker_name}: printed={info['printed']}, "
                  f"required={info['required']}, met={info['met']}")
    else:
        print(result["message"])
