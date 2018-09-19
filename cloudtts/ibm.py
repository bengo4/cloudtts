import json
import re

import requests

from .client import AudioFormat
from .client import Client
from .client import CloudTTSError
from .client import Gender
from .client import Language
from .client import VoiceConfig


class WatsonCredential:
    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url


class WatsonClient(Client):
    '''
    This is a client class for Watson Text to Speech API

    >>> from cloudtts import WatsonClient, WatsonCredential
    >>> cred = WatsonCredential(
    ...         username=YOUR_USER_NAME,
    ...         password=YOUR_PASSWORD,
    ...         url=API_ENDPOINT
    ... )
    >>> c = IBMClient(cred)
    >>> audio = c.tts('Hello world!')
    >>> open('/path/to/save/audio', 'wb') as f:
    ...   f.write(audio)
    '''

    VERSION = 'v1'
    MAX_TEXT_BYTES = 5 * 1024

    AVAILABLE_ACCEPTS = {
        'require_rate': [
            'audio/l16',
            'audio/mulaw',
        ],
        'allow_rate': [
            'audio/flac',
            'audio/mp3',
            'audio/mpeg',
            'audio/ogg',
            'audio/ogg;codecs=opus',
            'audio/ogg;codecs=vorbis',
            'audio/wav',
            'audio/webm;codecs=vorbis',
        ],
        'disallow_rate': [
            'audio/basic',
            'audio/webm',
            'audio/webm;codecs=opus',
        ],
    }

    AUDIO_FORMAT_DICT = {
        AudioFormat.mp3: 'audio/mp3',
        AudioFormat.ogg_opus: 'audio/ogg;codecs=opus',
        AudioFormat.ogg_vorbis: 'audio/ogg;codecs=vorbis',
    }

    MIN_RATE = 8000
    MAX_RATE = 192000

    AVAILABLE_VOICES = (
        'de-DE_BirgitVoice',
        'de-DE_DieterVoice',
        'en-GB_KateVoice',
        'en-US_AllisonVoice',
        'en-US_LisaVoice',
        'en-US_MichaelVoice',
        'es-ES_EnriqueVoice',
        'es-ES_LauraVoice',
        'es-LA_SofiaVoice',
        'es-US_SofiaVoice',
        'fr-FR_ReneeVoice',
        'it-IT_FrancescaVoice',
        'ja-JP_EmiVoice',
        'pt-BR_IsabelaVoice',
    )

    LANG_GENDER_DICT = {
        (Language.de_DE, Gender.female): 'de-DE_BirgitVoice',
        (Language.de_DE, Gender.male):   'de-DE_DieterVoice',
        (Language.en_GB, Gender.female): 'en-GB_KateVoice',
        (Language.en_US, Gender.female): 'en-US_AllisonVoice',
        (Language.en_US, Gender.male):   'en-US_MichaelVoice',
        (Language.es_ES, Gender.female): 'es-ES_LauraVoice',
        (Language.es_ES, Gender.male):   'es-ES_EnriqueVoice',
        (Language.es_US, Gender.female): 'es-US_SofiaVoice',
        (Language.fr_FR, Gender.female): 'fr-FR_ReneeVoice',
        (Language.it_IT, Gender.female): 'it-IT_FrancescaVoice',
        (Language.ja_JP, Gender.female): 'ja-JP_EmiVoice',
        (Language.pt_BR, Gender.female): 'pt-BR_IsabelaVoice',
    }

    def _voice_config_to_dict(self, vc):
        d = {}

        if vc.audio_format in WatsonClient.AUDIO_FORMAT_DICT:
            d['accept'] = WatsonClient.AUDIO_FORMAT_DICT[vc.audio_format]

        if (vc.language, vc.gender) in WatsonClient.LANG_GENDER_DICT:
            voice = WatsonClient.LANG_GENDER_DICT[(vc.language, vc.gender)]
            d['voice'] = voice

        return d

    def _is_valid_sampling_rate(self, r):
        return WatsonClient.MIN_RATE <= r <= WatsonClient.MAX_RATE

    def _is_valid_accept(self, params):
        rate_pat = re.compile('rate=(\d+)')

        if 'accept' not in params:
            return False

        if params['accept'] in WatsonClient.AVAILABLE_ACCEPTS['disallow_rate']:
            return True

        for codec in WatsonClient.AVAILABLE_ACCEPTS['allow_rate']:
            if params['accept'] == codec:
                return True

            if params['accept'].startswith(codec):
                with_rate = rate_pat.search(params['accept'])
                if with_rate and self._is_valid_sampling_rate(int(with_rate[1])):
                    return True

        for codec in WatsonClient.AVAILABLE_ACCEPTS['require_rate']:
            if params['accept'].startswith(codec):
                with_rate = rate_pat.search(params['accept'])
                if with_rate and self._is_valid_sampling_rate(int(with_rate[1])):
                    return True

        return False

    def _is_valid_voice(self, params):
        if 'voice' not in params:
            return False

        return params['voice'] in WatsonClient.AVAILABLE_VOICES

    def _is_valid_params(self, params):
        return self._is_valid_accept(params)and self._is_valid_voice(params)

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

        if self.credential:
            if isinstance(self.credential, WatsonCredential):
                pass
            else:
                raise TypeError('Invalid credential')
        else:
            raise CloudTTSError('No Authentication yet')

        params = self._make_params(voice_config, detail)

        if not self._is_valid_accept(params):
            raise ValueError

        if not self._is_valid_voice(params):
            raise ValueError

        _url = '{}/{}/synthesize'.format(self.credential.url,
                                         WatsonClient.VERSION)
        _query = {'voice': params['voice']}
        if 'customization_id' in params:
            _query['customization_id'] = params['customization_id']
        _headers = {'Accept': params['accept']}
        _auth = (self.credential.username, self.credential.password)
        _data = {'text': text}

        json_size = len(json.dumps(_data).encode())
        if json_size > WatsonClient.MAX_TEXT_BYTES:
            msg = 'WatsonClient.tts() process up to {} bytes, but got {}'.format(
                WatsonClient.MAX_TEXT_BYTES, json_size)
            raise CloudTTSError(msg)

        r = requests.post(url=_url, params=_query, headers=_headers,
                          auth=_auth, json=_data)

        if r.status_code == requests.codes.ok:
            return r.content
        else:
            r.raise_for_status()
