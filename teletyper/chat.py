from logging import getLogger
from pprint import pformat
from random import choice

from pytz import utc
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from tzlocal import get_localzone

from teletyper.lib import APP_NAME


class Chat(object):
    def __init__(self, conf, blog, vlog):
        self.log = getLogger(__name__)
        self.conf = conf
        self.blog = blog
        self.vlog = vlog

        self.updater = Updater(token=self.conf.telegram_token)
        self.log.debug('%s init done', __name__)

    def setup(self):
        for handler in [
                CommandHandler('start', self.bot_start),
                CommandHandler('help', self.bot_help),
                MessageHandler((
                    Filters.photo | Filters.video | Filters.forwarded
                ), self.bot_trigger)
        ]:
            self.updater.dispatcher.add_handler(handler)
        self.updater.dispatcher.add_error_handler(self.bot_error)
        self.log.info('ok, go!')

    def log_update(self, update, text):
        def _up(data):
            return pformat(getattr(data, '__dict__', data))

        self.log.info('\n    '.join([
            'bot update ->', text, '\n',
            'update', _up(update),
            'message', _up(update.message),
            'from_user', _up(update.message.from_user),
            'chat', _up(update.message.chat),
            'photo', _up(update.message.photo),
            'video', _up(update.message.photo),
        ]))

    def title(self, dts):
        dts = dts.replace(tzinfo=utc).astimezone(get_localzone())
        return dts.strftime(self.conf.post_title_fmt)

    def reply(self, update, choices, _preview=True, **formats):
        message = choice(choices).format(**formats)
        self.log.debug('send reply "%s"', message)
        update.message.reply_text(
            message, parse_mode='markdown',
            disable_web_page_preview=(not _preview)
        )

    def bot_error(self, _, update, error):
        self.log_update(update, error)
        self.log.error('update caused error "%s', error)

    def bot_start(self, _, update):
        self.log_update(update, '/start')
        self.reply(
            update, self.conf.bot_start, _preview=False,
            blog_url=self.blog.info['url']
        )

    def bot_help(self, _, update):
        self.log_update(update, '/help')
        self.reply(
            update, self.conf.bot_help,
            blog_url=self.blog.info['url'],
            blog_description=self.blog.info['description'],
            blog_name=self.blog.info['name'],
        )

    def handle_photo(self, bot, update, *, public, **kwargs):
        source = bot.getFile(sorted(
            update.message.photo, key=lambda ph: ph.width * ph.height
        )[-1].file_id).file_path
        photo = self.blog.post_photo(
            source, caption=update.message.caption, public=public, **kwargs
        )
        return (
            self.conf.bot_photo_public if public else self.conf.bot_photo_wait,
            photo
        )

    def handle_video(self, bot, update, *, public, **kwargs):
        source = bot.getFile(update.message.video.file_id).file_path
        if not self.vlog.check_quota(update.message.video.file_size):
            return (self.conf.bot_error_quota, dict())
        embed = self.vlog.post_video(
            source, caption=update.message.caption, public=public, **kwargs
        )
        if not embed:
            return (self.conf.bot_error_video, dict())
        video = self.blog.post_video(
            embed, caption=update.message.caption, public=public, **kwargs
        )
        return (
            self.conf.bot_video_public if public else self.conf.bot_video_wait,
            video
        )

    def bot_trigger(self, bot, update):
        self.log_update(update, 'trigger')

        tags = [APP_NAME]
        if update.message.chat.type == 'group':
            tags.append(update.message.chat.title.lower())
        title = self.title(update.message.date)
        public = (update.message.chat.id in self.conf.telegram_trusted_ids)

        if update.message.photo:
            message, post = self.handle_photo(
                bot, update, public=public, tags=tags, title=title
            )
        elif update.message.video:
            message, post = self.handle_video(
                bot, update, public=public, tags=tags, title=title
            )
        else:
            return
        self.reply(update, message, **post)

    def __call__(self):
        self.setup()
        self.updater.start_polling()
        self.updater.idle()
        self.updater.stop()
        self.log.info('good bye!')
        return True
