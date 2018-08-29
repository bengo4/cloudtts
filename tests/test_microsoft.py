from unittest import TestCase

from cloudtts import AudioFormat
from cloudtts import AzureClient
from cloudtts import CloudTTSError
from cloudtts import Gender
from cloudtts import Language
from cloudtts import VoiceConfig


class TestAzureClient(TestCase):
    def setUp(self):
        self.c = AzureClient()

    def test_init(self):
        self.assertIsInstance(self.c, AzureClient)

    def test_make_params_with_nothing(self):
        params = self.c._make_params(None, None)

        self.assertIsInstance(params, dict)
        self.assertIn('format', params)
        self.assertEqual(params['format'], 'audio-16khz-128kbitrate-mono-mp3')
        self.assertIn('language', params)
        self.assertEqual(params['language'], 'en-US')
        self.assertIn('voice', params)
        self.assertEqual(params['voice'], 'ZiraRUS')

    def test_make_params_with_voice_config_only(self):
        for l, g in AzureClient.LANG_GENDER_DICT:
            vc = VoiceConfig(language=l, gender=g)
            params = self.c._make_params(vc, None)
            voice = AzureClient.LANG_GENDER_DICT[(l, g)]
            self.assertEqual(params['voice'], voice)

    def test_make_params_with_detail_only(self):
        detail = {'format': 'ssml-16khz-16bit-mono-tts',
                  'gender': 'male',
                  'language': 'ja-JP',
                  'voice': 'Ichiro, Apollo'}
        params = self.c._make_params(None, detail)

        for k in detail:
            self.assertEqual(detail[k], params[k])

    def test_make_params_with_voice_config_and_detail(self):
        vc = VoiceConfig(audio_format=AudioFormat.mp3,
                         gender=Gender.female,
                         language=Language.en_US)
        detail = {'format': 'ssml-16khz-16bit-mono-tts',
                  'gender': 'male',
                  'language': 'ja-JP',
                  'voice': 'Ichiro, Apollo'}

        params = self.c._make_params(vc, detail)

        # detail overwrites values
        self.assertNotEqual(params['format'],
                            'audio-16khz-128kbitrate-mono-mp3')
        self.assertEqual(params['format'], detail['format'])

        self.assertNotEqual(params['voice'], 'ZiraRUS')
        self.assertEqual(params['voice'], detail['voice'])

    def test_auth_before_tts(self):
        txt = 'Hello world'

        self.assertRaises(CloudTTSError, lambda: self.c.tts(txt))

    def test_is_valid_format(self):
        for format in AzureClient.AVAILABLE_FORMATS:
            self.assertTrue(self.c._is_valid_format({'format': format}))

    def test_is_valid_voice(self):
        for voice in AzureClient.AVAILABLE_VOICES:
            self.assertTrue(self.c._is_valid_voice({'voice': voice}))


if __name__ == '__main__':
    unittest.main()
