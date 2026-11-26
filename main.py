# Sports Tournament Ranking System
# Stores match results and team scores, calculates tournament points and tie-breakers
# (score difference, scores for, and head-to-head points), and produces final rankings.

DEFAULT_POLICY = {
    "win_points": 3,
    "draw_points": 1,
    "loss_points": 0,
}


def create_team_record(team_name):
    return {
        "team": team_name.strip().title(),
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "points": 0,
        "scored": 0,
        "conceded": 0,
        "score_diff": 0,
        "h2h_points": 0,
    }


def evaluate_tournament(teams, matches, policy=None):
    """
    teams: list of team names (str)
    matches: list of dicts, each with:
        - 'team_a': str
        - 'team_b': str
        - 'score_a': int
        - 'score_b': int
    policy: dict with 'win_points', 'draw_points', 'loss_points'
    """
    active_policy = DEFAULT_POLICY.copy()
    if policy:
        active_policy.update(policy)

    win_pts = active_policy["win_points"]
    draw_pts = active_policy["draw_points"]
    loss_pts = active_policy["loss_points"]

    standings = {}
    for name in teams:
        clean_name = name.strip().title()
        if not clean_name:
            raise ValueError("Team name cannot be empty.")
        if clean_name in standings:
            raise ValueError(f"Duplicate team name '{clean_name}'.")
        standings[clean_name] = create_team_record(clean_name)

    for idx, match in enumerate(matches, start=1):
        t_a = match["team_a"].strip().title()
        t_b = match["team_b"].strip().title()
        s_a = int(match["score_a"])
        s_b = int(match["score_b"])

        if t_a == t_b:
            raise ValueError(f"Match #{idx}: A team cannot play against itself ('{t_a}').")
        if t_a not in standings or t_b not in standings:
            raise ValueError(f"Match #{idx}: Unknown team in matchup '{t_a}' vs '{t_b}'.")
        if s_a < 0 or s_b < 0:
            raise ValueError(f"Match #{idx}: Scores cannot be negative.")

        rec_a = standings[t_a]
        rec_b = standings[t_b]

        rec_a["played"] += 1
        rec_b["played"] += 1
        rec_a["scored"] += s_a
        rec_a["conceded"] += s_b
        rec_b["scored"] += s_b
        rec_b["conceded"] += s_a

        if s_a > s_b:
            rec_a["wins"] += 1
            rec_b["losses"] += 1
            rec_a["points"] += win_pts
            rec_b["points"] += loss_pts
            rec_a["h2h_points"] += win_pts
            rec_b["h2h_points"] += loss_pts
        elif s_b > s_a:
            rec_b["wins"] += 1
            rec_a["losses"] += 1
            rec_b["points"] += win_pts
            rec_a["points"] += loss_pts
            rec_b["h2h_points"] += win_pts
            rec_a["h2h_points"] += loss_pts
        else:
            rec_a["draws"] += 1
            rec_b["draws"] += 1
            rec_a["points"] += draw_pts
            rec_b["points"] += draw_pts
            rec_a["h2h_points"] += draw_pts
            rec_b["h2h_points"] += draw_pts

    for rec in standings.values():
        rec["score_diff"] = rec["scored"] - rec["conceded"]

    # Sort by:
    # 1. Total tournament points (descending)
    # 2. Score difference (descending)
    # 3. Total scores for (descending)
    # 4. Head-to-head points (descending)
    # 5. Team name (ascending, deterministic fallback)
    ranked_teams = sorted(
        standings.values(),
        key=lambda r: (-r["points"], -r["score_diff"], -r["scored"], -r["h2h_points"], r["team"]),
    )

    for rank_pos, rec in enumerate(ranked_teams, start=1):
        rec["rank"] = rank_pos

    return ranked_teams


def print_standings(ranked_teams, policy):
    print("\n" + "=" * 84)
    print(
        f"TOURNAMENT STANDINGS (Policy: Win={policy['win_points']} | "
        f"Draw={policy['draw_points']} | Loss={policy['loss_points']})"
    )
    print("=" * 84)
    print(
        f"{'Rank':<4} | {'Team':<18} | {'P':>2} | {'W':>2} | {'D':>2} | {'L':>2} | "
        f"{'GF/PF':>5} | {'GA/PA':>5} | {'Diff':>5} | {'H2H':>3} | {'Pts':>4}"
    )
    print("-" * 84)

    for r in ranked_teams:
        print(
            f"{r['rank']:<4} | {r['team']:<18} | {r['played']:>2} | {r['wins']:>2} | "
            f"{r['draws']:>2} | {r['losses']:>2} | {r['scored']:>5} | {r['conceded']:>5} | "
            f"{r['score_diff']:>+5} | {r['h2h_points']:>3} | {r['points']:>4}"
        )
    print("=" * 84)


def main():
    print("Sports Tournament Ranking System")
    win_pts = int(input("Enter points for a Win (e.g., 3): ") or DEFAULT_POLICY["win_points"])
    draw_pts = int(input("Enter points for a Draw (e.g., 1): ") or DEFAULT_POLICY["draw_points"])
    loss_pts = int(input("Enter points for a Loss (e.g., 0): ") or DEFAULT_POLICY["loss_points"])
    policy = {"win_points": win_pts, "draw_points": draw_pts, "loss_points": loss_pts}

    num_teams = int(input("\nEnter number of participating teams: "))
    teams = []
    for i in range(1, num_teams + 1):
        t_name = input(f"  Enter Team #{i} name: ").strip()
        teams.append(t_name)

    num_matches = int(input("\nEnter number of completed matches: "))
    matches = []
    for i in range(1, num_matches + 1):
        print(f"\nMatch #{i}:")
        t_a = input("  Team A name: ").strip()
        t_b = input("  Team B name: ").strip()
        s_a = int(input(f"  {t_a.title()} score: "))
        s_b = int(input(f"  {t_b.title()} score: "))
        matches.append({"team_a": t_a, "team_b": t_b, "score_a": s_a, "score_b": s_b})

    try:
        ranked_teams = evaluate_tournament(teams=teams, matches=matches, policy=policy)
        print_standings(ranked_teams, policy)
    except ValueError as err:
        print(f"\nInput Error: {err}")


if __name__ == "__main__":
    main()
