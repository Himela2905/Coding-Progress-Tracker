import requests

def fetch_leetcode_stats(username):
    """
    Fetch LeetCode stats for a given username using GraphQL.
    Returns a dictionary with total, easy, medium, hard solved counts.
    """
    if not username:
        return None

    url = "https://leetcode.com/graphql/"

    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """

    variables = {"username": username}

    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()

        ac_submissions = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]

        stats = {"total_solved": 0, "easy_solved": 0, "medium_solved": 0, "hard_solved": 0}

        for item in ac_submissions:
            diff = item["difficulty"]
            count = item["count"]
            stats["total_solved"] += count
            if diff == "Easy":
                stats["easy_solved"] = count
            elif diff == "Medium":
                stats["medium_solved"] = count
            elif diff == "Hard":
                stats["hard_solved"] = count

        return stats

    except Exception as e:
        print(f"Error fetching LeetCode stats: {e}")
        return None
