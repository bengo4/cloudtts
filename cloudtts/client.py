from enum import Enum, auto


class CloudTTSError(Exception):
    pass


class AudioFormat(Enum):
    mp3 = auto()         # Azure / Google / Polly / Watson
    ogg_opus = auto()    # Google / Watson
    ogg_vorbis = auto()  # Polly / Watson
    pcm = auto()         # Azure / Polly


class Gender(Enum):
    male = 'male'
    female = 'female'


class Language(Enum):
    da_DK = 'da-DK'  # Azure / Polly
    de_DE = 'de-DE'  # Azure / Google / Polly / Watson
    en_AU = 'en-AU'  # Azure / Google / Polly
    en_GB = 'en-GB'  # Azure / Google / Polly / Watson
    en_IN = 'en-IN'  # Azure / Polly
    en_US = 'en-US'  # Azure / Google / Polly / Watson
    es_ES = 'es-ES'  # Azure / Google / Polly / Watson
    es_US = 'es-US'  # Polly / Watson
    fr_CA = 'fr-CA'  # Azure / Google / Polly
    fr_FR = 'fr-FR'  # Azure / Google / Polly / Watson
    hi_IN = 'hi-IN'  # Azure / Polly
    it_IT = 'it-IT'  # Azure / Google / Polly / Watson
    ja_JP = 'ja-JP'  # Azure / Google / Polly / Watson
    ko_KR = 'ko-KR'  # Azure / Google / Polly
    nb_NO = 'nb-NO'  # Azure / Polly
    nl_NL = 'nl-NL'  # Azure / Google / Polly
    pl_PL = 'pl-PL'  # Azure / Polly
    pt_BR = 'pt-BR'  # Azure / Google / Polly / Watson
    pt_PT = 'pt-PT'  # Azure / Polly
    ro_RO = 'ro-RO'  # Azure / Polly
    ru_RU = 'ru-RU'  # Azure / Polly
    sv_SE = 'sv-SE'  # Azure / Google / Polly
    tr_TR = 'tr-TR'  # Azure / Google / Polly


class VoiceConfig:
    def __init__(self, audio_format=AudioFormat.mp3, gender=Gender.female,
                 language=Language.en_US):
        if isinstance(audio_format, AudioFormat):
            self.audio_format = audio_format
        else:
            raise TypeError

        if isinstance(gender, Gender):
            self.gender = gender
        else:
            raise TypeError

        if isinstance(language, Language):
            self.language = language
        else:
            raise TypeError


class Client:
    '''
    This is a base client for text to speech api services.
    '''

    TOO_LONG_DATA_MSG = ('Too long data is passed to tts(). '
                         'Available up to {} characters, but got {}.')

    def __init__(self, credential=None):
        self.auth(credential)

    def _voice_config_to_dict(self, vc):
        pass

    def _is_valid_params(self, params):
        pass

    def _make_params(self, vc, detail):
        params = {}

        if vc and detail:
            if not isinstance(vc, VoiceConfig):
                raise TypeError
            params = self._voice_config_to_dict(vc)
            params.update(detail)
        elif vc:
            if not isinstance(vc, VoiceConfig):
                raise TypeError
            params = self._voice_config_to_dict(vc)
        elif detail:
            params = detail
        else:
            vc = VoiceConfig()
            params = self._voice_config_to_dict(vc)

        if not self._is_valid_params(params):
            raise ValueError

        return params

    def auth(self, credential):
        self.credential = credential

    def tts(self, text, voice_config=None, detail=None):
        pass
