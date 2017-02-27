from teletyper.blog import Blog
from teletyper.chat import Chat
from teletyper.vlog import Vlog


def run_bot(conf):
    blog = Blog(conf)
    chat = Chat(conf, blog, Vlog(conf, blog))
    return chat()


RUN_MODES = dict(bot=run_bot)
