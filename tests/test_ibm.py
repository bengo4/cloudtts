from unittest import TestCase

from cloudtts import AudioFormat
from cloudtts import CloudTTSError
from cloudtts import Gender
from cloudtts import VoiceConfig
from cloudtts import WatsonClient
from cloudtts import WatsonCredential


class TestWatsonClient(TestCase):
    def setUp(self):
        self.c = WatsonClient()

    def test_init(self):
        self.assertIsInstance(self.c, WatsonClient)

    def test_make_params_with_nothing(self):
        params = self.c._make_params(None, None)

        self.assertIsInstance(params, dict)
        self.assertIn('accept', params)
        self.assertEqual(params['accept'], 'audio/mp3')
        self.assertIn('voice', params)
        self.assertEqual(params['voice'], 'en-US_AllisonVoice')

    def test_make_params_with_voice_config_only(self):
        for l, g in WatsonClient.LANG_GENDER_DICT:
            vc = VoiceConfig(language=l, gender=g)
            params = self.c._make_params(vc, None)
            voice = WatsonClient.LANG_GENDER_DICT[(l, g)]
            self.assertEqual(params['voice'], voice)

    def test_make_params_with_detail_only(self):
        detail = {'accept': 'audio/ogg;codecs=opus',
                  'voice': 'en-US_MichaelVoice'}

        params = self.c._make_params(None, detail)

        for k in detail:
            self.assertEqual(detail[k], params[k])

    def test_make_params_with_voice_config_and_detail(self):
        detail = {'accept': 'audio/ogg;codecs=opus;rate=192000',
                  'voice': 'en-US_MichaelVoice'}
        vc = VoiceConfig(audio_format=AudioFormat.mp3, gender=Gender.female)
        params = self.c._make_params(vc, detail)

        # detail overwrites values
        self.assertNotEqual(params['accept'], 'mp3')
        self.assertEqual(params['accept'], detail['accept'])

        self.assertNotEqual(params['voice'], 'en-US_AllisonVoice')
        self.assertEqual(params['voice'], detail['voice'])

    def test_auth_before_tts(self):
        txt = 'Hello world'

        self.assertRaises(CloudTTSError, lambda: self.c.tts(txt))

    def test_invalid_credential(self):
        self.c.auth({
            'username': 'username',
            'password': 'password',
            'url': 'https://stream.watsonplatform.net/text-to-speech/api'
        })
        txt = 'Hello world'
        self.assertRaises(TypeError, lambda: self.c.tts(txt))

    def test_is_valid_voice(self):
        for voice in WatsonClient.AVAILABLE_VOICES:
            self.assertTrue(self.c._is_valid_voice({'voice': voice}))

        self.assertFalse(self.c._is_valid_voice(
            {'voice': 'ja-JP_MitsuhiroVoice'}))

    def test_is_valid_accept(self):
        for codec in WatsonClient.AVAILABLE_ACCEPTS['require_rate']:
            d = {'accept': codec}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate='.format(codec)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, 'abc')}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE-1)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE)}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE)}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE+1)}
            self.assertFalse(self.c._is_valid_accept(d))

        for codec in WatsonClient.AVAILABLE_ACCEPTS['allow_rate']:
            d = {'accept': codec}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate='.format(codec)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, 'abc')}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE-1)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE)}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE)}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE+1)}
            self.assertFalse(self.c._is_valid_accept(d))

        for codec in WatsonClient.AVAILABLE_ACCEPTS['disallow_rate']:
            d = {'accept': codec}
            self.assertTrue(self.c._is_valid_accept(d))

            d = {'accept': '{};rate='.format(codec)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, 'abc')}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE-1)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MIN_RATE)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE)}
            self.assertFalse(self.c._is_valid_accept(d))

            d = {'accept': '{};rate={}'.format(codec, WatsonClient.MAX_RATE+1)}
            self.assertFalse(self.c._is_valid_accept(d))


class TestWatsonCredential(TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
