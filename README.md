# RandomSakuga
A Python script that uses the moebooru API to communicate with [Sakugabooru](https://www.sakugabooru.com) to fetch a random animated video. The Video is then posted to Facebook using the Graph API along with some info like the artist name, the media title (movie/TV show/OVA/etc) and a possible link to MyAnimeList queried using the Jikan API if the media is eastern.

## INSTALL
    pipx install git+https://github.com/TheDL98/RandomSakuga

## USAGE
There are multiple modes of operation
1. You can use the config file provided to configure the bot to start posting on certain time every day
2. You can use the config file to make the bot to post once immediately, then quit.
3. You can use the config file to make the bot post immediately, then post on a certain time every day.
4. You can use the provided systemd timer unit to make the bot post every day at a certain time
5. Or you can use the provided systemd service 


## TODO
- [ ] Add current step status
- [ ] Add standard input options that override the config file
