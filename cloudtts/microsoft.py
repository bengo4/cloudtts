import requests

from .client import AudioFormat
from .client import CloudTTSError
from .client import Client
from .client import Gender
from .client import Language
from .client import VoiceConfig


class AzureClient(Client):
    '''
    This is a client class for Azure Text to Speech API

    >>> from cloudtts import AzureClient
    >>> cred = {'api_key': YOUR_API_KEY}
    >>> c = AzureClient(cred)
    >>> audio = c.tts('Hello world!')
    >>> open('/path/to/save/audio', 'wb') as f:
    ...   f.write(audio)
    '''

    TokenEndpoint = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    TTSEndpoint = 'https://speech.platform.bing.com/synthesize'
    MAX_TEXT_LENGTH = 1024

    AVAILABLE_FORMATS = (
        'audio-16khz-128kbitrate-mono-mp3',
        'audio-16khz-16kbps-mono-siren',
        'audio-16khz-32kbitrate-mono-mp3',
        'audio-16khz-64kbitrate-mono-mp3',
        'raw-16khz-16bit-mono-pcm',
        'riff-16khz-16bit-mono-pcm',
        'riff-16khz-16kbps-mono-siren',
        'ssml-16khz-16bit-mono-tts',
    )

    AUDIO_FORMAT_DICT = {
        AudioFormat.mp3: 'audio-16khz-128kbitrate-mono-mp3',
        AudioFormat.pcm: 'raw-16khz-16bit-mono-pcm',
    }

    AVAILABLE_VOICES = (
        'An', 'Andika', 'Andrei', 'Asaf', 'Ayumi, Apollo',
        'BenjaminRUS',
        'Caroline', 'Catherine', 'Cosimo, Apollo',
        'Daniel, Apollo', 'Danny, Apollo',
        'EkaterinaRUS',
        'Filip',
        'George, Apollo', 'Guillaume', 'Guy24kRUS',
        'HanHanRUS', 'HannaRUS', 'HarmonieRUS', 'HarukaRUS', 'HayleyRUS',
        'HazelRUS', 'HeamiRUS', 'HeatherRUS', 'Hedda', 'HeddaRUS', 'HedvigRUS',
        'Heera, Apollo', 'HeidiRUS', 'HelenaRUS', 'HeliaRUS', 'HelleRUS',
        'HeloisaRUS', 'Hemant', 'HerenaRUS', 'HildaRUS', 'Hoda', 'HortenseRUS',
        'HuihuiRUS', 'HuldaRUS',
        'Ichiro, Apollo', 'Irina, Apollo', 'Ivan',
        'Jakub', 'Jessa24kRUS', 'JessaRUS', 'Julie, Apollo',
        'Kalpana', 'Kalpana, Apollo', 'Kangkang, Apollo', 'Karsten',
        'Lado', 'Laura, Apollo', 'Linda', 'LuciaRUS',
        'Matej', 'Michael',
        'Naayf',
        'Pablo, Apollo', 'Pattara', 'Paul, Apollo', 'PaulinaRUS',
        'Pavel, Apollo', 'PriyaRUS',
        'Raul, Apollo', 'Ravi, Apollo', 'Rizwan',
        'Sean', 'SedaRUS', 'Stefan, Apollo', 'Stefanos', 'Susan, Apollo',
        'Szabolcs',
        'Tracy, Apollo', 'TracyRUS',
        'Valluvar',
        'Yaoyao, Apollo', 'Yating, Apollo',
        'ZiraRUS',
    )

    LANG_GENDER_DICT = {
        (Language.da_DK, Gender.female): 'HelleRUS',
        (Language.de_DE, Gender.female): 'HeddaRUS',
        (Language.de_DE, Gender.male): 'Stefan, Apollo',
        (Language.en_AU, Gender.female): 'HayleyRUS',
        (Language.en_GB, Gender.female): 'Susan, Apollo',
        (Language.en_GB, Gender.male): 'George, Apollo',
        (Language.en_IN, Gender.female): 'PriyaRUS',
        (Language.en_IN, Gender.male): 'Ravi, Apollo',
        (Language.en_US, Gender.female): 'ZiraRUS',
        (Language.en_US, Gender.male): 'Guy24kRUS',
        (Language.es_ES, Gender.female): 'HelenaRUS',
        (Language.es_ES, Gender.male): 'Pablo, Apollo',
        (Language.fr_CA, Gender.female): 'HarmonieRUS',
        (Language.fr_FR, Gender.female): 'HortenseRUS',
        (Language.fr_FR, Gender.male): 'Paul, Apollo',
        (Language.hi_IN, Gender.female): 'Kalpana, Apollo',
        (Language.hi_IN, Gender.male): 'Hemant',
        (Language.it_IT, Gender.female): 'LuciaRUS',
        (Language.it_IT, Gender.male): 'Cosimo, Apollo',
        (Language.ja_JP, Gender.female): 'Ayumi, Apollo',
        (Language.ja_JP, Gender.male): 'Ichiro, Apollo',
        (Language.ko_KR, Gender.female): 'HeamiRUS',
        (Language.nb_NO, Gender.female): 'HuldaRUS',
        (Language.nl_NL, Gender.female): 'HannaRUS',
        (Language.pl_PL, Gender.female): 'PaulinaRUS',
        (Language.pt_BR, Gender.female): 'HeloisaRUS',
        (Language.pt_BR, Gender.male): 'Daniel, Apollo',
        (Language.pt_PT, Gender.female): 'HeliaRUS',
        (Language.ro_RO, Gender.male): 'Andrei',
        (Language.ru_RU, Gender.female): 'EkaterinaRUS',
        (Language.ru_RU, Gender.male): 'Pavel, Apollo',
        (Language.sv_SE, Gender.female): 'HedvigRUS',
        (Language.tr_TR, Gender.female): 'SedaRUS',
    }

    XML = ('<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"'
           '       xml:lang="{lang}">'
           '  <voice xml:lang="{lang}" xml:gender="{gender}"'
           '         name="Microsoft Server Speech Text to Speech Voice ({lang}, {voice})">'
           '    {text}'
           '  </voice>'
           '</speak>')

    def _voice_config_to_dict(self, vc):
        d = {}

        if vc.audio_format in AzureClient.AUDIO_FORMAT_DICT:
            d['format'] = AzureClient.AUDIO_FORMAT_DICT[vc.audio_format]

        if (vc.language, vc.gender) in AzureClient.LANG_GENDER_DICT:
            d['voice'] = AzureClient.LANG_GENDER_DICT[(vc.language, vc.gender)]
            d['language'] = vc.language.value
            d['gender'] = vc.gender.value

        return d

    def _is_valid_format(self, params):
        if 'format' not in params:
            return False

        return params['format'] in AzureClient.AVAILABLE_FORMATS

    def _is_valid_voice(self, params):
        if 'voice' not in params:
            return False

        return params['voice'] in AzureClient.AVAILABLE_VOICES

    def _is_valid_params(self, params):
        return self._is_valid_format(params) and self._is_valid_voice(params)

    def _token(self):
        headers = {'Ocp-Apim-Subscription-Key': self.credential['api_key']}
        r = requests.post(AzureClient.TokenEndpoint, headers=headers)

        return str(r.text)

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

        _xml = AzureClient.XML.format(
            lang=params['language'],
            gender=params['gender'],
            voice=params['voice'],
            text=text
        )

        if len(_xml) > AzureClient.MAX_TEXT_LENGTH:
            msg = 'AzureClient.tts() process up to {} chars, but got {}'.format(
                AzureClient.MAX_TEXT_LENGTH, len(_xml))
            raise CloudTTSError(msg)

        _headers = {'Content-type': 'application/ssml+xml',
                    'X-Microsoft-OutputFormat': params['format'],
                    'Authorization': 'Bearer: {}'.format(self._token())}

        r = requests.post(url=AzureClient.TTSEndpoint,
                          headers=_headers, data=_xml.encode('utf-8'))

        if r.status_code == requests.codes.ok:
            return r.content
        else:
            r.raise_for_status()
