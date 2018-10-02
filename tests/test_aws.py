from unittest import TestCase

from cloudtts import AudioFormat
from cloudtts import CloudTTSError
from cloudtts import Gender
from cloudtts import Language
from cloudtts import PollyClient
from cloudtts import PollyCredential
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

    def test_error_without_data(self):
        cred = PollyCredential('ap-northeast-1')
        self.c.auth(cred)

        self.assertRaises(ValueError, lambda: self.c.tts())

    def test_acceptable_text_length(self):
        cred = PollyCredential('ap-northeast-1')
        self.c.auth(cred)

        text = 'a' * PollyClient.MAX_TEXT_LENGTH

        # raise TypeError not to call API and
        # to make sure MAX_TEXT_LENGTH works
        self.assertRaises(TypeError,
                          lambda: self.c.tts(
                              text=text,
                              voice_config=True,
                          ))

    def test_error_with_too_long_text(self):
        cred = PollyCredential('ap-northeast-1')
        self.c.auth(cred)

        text = 'a' * (PollyClient.MAX_TEXT_LENGTH+1)

        # CloudTTSError is raised with too long text
        self.assertRaises(CloudTTSError, lambda: self.c.tts(text=text))

    def test_error_with_too_long_ssml(self):
        cred = PollyCredential('ap-northeast-1')
        self.c.auth(cred)

        text = 'a' * PollyClient.MAX_TEXT_LENGTH

        # raise TypeError not to call API and
        # to make sure MAX_TEXT_LENGTH works
        ssml = '<speak>{}</speak>'.format(text)
        self.assertRaises(TypeError,
                          lambda: self.c.tts(
                              ssml=ssml,
                              voice_config=True,
                          ))

        # CloudTTSError is raised with too long ssml
        ssml = '<speak>{}</speak>'.format(text + 'a')
        self.assertRaises(CloudTTSError, lambda: self.c.tts(ssml=ssml))

    def test_control_ssml_length_with_text(self):
        cred = PollyCredential('ap-northeast-1')
        self.c.auth(cred)

        text = 'a' * PollyClient.MAX_TEXT_LENGTH
        ssml = '<speak><break>{}</speak>'.format(text)

        # '<break>' is couted and CloudTTSError is raised
        self.assertRaises(CloudTTSError, lambda: self.c.tts(ssml=ssml))

        # 'text' is used to count characters
        #
        # raise TypeError not to call API and
        # to make sure MAX_TEXT_LENGTH works
        self.assertRaises(TypeError,
                          lambda: self.c.tts(
                              text=text,
                              ssml=ssml,
                              voice_config=True,
                          ))

    def test_invalid_credential(self):
        self.c.auth({'region_name': 'ap-northeast-1'})
        txt = 'Hello world'
        self.assertRaises(TypeError, lambda: self.c.tts(txt))

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


class TestPollyCredential(TestCase):
    def test_has_access_key(self):
        c = PollyCredential('ap-northeast-1')
        self.assertFalse(c.has_access_key())

        c = PollyCredential('ap-northeast-1', aws_access_key_id='abc')
        self.assertFalse(c.has_access_key())

        c = PollyCredential('ap-northeast-1',
                            aws_access_key_id='abc',
                            aws_secret_access_key='xyz')
        self.assertTrue(c.has_access_key())


if __name__ == '__main__':
    unittest.main()
