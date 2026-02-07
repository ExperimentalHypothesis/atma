from flask import current_app as app


def getCurrentSong() -> dict:
    if app.config["FLASK_ENV"] == "development":
        return dict(author="name of author", title="name of title")
    else:
        try:
            with open(app.config["ICES_CUE_CHANNEL1"]) as f:
                lines = [line for line in f]
                author = lines[-2].strip().lower()
                title = lines[-1].strip().lower()
        except Exception as e:
            return dict(author="unknown artists", title="unknown song")

        return dict(title=title, author=author)