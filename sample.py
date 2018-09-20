from cloudtts import AzureClient, AzureCredential
from cloudtts import GoogleClient
from cloudtts import PollyClient, PollyCredential
from cloudtts import WatsonClient, WatsonCredential

from cloudtts import VoiceConfig
from cloudtts import Gender
from cloudtts import Language

enVC = VoiceConfig()
jaVC = VoiceConfig(language=Language.ja_JP, gender=Gender.male)


def _azure():
    cred = AzureCredential(api_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    c = AzureClient(cred)

    # English US
    audio = c.tts('Hi there, it is too hot today.', voice_config=enVC)
    with open('azure_hot_en.mp3', 'wb') as f:
        f.close(audio)

    # English US with SSML
    audio = c.tts(
        '<speak>Hi there,<break time="1s" /> it is too hot today.</speak>',
        voice_config=enVC
    )
    with open('azure_hot_en_ssml.mp3', 'wb') as f:
        f.close(audio)

    # Japanese
    audio = c.tts('今日はすごく暑いですね。', voice_config=jaVC)
    with open('azure_hot_ja.mp3', 'wb'):
        f.close(audio)


def _google():
    c = GoogleClient('/path/to/google_credential.json')

    # English US
    audio = c.tts('Hi there, it is too hot today.', voice_config=enVC)
    with open('google_hot_en.mp3', 'wb') as f:
        f.write(audio)

    # English US with SSML
    ssml = '<speak>Hi there,<break time="1s" /> it is too hot today.</speak>'
    audio = c.tts(ssml=ssml, voice_config=enVC)
    with open('google_hot_en_ssml.mp3', 'wb') as f:
        f.write(audio)

    # Japanese
    audio = c.tts('今日はすごく暑いですね。', voice_config=jaVC)
    with open('google_hot_ja.mp3', 'wb') as f:
        f.write(audio)


def _polly():
    cred = PollyCredential(
        aws_access_key_id='XXXXXXXXXXXXXXXXXXXX',
        aws_secret_access_key='YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',
        region_name='ap-northeast-1'
    )
    c = PollyClient(cred)

    # English US
    audio = c.tts('Hi there, it is too hot today.', voice_config=enVC)
    with open('polly_hot_en.mp3', 'wb') as f:
        f.write(audio)

    # English US with SSML
    ssml = '<speak>Hi there,<break time="1s" /> it is too hot today.</speak>'
    audio = c.tts(ssml=ssml, voice_config=enVC)
    with open('polly_hot_en_ssml.mp3', 'wb') as f:
        f.write(audio)

    # Japanese
    c.tts('今日はすごく暑いですね。', voice_config=jaVC)
    with open('polly_hot_ja.mp3', 'wb') as f:
        f.write(audio)


def _watson():
    cred = WatsonCredential(
        url='https://stream.watsonplatform.net/text-to-speech/api',
        username='XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX',
        password='YYYYYYYYYYYY',
    )
    c = WatsonClient(cred)

    # English US
    audio = c.tts('Hi there, it is too hot today.', voice_config=enVC)
    with open('watson_hot_en.mp3', 'wb') as f:
        f.write(audio)

    # English US with SSML
    audio = c.tts(
        '<speak>Hi there,<break time="1s" /> it is too hot today.</speak>',
        voice_config=enVC
    )
    with open('watson_hot_en_ssml.mp3', 'wb') as f:
        f.close(audio)

    # Japanese
    audio = c.tts('今日はすごく暑いですね。', voice_config=jaVC)
    with open('watson_hot_ja.mp3', 'wb') as f:
        f.write(audio)


if __name__ == '__main__':
    _azure()
    _google()
    _polly()
    _watson()
