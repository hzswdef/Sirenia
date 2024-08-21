from nextcord import Member, User

from tools.database import Database


class Level(object):

    def __init__(self, database: Database) -> None:
        self.database = database

    def _is_user_exist(self, uid: int) -> bool:
        data = self.database.query(
            "SELECT `uid` FROM `users`"
            f" WHERE `uid` = {uid}",
            return_output=True,
        )

        return bool(data)

    def _create_user(self, uid: int) -> None:
        self.database.query(
            "INSERT INTO `users`"
            " (`uid`, `messages`, `voice_activity`)"
            f" VALUES ({uid}, 0, 0)"
        )

    def on_message(self, user: User | Member) -> None:
        if not self._is_user_exist(user.id):
            self._create_user(user.id)

        self.database.query(
            "UPDATE `users`"
            " SET `messages` = `messages` + 1"
            f" WHERE `uid` = {user.id}"
        )

    def on_voice_activity(self, user: User | Member, join_on: int, left_on: int) -> None:
        if not self._is_user_exist(user.id):
            self._create_user(user.id)

        total = left_on - join_on

        self.database.query(
            "UPDATE `users`"
            f" SET `voice_activity` = `voice_activity` + {total}"
            f" WHERE `uid` = {user.id}"
        )

        self.database.query(
            "INSERT INTO `voice_activity_history`"
            " (`uid`, `join_on`, `left_on`, `total`)"
            f" VALUES ({user.id}, {join_on}, {left_on}, {total})"
        )
