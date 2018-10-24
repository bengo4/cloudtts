__version__ = '0.0.2'

from .client import CloudTTSError

from .client import AudioFormat
from .client import Gender
from .client import Language
from .client import VoiceConfig

from .aws import PollyClient, PollyCredential
from .google import GoogleClient
from .ibm import WatsonClient, WatsonCredential
from .microsoft import AzureClient, AzureCredential
