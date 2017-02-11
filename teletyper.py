from argparse import ArgumentParser
from logging import DEBUG, Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler
from os import makedirs, path
from pprint import pformat

from pytumblr import TumblrRestClient
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def parse():
    prs = ArgumentParser('doc_telex')
    prs.add_argument(
        '--log-file', dest='log_file',
        action='store', help='log file location', default='log/log.log'
    )
    prs.add_argument(
        '--telegram-token', dest='telegram_token',
        action='store', help='telegram bot token', required=True
    )
    prs.add_argument(
        '--tumblr-consumer-key', dest='tumblr_consumer_key',
        action='store', help='tumblr consumer key', required=True
    )
    prs.add_argument(
        '--tumblr-consumer-secret', dest='tumblr_consumer_secret',
        action='store', help='tumblr consumer secret', required=True
    )
    prs.add_argument(
        '--tumblr-oauth-token', dest='tumblr_oauth_token',
        action='store', help='tumblr oauth token', required=True
    )
    prs.add_argument(
        '--tumblr-oauth-secret', dest='tumblr_oauth_secret',
        action='store', help='tumblr oauth secret', required=True
    )
    prs.add_argument(
        '--tumblr-blog-name', dest='tumblr_blog_name',
        action='store', help='tumblr blog name', required=True
    )
    prs.add_argument(
        '--tumblr-blog-state', dest='tumblr_blog_state',
        action='store', help='tumblr blog entry state', required=True,
        choices=['published', 'draft', 'queue', 'private']
    )

    return prs.parse_args()


def logger(log_file):
    log = getLogger()
    formatter = Formatter('''
%(levelname)s - %(asctime)s %(name)s.%(funcName)s() [%(pathname)s%(lineno)d]
    %(message)s
'''.lstrip())
    log_file = path.abspath(path.expanduser(log_file))
    if not path.exists(path.dirname(log_file)):
        makedirs(path.dirname(log_file))

    stream = StreamHandler(stream=None)
    stream.setFormatter(formatter)
    stream.setLevel(DEBUG)

    bucket = RotatingFileHandler(
        log_file, maxBytes=(1024 * 1024), backupCount=9
    )
    bucket.setFormatter(formatter)
    bucket.setLevel(DEBUG)

    log.setLevel(DEBUG)
    log.addHandler(stream)
    log.addHandler(bucket)
    return log


class Telex(object):
    def __init__(self, args):
        self.log = logger(args.log_file)
        self.tumblr_client = TumblrRestClient(
            args.tumblr_consumer_key,
            args.tumblr_consumer_secret,
            args.tumblr_oauth_token,
            args.tumblr_oauth_secret
        )
        self.telegram_updater = Updater(token=args.telegram_token)
        self.tumblr_blog = self._pull_blog(args.tumblr_blog_name)
        self.tumblr_state = args.tumblr_blog_state
        for handler in [
                CommandHandler('start', self.bot_start),
                CommandHandler('help', self.bot_help),
                MessageHandler((
                    Filters.photo | Filters.forwarded
                ), self.bot_photo),
        ]:
            self.telegram_updater.dispatcher.add_handler(handler)
        self.telegram_updater.dispatcher.add_error_handler(self.bot_error)
        self.log.info('ok go!')

    def _pull_blog(self, name):
        return [
            bl for bl in self.tumblr_client.info()['user']['blogs']
            if bl['name'] == name
        ][-1]

    def bot_error(self, bot, update, error):
        self.log.error('update "{}" caused error: "{}"'.format(
            pformat(update), error
        ))

    def bot_start(self, bot, update):
        update.message.reply_text(
            '''
welcome!

>> {url} <<
            '''.strip().format(url=self.tumblr_blog['url']),
            parse_mode='markdown', disable_web_page_preview=False
        )

    def bot_help(self, bot, update):
        update.message.reply_text(
            '''
no, you help me!
send pictures for {name}!!1!1

>> {url} <<

{desc}
            '''.strip().format(
                name=self.tumblr_blog['name'], url=self.tumblr_blog['url'],
                desc=self.tumblr_blog['description']
            ),
            parse_mode='markdown', disable_web_page_preview=True
        )

    def bot_photo(self, bot, update):
        if not update.message.photo:
            return
        photo = bot.getFile(update.message.photo[-1].file_id)
        tumblr_id = self.tumblr_client.create_photo(
            self.tumblr_blog['name'],
            state=self.tumblr_state,
            source=photo.file_path,
            format='markdown',
            tags=['telex'],
            caption='''
by [@{name}]({url}) {extra}
            '''.strip().format(
                name=update.message.from_user.username,
                url='http://t.me/{}'.format(update.message.from_user.username),
                extra=(
                    'via #{}'.format(update.message.chat.title) if
                    update.message.chat.type == 'group' else ''
                )
            )
        )['id']
        tumblr_post = self.tumblr_client.posts(
            self.tumblr_blog['name'], id=tumblr_id,
        )['posts'][0]

        update.message.reply_text(
            '''
ok!
>> {txt} <<
            '''.strip().format(txt=(
                tumblr_post['short_url'] if tumblr_post['state'] == 'published'
                else 'will be published soon..'
            )),
            parse_mode='markdown', disable_web_page_preview=False
        )

    def __call__(self):
        self.telegram_updater.start_polling()
        self.telegram_updater.idle()
        self.telegram_updater.stop()
        self.log.info('good bye!')
        return True


if __name__ == '__main__':
    exit(Telex(parse())())
