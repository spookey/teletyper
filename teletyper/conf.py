from logging import getLogger

from teletyper.lib import APP_NAME
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
            if not value or value in self.empty:
                missing.append(name)
            target[name] = value

        if missing:
            self.log.warning('values missing "%s"', '", "'.join(missing))
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

    empty = ([], '')
    config_default = dict(
        app_name=APP_NAME,
        post_title_fmt='%Y_%m_%d-%H_%M_%S',
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
        bot_cmd_help=[
            'No, you help me!',
            'Yes, this is Dog?!',
        ],
        bot_cmd_help_add=[
            '*Send pictures and videos for {blog_name}*',
            '*{blog_name} needs your pictures and videos*',
        ],
        bot_cmd_start=[
            '*Welcome!*',
            '*Well hello there!*',
        ],
        bot_cmd_start_add=[
            'See some crazy stuff here',
            'Get fresh updates from here',
        ],
        bot_err_change='*ERROR* could not edit file info',
        bot_err_change_add=[
            'Could there someone look into it?',
            'Someone should really fix that!',
        ],
        bot_err_large='*ERROR* file is too large',
        bot_err_large_add=[
            'The telegram api won\'t deliver..',
            'Try two half-length versions instead :)',
        ],
        bot_err_post='*ERROR* could not post',
        bot_err_post_add=[
            'Something is somewhere broken',
            'Kopfweh!',
            'Sorry!',
        ],
        bot_err_quota='*ERROR* no quota left',
        bot_err_quota_add=[
            'You feed me too much, I am sick.',
            'You remember that mail server?',
        ],
        bot_err_upload='*ERROR* could not upload file',
        bot_err_upload_add=[
            'I am so sorry.',
            'I feel miserable.',
        ],
        bot_trg_intro=[
            'Erfolg!',
            'I see what you did there!',
            'Nice!',
            'Ok!',
            'Success!',
            'Very nice!',
            'Well done!',
        ],
        bot_trg_wait=[
            'Be patient, will be published soon..',
            'Just wait till it gets published..',
            'Will be published soon!',
        ]
    )
