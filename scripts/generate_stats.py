#!/usr/bin/env python3
"""Fetch real numbers from the GitHub GraphQL API and render assets/stats.svg.

Needs GITHUB_TOKEN. Standard library only. Never invents data: if the API
call fails the script exits non-zero and the existing SVG is left untouched.
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_assets import OUT, render_stats  # noqa: E402

LOGIN = os.environ.get("PROFILE_LOGIN", "Oussamabenhenia")
QUERY = """
query($login:String!){ user(login:$login){
  followers{totalCount}
  pullRequests{totalCount}
  contributionsCollection{contributionCalendar{totalContributions}}
  repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){
    totalCount
    nodes{languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}
  }}}"""


def main():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.load(r)["data"]["user"]
    langs = Counter()
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total = sum(langs.values()) or 1
    data = {
        "repos": u["repositories"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "prs": u["pullRequests"]["totalCount"],
        "commits": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "langs": [(n, 100 * b / total) for n, b in langs.most_common(6)],
        "updated": date.today().isoformat(),
    }
    (OUT / "stats.svg").write_text(render_stats(data), encoding="utf-8")


if __name__ == "__main__":
    main()
