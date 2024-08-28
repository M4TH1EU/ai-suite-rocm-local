import json
import urllib

from main import ROCM_VERSION, logger


def get_prebuilts(repo_owner: str = "M4TH1EU", repo_name: str = "ai-suite-rocm-local",
                  release_tag: str = f"prebuilt-whl-{ROCM_VERSION}") -> list:

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_tag}"

    try:
        with urllib.request.urlopen(api_url) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch data: HTTP Status {response.status}")
                return []

            release_data = json.load(response)

            assets = release_data.get('assets', [])
            if not assets:
                logger.error("No assets found in release data")
                return []

            return assets

    except urllib.error.URLError as e:
        logger.error(f"Error fetching release data: {e}")
