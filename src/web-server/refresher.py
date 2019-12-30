from multiprocessing import Process, active_children

from flask import redirect

from constants import CSV_ROOT

from authorized_staff import setup_authorized_staff
from named_shortlinks import setup_named_shortlinks
from preloaded_tables import setup_preloaded_tables
from shortlink_generator import setup_shortlink_generator
from shortlink_paths import setup_shortlink_paths
from stored_files import setup_stored_files


def create_refresher(app):
    @app.route("/data/registry")
    def registry():
        return redirect(CSV_ROOT)

    @app.route("/data/refresh")
    def sync_refresh():
        refresh()
        return (
            "Success! All public shortlinks, members of staff, and stored files successfully updated!",
            200,
        )

    @app.route("/api/async_refresh", methods=["POST"])
    @app.route("/api/_async_refresh", methods=["POST"])  # deprecated
    def async_refresh():
        active_children()  # kills zombies
        p = Process(target=refresh)
        p.start()
        return "", 204

    def refresh():
        for f in setup_funcs:
            f()


setup_funcs = [
    setup_authorized_staff,
    setup_named_shortlinks,
    setup_preloaded_tables,
    setup_shortlink_generator,
    setup_shortlink_paths,
    setup_stored_files,
]
