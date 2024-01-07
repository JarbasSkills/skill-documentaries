from os.path import join, dirname

from reddit_movies import RedditMovies

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


from reddit_movies import RedditDocumentaries


class DocumentariesSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.DOCUMENTARY]
        self.skill_icon = join(dirname(__file__), "ui",
                               "documentaries_icon.png")
        super().__init__(*args, **kwargs)

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

        self._scrap_reddit()
        self.register_ocp_keyword(MediaType.DOCUMENTARY,
                                  "documentary_streaming_provider",
                                  ["Reddit Documentaries", "Reddit"])

    def _scrap_reddit(self, message=None):
        movies = []
        for v in self.reddit.get_cached_entries():
            t = v["title"].split(" (")[0].replace("COMPLETE", "")
            if '"' in t:
                t = t.split('"')[1]
            movies.append(t.strip())
        try:
            for v in self.reddit.scrap():
                print(v)
                t = v["title"].split(" (")[0].replace("COMPLETE", "")
                if '"' in t:
                    t = t.split('"')[1]
                movies.append(t.strip())
        except:
            pass
        self.register_ocp_keyword(MediaType.DOCUMENTARY,
                                  "documentary_name", movies)
        self.schedule_event(self._scrap_reddit, 3600)  # repeat every hour

    @ocp_search()
    def search_reddit(self, phrase, media_type):
        base_score = 15 if media_type == MediaType.DOCUMENTARY else 0
        entities = self.ocp_voc_match(phrase)

        title = entities.get("documentary_name")
        skill = "documentary_streaming_provider" in entities  # skill matched

        base_score += 30 * len(entities)
        if title:
            base_score += 30
            # search cached database (updated hourly)
            for v in self.reddit.get_cached_entries():
                if title.lower() in v["title"].lower():
                    # return as a video result (single track dict)
                    yield {
                        "match_confidence": base_score,
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
        if skill:
            yield self.get_playlist()

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.DOCUMENTARY,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "Reddit Documentaries (Documentary Playlist)",
            "author": "Reddit"
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


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = DocumentariesSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_reddit("Vatican City", MediaType.DOCUMENTARY):
        print(r)
        # {'match_confidence': 75, 'media_type': <MediaType.DOCUMENTARY: 15>, 'uri': 'youtube//https://www.youtube.com/watch?v=gwrKLL4Gefg', 'playback': <PlaybackType.VIDEO: 1>, 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'bg_image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'title': 'Vatican City', 'skill_id': 't.fake'}

