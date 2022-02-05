from os.path import join, dirname

from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_utils.parse import fuzzy_match, MatchStrategy
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
from reddit_movies import RedditDocumentaries


class DocumentariesSkill(OVOSCommonPlaybackSkill):

    def __init__(self):
        super().__init__("Documentaries")
        self.skill_icon = join(dirname(__file__), "ui",
                               "documentaries_icon.png")
        self.media_type = MediaType.DOCUMENTARY
        self.playback_type = PlaybackType.VIDEO
        self.supported_media = [MediaType.DOCUMENTARY,
                                MediaType.VIDEO]
        self.reddit = RedditDocumentaries()

    def initialize(self):
        # get your own keys! these might stop working any time
        if "praw_client" not in self.settings:
            self.settings["praw_client"] = "Cij47m8Dg6dSIA"
        if "praw_secret" not in self.settings:
            self.settings["praw_secret"] = "7Hib7ujbWsrmzvgw93woBQ923w0"

        if self.settings.get("praw_secret") and \
                self.settings.get("praw_client"):
            self.reddit = RedditDocumentaries(
                client=self.settings["praw_client"],
                secret=self.settings["praw_secret"])

        self.schedule_event(self._scrap_reddit, 1)

    def _scrap_reddit(self, message=None):
        for v in self.reddit.scrap():
            pass  # TODO Some validation ?
        self.schedule_event(self._scrap_reddit, 3600)  # repeat every hour

    def calc_score(self, phrase, match, base_score=0):
        # check for forbidden words in title
        if self.voc_match(match["title"].lower(), "blacklist"):
            return 0

        score = 100 * fuzzy_match(phrase.lower(), match["title"].lower(),
                                  strategy=MatchStrategy.TOKEN_SET_RATIO)
        return min(100, base_score + score)

    def parse_media_type(self, phrase, media_type):
        score = 0
        if self.voc_match(phrase, "reddit"):
            score += 10
            phrase = self.remove_voc(phrase, "reddit")
        if self.voc_match(phrase, "documentaries") or \
                media_type == MediaType.DOCUMENTARY:
            if score:
                score += 25  # "reddit documentaries" -> near exact match
            score += 50
            phrase = self.remove_voc(phrase, "documentaries")
        return score, phrase

    @ocp_search()
    def search_reddit(self, phrase, media_type):
        base_score, phrase = self.parse_media_type(phrase, media_type)
        if base_score >= 50:
            yield {
                "match_confidence": base_score,
                "media_type": MediaType.DOCUMENTARY,
                "playlist": self.featured_media(),
                "playback": PlaybackType.VIDEO,
                "image": self.skill_icon,
                "bg_image": self.skill_icon,
                "skill_icon": self.skill_icon,
                "title": "r/Documentaries (Playlist)",
                "author": "r/Documentaries",
                "skill_id": self.skill_id
            }

        # search cached documentary database (updated hourly)
        for v in self.reddit.get_cached_entries():
            if media_type == MediaType.DOCUMENTARY:
                score = self.calc_score(phrase, v, base_score=base_score)
                if score < 50:
                    continue
                # return as a video result (single track dict)
                yield {
                    "match_confidence": score,
                    "media_type": MediaType.DOCUMENTARY,
                    #  "length": v.length * 1000,
                    "uri": "youtube//" + v["url"],
                    "playback": PlaybackType.VIDEO,
                    "image": v.get("thumbnail") or self.skill_icon,
                    "bg_image": v.get("thumbnail") or self.skill_icon,
                    "skill_icon": self.skill_icon,
                    "title": v["title"],
                    "skill_id": self.skill_id
                }

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "match_confidence": 50,
            "media_type": MediaType.DOCUMENTARY,
            #  "length": v.length * 1000,
            "uri": "youtube//" + v["url"],
            "playback": PlaybackType.VIDEO,
            "image": v.get("thumbnail") or self.skill_icon,
            "bg_image": v.get("thumbnail") or self.skill_icon,
            "skill_icon": self.skill_icon,
            "title": v["title"],
            "skill_id": self.skill_id
        } for v in self.reddit.get_cached_entries()]


def create_skill():
    return DocumentariesSkill()
