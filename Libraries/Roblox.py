"""
# Roblox
Library to get certain Roblox resources.
"""

import requests

FALLBACK_PFP = "https://t5.rbxcdn.com/e4ba7dbfa08eb96193b65ac224ace948"

def getProfilePic(id:int):
    """
    Returns the given Roblox user's profile picture's URL or the `FALLBACK_PFP`
    """
    try:
        rq = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={str(id)}&size=720x720&format=Png&isCircular=false")
        data = rq.json()
        rq.close()
        if "data" in data:
            h = data.get("data")[0]
            if "imageUrl" in h:
                return h.get("imageUrl")
            else:
                raise RuntimeError()
        else:
            raise RuntimeError()
    except:
        return FALLBACK_PFP