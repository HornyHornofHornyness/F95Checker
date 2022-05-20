import subprocess
import pathlib
import shlex
import time
import stat
import os

from modules.structs import Browser, Game, MsgBox, Os
from modules.remote import async_thread, filepicker
from modules import globals, db, utils


def _launch(path: str | pathlib.Path):
    exe = pathlib.Path(path).absolute()
    if not exe.is_file():
        raise FileNotFoundError()

    if globals.os is Os.Windows:
        # Open with default app
        os.startfile(str(exe))
    else:
        mode = exe.stat().st_mode
        executable = not (mode & stat.S_IEXEC < stat.S_IEXEC)
        if not executable:
            with exe.open("r") as f:
                if f.read(2) == "#!":
                    # Make executable if shebang is present
                    exe.chmod(mode | stat.S_IEXEC)
                    executable = True
        if (exe.parent / "renpy").is_dir():
            # Make all needed renpy libs executable
            for file in (exe.parent / "lib").glob("**/*"):
                if file.is_file() and not file.suffix:
                    mode = file.stat().st_mode
                    if mode & stat.S_IEXEC < stat.S_IEXEC:
                        file.chmod(mode | stat.S_IEXEC)
        if executable:
            # Run as executable
            subprocess.Popen(
                [
                    str(exe)
                ],
                cwd=str(exe.parent),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Open with default app
            if globals.os is Os.Linux:
                open_util = "xdg-open"
            elif globals.os is Os.MacOS:
                open_util = "open"
            subprocess.Popen(
                [
                    open_util,
                    str(exe)
                ],
                cwd=str(exe.parent),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )


def launch_game_exe(game: Game):
    def _launch_game():
        if not game.executable:
            return
        try:
            _launch(game.executable)
            game.last_played.update(time.time())
            async_thread.run(db.update_game(game, "last_played"))
        except FileNotFoundError:
            def reset_callback():
                game.executable = ""
                async_thread.run(db.update_game(game, "executable"))
            buttons = {
                "󰄬 Yes": reset_callback,
                "󰜺 No": None
            }
            utils.push_popup(globals.gui.draw_msgbox, "File not found!", "The selected executable could not be found.\n\nDo you want to unset the path?", MsgBox.warn, buttons)
        except Exception:
            utils.push_popup(globals.gui.draw_msgbox, "Oops!", f"Something went wrong launching {game.name}:\n\n{utils.get_traceback()}", MsgBox.error)
    if not game.executable:
        def select_callback(selected):
            if selected:
                game.executable = selected
                async_thread.run(db.update_game(game, "executable"))
                _launch_game()
        utils.push_popup(filepicker.FilePicker(f"Select executable for {game.name}", callback=select_callback).tick)
    else:
        _launch_game()


def open_game_folder(game: Game):
    dir = pathlib.Path(game.executable).absolute().parent
    if not dir.is_dir():
        def reset_callback():
            game.executable = ""
            async_thread.run(db.update_game(game, "executable"))
        buttons = {
            "󰄬 Yes": reset_callback,
            "󰜺 No": None
        }
        utils.push_popup(globals.gui.draw_msgbox, "No such folder!", "The parent folder for the game executable could not be found.\n\nDo you want to unset the path?", MsgBox.warn, buttons)
    if globals.os is Os.Windows:
        os.startfile(str(dir))  # TODO: Needs testing
    else:
        if globals.os is Os.Linux:
            open_util = "xdg-open"
        elif globals.os is Os.MacOS:
            open_util = "open"
        subprocess.Popen(
            [
                open_util,
                str(dir)
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def open_webpage(url: str):
    set = globals.settings
    if set.browser is Browser._None:
        utils.push_popup(globals.gui.draw_msgbox, "Browser", "Please select a browser in order to open webpages!", MsgBox.warn)
        return
    # TODO: download pages
    name = set.browser.name
    if set.browser is Browser.Custom:
        name = "your browser"
        path = set.browser_custom_executable
        args = shlex.split(set.browser_custom_arguments)
    else:
        path = set.browser.path
        args = []
        if set.browser_private:
            args.append(set.browser.private)
    try:
        subprocess.Popen(
            [
                path,
                *args,
                url
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        utils.push_popup(globals.gui.draw_msgbox, "Oops!", f"Something went wrong opening {name}:\n\n{utils.get_traceback()}", MsgBox.error)


def remove_game(game: Game):
    def remove_callback():
        id = game.id
        del globals.games[id]
        globals.gui.require_sort = True
        async_thread.run(db.remove_game(id))
        for img in globals.images_path.glob(f"{id}.*"):
            try:
                img.unlink()
            except Exception:
                pass
    if globals.settings.confirm_on_remove:
        buttons = {
            "󰄬 Yes": remove_callback,
            "󰜺 No": None
        }
        utils.push_popup(globals.gui.draw_msgbox, "Remove game", f"Are you sure you want to remove {game.name} from your list?", MsgBox.warn, buttons)
    else:
        remove_callback()
