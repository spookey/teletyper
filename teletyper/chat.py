from logging import getLogger
from pprint import pformat
from random import choice

from pytz import utc
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from tzlocal import get_localzone


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
                MessageHandler(
                    Filters.photo | Filters.forwarded, self.bot_photo
                ),
                MessageHandler(
                    Filters.video | Filters.forwarded, self.bot_video
                ),
        ]:
            self.updater.dispatcher.add_handler(handler)
        self.updater.dispatcher.add_error_handler(self.bot_error)
        self.log.info('ok, go!')

    def log_update(self, update, text):
        def _up(data):
            if not data:
                return '-'
            return pformat(getattr(data, '__dict__', data))

        self.log.info('\n    '.join([
            'bot update ->', text, '\n',
            'update', _up(update),
            'message', _up(update.message),
            'from_user', _up(update.message.from_user),
            'chat', _up(update.message.chat),
            'photo', _up(update.message.photo),
            'video', _up(update.message.video),
        ]))

    def title(self, update):
        ltz = get_localzone()
        dts = update.message.date.replace(tzinfo=utc).astimezone(ltz)
        return dts.strftime(self.conf.post_title_fmt)

    def trusted(self, update):
        return update.message.chat.id in self.conf.telegram_trusted_ids

    def tags(self, update):
        res = [self.conf.app_name]
        if update.message.chat.type == 'group':
            res.append(update.message.chat.title.lower())
        return res

    def reply(self, update, text, preview=True):
        self.log.debug('send reply "%s"', text)
        update.message.reply_text(
            text, parse_mode='markdown',
            disable_web_page_preview=(not preview)
        )

    def bot_error(self, _, update, error):
        self.log_update(update, error)
        self.log.error('update caused error "%s', error)

    def bot_start(self, _, update):
        self.log_update(update, '/start')
        self.reply(
            update, mixer(
                self.conf.bot_cmd_start,
                self.conf.bot_cmd_start_add,
                '', '>>> {} <<<'.format(self.blog.info['url'])
            ), preview=False,
        )

    def bot_help(self, _, update):
        self.log_update(update, '/help')
        self.reply(
            update, mixer(
                self.conf.bot_cmd_help,
                self.conf.bot_cmd_help_add,
                '', '>>> {} <<<'.format(self.blog.info['url']),
                '', self.blog.info['description'],
                blog_name=self.blog.info['name'],
            ), preview=True
        )

    def bot_photo(self, bot, update):
        if not update.message.photo:
            return
        self.log_update(update, 'photo')

        public = self.trusted(update)
        source = bot.getFile(sorted(
            update.message.photo, key=lambda ph: ph.width * ph.height
        )[-1].file_id).file_path
        post = self.blog.post_photo(
            source, caption=update.message.caption, public=public,
            tags=self.tags(update), title=self.title(update),
        )
        if not post:
            self.reply(update, mixer(
                self.conf.bot_err_post, self.conf.bot_err_post_add
            ))
        else:
            self.reply(update, mixer(self.conf.bot_trg_intro, '', (
                '>>> {} <<<'.format(post['short_url'])
                if public else self.conf.bot_trg_wait
            )))

    def bot_video(self, bot, update):
        if not update.message.video:
            return
        self.log_update(update, 'video')

        public = self.trusted(update)
        tags = self.tags(update)
        title = self.title(update)

        if update.message.video.file_size > (1024 * 1024) * 20:
            return self.reply(update, mixer(
                self.conf.bot_err_large, self.conf.bot_err_large_add
            ))
        if not self.vlog.quota(update.message.video.file_size):
            return self.reply(update, mixer(
                self.conf.bot_err_quota, self.conf.bot_err_quota_add
            ))
        source = bot.getFile(update.message.video.file_id).file_path
        upload = self.vlog.upload(source)
        if not upload:
            return self.reply(update, mixer(
                self.conf.bot_err_upload, self.conf.bot_err_upload_add
            ))

        video = self.vlog.change(
            upload, caption=update.message.caption,
            public=public, tags=tags, title=title,
        )
        if not video:
            return self.reply(update, mixer(
                self.conf.bot_err_change, self.conf.bot_err_change_add
            ))

        post = self.blog.post_video(
            video['embed']['html'], caption=update.message.caption,
            public=public, tags=tags, title=title,
        )
        if not post:
            self.reply(update, mixer(
                self.conf.bot_err_post, self.conf.bot_err_post_add
            ))
        else:
            self.reply(update, mixer(self.conf.bot_trg_intro, '', (
                '>>> {} <<<'.format(post['short_url'])
                if public else self.conf.bot_trg_wait
            )), preview=False)

    def __call__(self):
        self.setup()
        self.updater.start_polling()
        self.updater.idle()
        self.updater.stop()
        self.log.info('good bye!')
        return True


def mixer(*elems, **kwargs):
    return '\n'.join([(
        choice(elem) if isinstance(elem, (list, tuple)) else elem
    ) for elem in elems]).format(**kwargs)
