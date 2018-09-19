from .client import CloudTTSError

from .client import AudioFormat
from .client import Gender
from .client import Language
from .client import VoiceConfig

from .aws import PollyClient, PollyCredential
from .google import GoogleClient
from .ibm import WatsonClient
from .microsoft import AzureClient
