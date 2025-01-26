from ZeMusic.core.bot import Mody
from ZeMusic.core.dir import dirr
from ZeMusic.core.git import git
from ZeMusic.core.userbot import Userbot
from ZeMusic.misc import dbb, heroku
from ZeMusic.core.rd import Rd
from .logging import LOGGER

dirr()
git()
dbb()
heroku()
rd = Rd()
app = Mody()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
