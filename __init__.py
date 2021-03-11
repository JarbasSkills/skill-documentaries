from ovos_utils.skills.templates.video_collection import VideoCollectionSkill
from mycroft.skills.core import intent_file_handler
from pyvod import Collection, Media
from os.path import join, dirname, basename
from ovos_utils.playback import CPSMatchType, CPSPlayback, CPSMatchConfidence


class DocumentariesSkill(VideoCollectionSkill):

    def __init__(self):
        super().__init__("Documentaries")
        self.message_namespace = basename(dirname(__file__)) + ".jarbasskills"
        # load video catalog
        path = join(dirname(__file__), "res", "Documentaries.jsondb")
        self.skill_logo = join(dirname(__file__), "ui",
                               "documentaries_icon.png")
        self.skill_icon = join(dirname(__file__), "ui",
                               "documentaries_icon.png")
        self.default_bg =  join(dirname(__file__), "ui",
                                "bg.jpeg")
        self.settings["match_description"] = True
        self.media_type = CPSMatchType.DOCUMENTARY
        self.playback_type = CPSPlayback.AUDIO
        self.media_collection = Collection("Documentaries",
                                           logo=self.skill_logo, db_path=path)
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.DOCUMENTARY,
                                CPSMatchType.VIDEO]

    def get_intro_message(self):
        self.speak_dialog("intro")

    @intent_file_handler('home.intent')
    def handle_homescreen_utterance(self, message):
        self.handle_homescreen(message)

    # matching
    def normalize_title(self, title):
        title = super(DocumentariesSkill, self).normalize_title(title)
        return self.remove_voc(title, "documentaries")

    def match_media_type(self, phrase, media_type):
        score = 0

        if self.voc_match(phrase, "video") or \
                media_type == CPSMatchType.VIDEO:
            score += 5

        if self.voc_match(phrase, "documentaries") or \
                media_type == CPSMatchType.DOCUMENTARY:
            score += 20

        if self.voc_match(phrase, "reddit"):
            score += 10

        return score


def create_skill():
    return DocumentariesSkill()
