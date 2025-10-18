import os
import json

class ProgressManager:
    """
    Handles all user progress-related operations:
    - Load and save progress
    - Track LeetCode username
    - Manage per-user JSON files
    """

    def __init__(self, username: str):
        """
        Initialize a ProgressManager for a specific user.

        Args:
            username (str): User's email or unique ID
        """
        self.username = username
        self.file_path = f"data/{self._sanitize_filename(username)}_progress.json"
        os.makedirs("data", exist_ok=True)

    # ----------------------------
    # Filename safety
    # ----------------------------
    def _sanitize_filename(self, name: str) -> str:
        """Replace invalid filename characters to safely store JSON files."""
        return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)

    # ----------------------------
    # Load user data
    # ----------------------------
    def load_user_data(self) -> dict:
        """
        Load user progress data from JSON file.

        Returns:
            dict: User data dictionary, empty if file doesn't exist
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    else:
                        return {}
            except Exception:
                return {}
        return {}

    # Alias for backward compatibility
    load_progress = load_user_data
    get_progress = load_user_data

    # ----------------------------
    # Save user data
    # ----------------------------
    def save_user_data(self, data: dict = None):
        """
        Save user progress data to JSON file.

        Args:
            data (dict): Data to save. If None, saves an empty dict.
        """
        if not isinstance(data, dict):
            data = {}
        if data is None:
            data = {}
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # Alias for backward compatibility
    save_progress = save_user_data

    # ----------------------------
    # Get LeetCode username
    # ----------------------------
    def get_leetcode_username(self) -> str:
        """
        Retrieve stored LeetCode username for the user.

        Returns:
            str: LeetCode username or empty string if not set
        """
        data = self.load_user_data()
        return data.get("leetcode_username", "")

    # ----------------------------
    # Set LeetCode username
    # ----------------------------
    def set_leetcode_username(self, lc_username: str):
        """
        Save or update user's LeetCode username.

        Args:
            lc_username (str): LeetCode username
        """
        data = self.load_user_data()
        if not isinstance(data, dict):
            data = {}
        data["leetcode_username"] = lc_username
        self.save_user_data(data)

    # ----------------------------
    # Reset specific topic
    # ----------------------------
    def reset_topic(self, topic_name: str):
        """
        Delete a specific topic from user's progress.

        Args:
            topic_name (str): Topic key to remove
        """
        data = self.load_user_data()
        if topic_name in data and topic_name != "leetcode_username":
            del data[topic_name]
            self.save_user_data(data)

    # ----------------------------
    # Reset all progress
    # ----------------------------
    def reset_all_progress(self):
        """
        Remove all user progress (keeps file, empties content)
        """
        self.save_user_data({})

    # ----------------------------
    # Add or update a topic
    # ----------------------------
    def add_or_update_topic(self, topic_name: str, completion: int = 0, accuracy: float = None):
        """
        Add a new topic or update existing topic progress.

        Args:
            topic_name (str): Topic name
            completion (int): Completion percentage (0–100)
            accuracy (float): Optional accuracy percentage
        """
        data = self.load_user_data()
        if not isinstance(data, dict):
            data = {}
        completion = max(0, min(100, completion))
        data[topic_name] = {
            "completion": completion,
            "accuracy": accuracy if accuracy is not None else 0,
            "completed": completion == 100
        }
        self.save_user_data(data)
