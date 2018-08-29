from unittest import TestCase

from cloudtts import AudioFormat
from cloudtts import CloudTTSError
from cloudtts import Gender
from cloudtts import Language
from cloudtts import PollyClient
from cloudtts import VoiceConfig


class TestPollyClient(TestCase):
    def setUp(self):
        self.c = PollyClient()

    def test_init(self):
        self.assertIsInstance(self.c, PollyClient)

    def test_make_params_with_nothing(self):
        params = self.c._make_params(None, None)

        self.assertIsInstance(params, dict)
        self.assertIn('output_format', params)
        self.assertEqual(params['output_format'], 'mp3')
        self.assertIn('voice_id', params)
        self.assertEqual(params['voice_id'], 'Joanna')

    def test_make_params_with_voice_config_only(self):
        for l, g in PollyClient.LANG_GENDER_DICT:
            vc = VoiceConfig(language=l, gender=g)
            params = self.c._make_params(vc, None)
            voice_id = PollyClient.LANG_GENDER_DICT[(l, g)]
            self.assertEqual(params['voice_id'], voice_id)

    def test_make_params_with_detail_only(self):
        detail = {'output_format': 'mp3',
                  'sample_rate': '16000',
                  'voice_id': 'Kendra'}
        params = self.c._make_params(None, detail)

        for k in detail:
            self.assertEqual(detail[k], params[k])

    def test_make_params_with_voice_config_and_detail(self):
        detail = {'output_format': 'pcm',
                  'sample_rate': '16000',
                  'voice_id': 'Kendra'}
        vc = VoiceConfig(audio_format=AudioFormat.mp3, gender=Gender.female)
        params = self.c._make_params(vc, detail)

        # detail overwrites values
        self.assertNotEqual(params['output_format'], 'mp3')
        self.assertEqual(params['output_format'], detail['output_format'])

        self.assertNotEqual(params['voice_id'], 'Joanna')
        self.assertEqual(params['voice_id'], detail['voice_id'])

    def test_auth_before_tts(self):
        txt = 'Hello world'

        self.assertRaises(CloudTTSError, lambda: self.c.tts(txt))

    def test_is_valid_output_format(self):
        self.assertFalse(self.c._is_valid_output_format({}))

        for fmt in PollyClient.AVAILABLE_SAMPLE_RATES:
            params = {'output_format': fmt}
            self.assertTrue(self.c._is_valid_output_format(params))

    def test_is_valid_sample_rate(self):
        for fmt in ('mp3', 'ogg_vorbis'):
            params = {'output_format': fmt}
            for rate in ('8000', '16000', '22050'):
                params = {'output_format': fmt, 'sample_rate': rate}
                self.assertTrue(self.c._is_valid_output_format(params))

        params = {'output_format': 'pcm'}
        for rate in ('8000', '16000'):
            params['sample_rate'] = rate
            self.assertTrue(self.c._is_valid_output_format(params))

    def test_is_valid_voice_id(self):
        self.assertFalse(self.c._is_valid_voice_id({}))

        for voice in PollyClient.AVAILABLE_VOICE_IDS:
            self.assertTrue(self.c._is_valid_voice_id({'voice_id': voice}))


if __name__ == '__main__':
    unittest.main()
