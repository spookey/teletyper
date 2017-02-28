from logging import getLogger

from teletyper.lib.disk import read_yaml, write_yaml


class Conf(object):
    def __init__(self, config_file, speech_file):
        self.log = getLogger(__name__)
        self.config_file = config_file
        self._config_data = read_yaml(self.config_file, fallback={})
        self.speech_file = speech_file
        self._speech_data = read_yaml(self.speech_file, fallback={})
        self.check()
        self.log.debug('%s init done', __name__)

    def handle(self, target, source, location):
        missing = []
        for name, default in source.items():
            value = target.get(name, default)
            if not value or value == default:
                missing.append(name)
            target[name] = value

        if missing:
            self.log.error('values missing "%s"', '", "'.join(missing))
        self.log.info('saving conf to file "%s"', location)
        write_yaml(location, content=target)

    def check(self):
        self.handle(self._config_data, self.config_default, self.config_file)
        self.handle(self._speech_data, self.speech_default, self.speech_file)

    def __getattr__(self, name):
        if name in self._config_data.keys():
            return self._config_data[name]
        elif name in self._speech_data.keys():
            return self._speech_data[name]
        else:
            raise AttributeError

    empty = ([''], [], '')
    config_default = dict(
        post_title_fmt='%Y-%m-%d %H:%M:%S',
        telegram_token='',
        telegram_trusted_ids=[],
        tumblr_blog_name='',
        tumblr_consumer_key='',
        tumblr_consumer_secret='',
        tumblr_oauth_secret='',
        tumblr_oauth_token='',
        vimeo_client_id='',
        vimeo_client_secret='',
        vimeo_token='',
    )
    speech_default = dict(
        bot_error_quota=['''
*ERROR* no quota left

You remember that mail server?
        '''.strip(), '''
*ERROR* no quota left

You feed me too much, I am sick.
        '''.strip()],
        bot_error_too_big=['''
*ERROR* file too big

The api won't deliver..
        '''.strip(), '''
*ERROR* file too big

Try two half-length versions instead :)
        '''.strip()],
        bot_error_video=['''
*ERROR* video upload failed

I am so sorry.
        '''.strip(), '''
*ERROR* video upload failed

I feel miserable.
        '''.strip()],
        bot_help=['''
No, you help me!

*Send pictures and videos for {blog_name}*
>> {blog_url} <<

{blog_description}
        '''.strip(), '''
Yes, this is Dog?!

*{blog_name} needs your pictures and videos*
>> {blog_url} <<

{blog_description}
        '''.strip()],

        bot_photo_public=['''
I see what you did there!
>> {short_url} <<
        '''.strip(), '''
Very nice!
>> {short_url} <<
        '''.strip()],

        bot_photo_wait=['''
Ok!
>> will be published soon <<
        '''.strip(), '''
Nice!
>> just wait till it gets published <<
        '''.strip()],

        bot_start=['''
*Welcome!*

See some crazy stuff here:
>> {blog_url} <<
        '''.strip(), '''
*Well hello there!*

Get fresh updates from here:
>> {blog_url} <<
        '''.strip()],

        bot_video_public=['''
Well done!
>> {short_url} <<
        '''.strip(), '''
Moving pictures!
>> {short_url} <<
        '''.strip()],

        bot_video_wait=['''
Success!
>> will be published soon <<
        '''.strip(), '''
Great!
>> just wait till it gets published <<
        '''.strip()],
    )
