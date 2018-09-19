from contextlib import closing

from boto3 import Session

from .client import AudioFormat
from .client import Client
from .client import CloudTTSError
from .client import Gender
from .client import Language
from .client import VoiceConfig


class PollyCredential:
    def __init__(self, region_name,
                 aws_access_key_id='', aws_secret_access_key=''):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def has_access_key(self):
        return self.aws_access_key_id and self.aws_secret_access_key


class PollyClient(Client):
    '''
    This is a client class for Amazon Polly API

    >>> from cloudtts import PollyClient, PollyCredential
    >>> cred = PollyCredential(
    ...         aws_access_key_id=YOUR_ACCESS_KEY_ID,
    ...         aws_secret_access_key=YOUR_SECRET_ACCESS_KEY,
    ...         region_name=AWS_REGION_NAME
    ... )
    >>> c = PollyClient(cred)
    >>> audio = c.tts('Hello world!')
    >>> open('/path/to/save/audio', 'wb') as f:
    ...   f.write(audio)
    '''

    AVAILABLE_SAMPLE_RATES = {
        'mp3': ('8000', '16000', '22050'),
        'ogg_vorbis': ('8000', '16000', '22050'),
        'pcm': ('8000', '16000'),
    }
    AVAILABLE_VOICE_IDS = ('Aditi', 'Aditi', 'Amy', 'Astrid',
                           'Brian',
                           'Carla', 'Carmen', 'Celine', 'Chantal', 'Conchita',
                           'Cristiano', 'Céline',
                           'Dora', 'Dóra',
                           'Emma', 'Enrique', 'Ewa',
                           'Filiz',
                           'Geraint', 'Giorgio', 'Gwyneth',
                           'Hans',
                           'Ines', 'Inês', 'Ivy',
                           'Jacek', 'Jan', 'Joanna', 'Joey', 'Justin',
                           'Karl', 'Kendra', 'Kimberly',
                           'Liv', 'Lotte', 'Léa',
                           'Mads', 'Maja', 'Marlene', 'Mathieu', 'Matthew',
                           'Maxim', 'Miguel', 'Mizuki',
                           'Naja', 'Nicole',
                           'Penelope', 'Penélope',
                           'Raveena', 'Ricardo', 'Ruben', 'Russell',
                           'Salli', 'Seoyeon',
                           'Takumi', 'Tatyana',
                           'Vicki', 'Vitoria', 'Vitória',
                           )

    AUDIO_FORMAT_DICT = {
        AudioFormat.mp3: ('mp3', '22050'),
        AudioFormat.ogg_vorbis: ('ogg_vorbis', '22050'),
        AudioFormat.pcm: ('pcm', '16000'),
    }

    LANG_GENDER_DICT = {
        (Language.da_DK, Gender.female): 'Naja',
        (Language.da_DK, Gender.male): 'Mads',
        (Language.de_DE, Gender.female): 'Marlene',
        (Language.de_DE, Gender.male): 'Hans',
        (Language.en_AU, Gender.female): 'Nicole',
        (Language.en_AU, Gender.male): 'Russell',
        (Language.en_GB, Gender.female): 'Amy',
        (Language.en_GB, Gender.male): 'Brian',
        (Language.en_IN, Gender.female): 'Aditi',  # bilingual
        (Language.en_US, Gender.female): 'Joanna',
        (Language.en_US, Gender.male): 'Joey',
        (Language.es_ES, Gender.female): 'Conchita',
        (Language.es_ES, Gender.male): 'Enrique',
        (Language.es_US, Gender.female): 'Penelope',
        (Language.es_US, Gender.male): 'Miguel',
        (Language.fr_CA, Gender.female): 'Chantal',
        (Language.fr_FR, Gender.female): 'Celine',
        (Language.fr_FR, Gender.male): 'Mathieu',
        (Language.hi_IN, Gender.female): 'Aditi',  # bilingual
        (Language.it_IT, Gender.female): 'Carla',
        (Language.it_IT, Gender.male): 'Giorgio',
        (Language.ja_JP, Gender.female): 'Mizuki',
        (Language.ja_JP, Gender.male): 'Takumi',
        (Language.ko_KR, Gender.female): 'Seoyeon',
        (Language.nb_NO, Gender.female): 'Liv',
        (Language.nl_NL, Gender.female): 'Lotte',
        (Language.nl_NL, Gender.male): 'Ruben',
        (Language.pl_PL, Gender.female): 'Ewa',
        (Language.pl_PL, Gender.male): 'Jacek',
        (Language.pt_BR, Gender.female): 'Vitoria',
        (Language.pt_BR, Gender.male): 'Ricardo',
        (Language.pt_PT, Gender.female): 'Ines',
        (Language.pt_PT, Gender.male): 'Cristiano',
        (Language.ro_RO, Gender.female): 'Carmen',
        (Language.ru_RU, Gender.female): 'Tatyana',
        (Language.ru_RU, Gender.male): 'Maxim',
        (Language.sv_SE, Gender.female): 'Astrid',
        (Language.tr_TR, Gender.female): 'Filiz',
    }

    def _voice_config_to_dict(self, vc):
        d = {}

        if vc.audio_format in PollyClient.AUDIO_FORMAT_DICT:
            d['output_format'], d['sample_rate'] = \
                PollyClient.AUDIO_FORMAT_DICT[vc.audio_format]

        if (vc.language, vc.gender) in PollyClient.LANG_GENDER_DICT:
            voice_id = PollyClient.LANG_GENDER_DICT[(vc.language, vc.gender)]
            d['voice_id'] = voice_id

        return d

    def _is_valid_output_format(self, params):
        if not 'output_format' in params:
            return False

        return params['output_format'] in PollyClient.AVAILABLE_SAMPLE_RATES

    def _is_valid_sample_rate(self, params):
        if params['output_format'] not in PollyClient.AVAILABLE_SAMPLE_RATES:
            return False

        if 'sample_rate' not in params:
            return False

        rates = PollyClient.AVAILABLE_SAMPLE_RATES[params['output_format']]
        return params['sample_rate'] in rates

    def _is_valid_voice_id(self, params):
        if 'voice_id' not in params:
            return False

        return params['voice_id'] in PollyClient.AVAILABLE_VOICE_IDS

    def _is_valid_params(self, params):
        return self._is_valid_output_format(params) and \
            self._is_valid_sample_rate(params) and \
            self._is_valid_voice_id(params)

    def tts(self, text='', ssml='', voice_config=None, detail=None):
        '''
        Synthesizes audio data for text.

        Args:
          text: string / target to be synthesized(plain text)
          ssml: string / target to be synthesized(SSML)
          voice_config: VoiceConfig / parameters for voice and audio
          detail: dict / detail parameters for voice and audio

        Returns:
          binary
        '''

        if self.credential:
            if isinstance(self.credential, PollyCredential):
                pass
            else:
                raise TypeError('Invalid credential')
        else:
            raise CloudTTSError('No Authentication yet')

        if self.credential.has_access_key():
            sess = Session(
                region_name=self.credential.region_name,
                aws_access_key_id=self.credential.aws_access_key_id,
                aws_secret_access_key=self.credential.aws_secret_access_key
            )
        else:
            sess = Session(region_name=self.credential.region_name)

        polly = sess.client('polly')

        params = self._make_params(voice_config, detail)

        response = polly.synthesize_speech(
            Text=ssml if ssml else text,
            TextType='ssml' if ssml else 'text',
            OutputFormat=params['output_format'],
            VoiceId=params['voice_id'],
            SampleRate=params['sample_rate'],
        )

        audio = None
        if 'AudioStream' in response:
            with closing(response['AudioStream']) as stream:
                audio = stream.read()

        return audio
