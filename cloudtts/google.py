import os

from google.cloud import texttospeech

from .client import AudioFormat
from .client import Client
from .client import CloudTTSError
from .client import Gender
from .client import Language
from .client import VoiceConfig


class GoogleClient(Client):
    '''
    This is a client class for Google Cloud Text-to-Speech API

    >>> from cloudtts import GoogleClient
    >>> c = GoogleClient('/path/to/credential.json')
    >>> audio = c.tts('Hello world!')
    >>> open('/path/to/save/audio', 'wb') as f:
    ...   f.write(audio)

    '''

    AUDIO_FORMAT_DICT = {
        AudioFormat.mp3: texttospeech.enums.AudioEncoding.MP3,
        AudioFormat.ogg_opus: texttospeech.enums.AudioEncoding.OGG_OPUS,
    }

    GENDER_DICT = {
        Gender.male: texttospeech.enums.SsmlVoiceGender.MALE,
        Gender.female: texttospeech.enums.SsmlVoiceGender.FEMALE,
    }

    AVAILABLE_LANGUAGES = [
        Language.nl_NL,
        Language.en_AU,
        Language.en_GB,
        Language.en_US,
        Language.fr_FR,
        Language.fr_CA,
        Language.de_DE,
        Language.it_IT,
        Language.ja_JP,
        Language.ko_KR,
        Language.pt_BR,
        Language.es_ES,
        Language.sv_SE,
        Language.tr_TR,
    ]

    def _voice_config_to_dict(self, vc):
        d = {}

        if vc.audio_format in GoogleClient.AUDIO_FORMAT_DICT:
            af = GoogleClient.AUDIO_FORMAT_DICT[vc.audio_format]
            d['audio_encoding'] = af

        if vc.gender in GoogleClient.GENDER_DICT:
            d['gender'] = GoogleClient.GENDER_DICT[vc.gender]

        if vc.language in GoogleClient.AVAILABLE_LANGUAGES:
            d['language'] = vc.language.value

        return d

    def _is_valid_audio_encoding(self, params):
        if 'audio_encoding' not in params:
            return False

        return isinstance(params['audio_encoding'],
                          texttospeech.enums.AudioEncoding)

    def _is_valid_gender(self, params):
        if 'gender' not in params:
            return False

        return isinstance(params['gender'], texttospeech.enums.SsmlVoiceGender)

    def _is_valid_language(self, params):
        if 'language' not in params:
            return False

        for lang in GoogleClient.AVAILABLE_LANGUAGES:
            if params['language'] == lang.value:
                return True
        else:
            return False

    def _is_valid_params(self, params):
        return self._is_valid_audio_encoding(params) and \
            self._is_valid_gender(params) and \
            self._is_valid_language(params)

    def auth(self, credential):
        '''
        Authenticates

        Args:
          credential: string / path to JSON file
        '''

        if credential:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential

        super().auth(credential)

    def tts(self, text, voice_config=None, detail=None):
        '''
        Synthesizes audio data for text.

        Args:
          text: string / target to be synthesized
          voice_config: VoiceConfig / parameters for voice and audio
          detail: dict / detail parameters for voice and audio

        Returns:
          binary
        '''

        if not self.credential:
            raise CloudTTSError('No Authentication yet')

        params = self._make_params(voice_config, detail)

        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=params['language'],
            ssml_gender=params['gender'])
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=params['audio_encoding'])
        response = client.synthesize_speech(input_text, voice, audio_config)

        return response.audio_content
