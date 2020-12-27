from ovos_utils.waiting_for_mycroft.common_play import CPSMatchType
from ovos_utils.skills.templates.media_collection import MediaCollectionSkill
from mycroft.skills.core import intent_file_handler
from mycroft.util.parse import fuzzy_match, match_one
from pyvod import Collection, Media
from os.path import join, dirname, basename
import random
from json_database import JsonStorageXDG
import datetime


class DocumentariesSkill(MediaCollectionSkill):

    def __init__(self):
        super().__init__("Documentaries")
        self.message_namespace = basename(dirname(__file__)) + ".jarbasskills"
        # load video catalog
        path = join(dirname(__file__), "res", "Documentaries.jsondb")
        logo = join(dirname(__file__), "res", "documentaries_logo.png"),
        self.media_collection = Collection("Documentaries", logo=logo, db_path=path)

    def get_intro_message(self):
        self.speak_dialog("intro")

    @intent_file_handler('documentarieshome.intent')
    def handle_homescreen_utterance(self, message):
        self.handle_homescreen(message)

    # matching
    def match_media_type(self, phrase, media_type):
        match = None
        score = 0

        if self.voc_match(phrase, "video") or media_type == \
                CPSMatchType.VIDEO:
            score += 0.05
            match = CPSMatchLevel.GENERIC

        if self.voc_match(phrase, "documentaries"):
            score += 0.3
            match = CPSMatchLevel.TITLE

        return match, score

    def calc_final_score(self, phrase, base_score, match_level):
        score = base_score
        if self.voc_match(phrase, "documentaries"):
            score += 0.5
        return score


def create_skill():
    return DocumentariesSkill()
