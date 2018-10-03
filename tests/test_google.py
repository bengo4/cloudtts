from unittest import TestCase, skip

from google.cloud import texttospeech

from cloudtts import AudioFormat
from cloudtts import CloudTTSError
from cloudtts import GoogleClient
from cloudtts import Gender
from cloudtts import Language
from cloudtts import VoiceConfig


class TestGoogleClient(TestCase):
    def setUp(self):
        self.c = GoogleClient()

    def test_init(self):
        self.assertIsInstance(self.c, GoogleClient)

    def test_make_params_with_nothing(self):
        params = self.c._make_params(None, None)

        self.assertIsInstance(params, dict)
        self.assertIn('audio_encoding', params)
        self.assertEqual(params['audio_encoding'],
                         texttospeech.enums.AudioEncoding.MP3)
        self.assertIn('gender', params)
        self.assertEqual(params['gender'],
                         texttospeech.enums.SsmlVoiceGender.FEMALE)
        self.assertIn('language', params)
        self.assertEqual(params['language'], Language.en_US.value)

    def test_make_params_with_voice_config_only(self):
        for l in GoogleClient.AVAILABLE_LANGUAGES:
            for g in GoogleClient.GENDER_DICT:
                vc = VoiceConfig(language=l, gender=g)
                params = self.c._make_params(vc, None)

                self.assertEqual(params['gender'], GoogleClient.GENDER_DICT[g])
                self.assertEqual(params['language'], l.value)

    def test_make_params_with_detail_only(self):
        detail = {'audio_encoding': texttospeech.enums.AudioEncoding.OGG_OPUS,
                  'gender': texttospeech.enums.SsmlVoiceGender.NEUTRAL,
                  'language': 'ja-JP'}

        params = self.c._make_params(None, detail)

        for k in detail:
            self.assertEqual(detail[k], params[k])

    def test_make_params_with_voice_config_and_detail(self):
        detail = {'audio_encoding': texttospeech.enums.AudioEncoding.OGG_OPUS,
                  'gender': texttospeech.enums.SsmlVoiceGender.NEUTRAL,
                  'language': 'ja-JP'}
        vc = VoiceConfig(audio_format=AudioFormat.mp3,
                         gender=Gender.female,
                         language=Language.it_IT)
        params = self.c._make_params(vc, detail)

        # detail overwrites values
        self.assertNotEqual(params['audio_encoding'],
                            texttospeech.enums.AudioEncoding.MP3)
        self.assertEqual(params['audio_encoding'], detail['audio_encoding'])

        self.assertNotEqual(params['gender'],
                            texttospeech.enums.SsmlVoiceGender.FEMALE)
        self.assertEqual(params['gender'], detail['gender'])

        self.assertNotEqual(params['language'], 'it-IT')
        self.assertEqual(params['language'], detail['language'])

    def test_auth_before_tts(self):
        txt = 'Hello world'

        self.assertRaises(CloudTTSError, lambda: self.c.tts(txt))

    def test_error_without_data(self):
        self.c.auth('/path/to/google/credential.json')

        self.assertRaises(ValueError, lambda: self.c.tts())

    def test_acceptable_text_length(self):
        self.c.auth('/path/to/google/credential.json')

        text = 'a' * GoogleClient.MAX_TEXT_LENGTH

        # raise TypeError not to call API and
        # to make sure MAX_TEXT_LENGTH works
        self.assertRaises(TypeError,
                          lambda: self.c.tts(
                              text=text,
                              voice_config=True,
                          ))

    def test_error_with_too_long_text(self):
        self.c.auth('/path/to/google/credential.json')

        text = 'a' * (GoogleClient.MAX_TEXT_LENGTH+1)

        # CloudTTSError is raised with too long text
        self.assertRaises(CloudTTSError, lambda: self.c.tts(text=text))

    def test_error_with_too_long_ssml(self):
        self.c.auth('/path/to/google/credential.json')

        text = 'a' * GoogleClient.MAX_TEXT_LENGTH

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
        self.c.auth('/path/to/google/credential.json')

        text = 'a' * GoogleClient.MAX_TEXT_LENGTH
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


if __name__ == '__main__':
    unittest.main()
