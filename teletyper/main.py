from teletyper.blog import Blog
from teletyper.chat import Chat
from teletyper.pull import Pull
from teletyper.vlog import Vlog


def run_bot(conf):
    blog = Blog(conf)
    vlog = Vlog(conf, blog)
    chat = Chat(conf, blog, vlog)
    return chat()


def run_archive(conf):
    blog = Blog(conf)
    vlog = Vlog(conf, blog)
    pull = Pull(conf, blog, vlog)
    return pull()


RUN_MODES = dict(archive=run_archive, bot=run_bot)
