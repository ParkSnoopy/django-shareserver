from datetime import datetime, timedelta, timezone



class FilePermissionHandler:
    def __init__(self, permission_lifetime_in_minute=5):
        self.container = dict()
        self.permission_lifetime_in_minute = permission_lifetime_in_minute

    def get_container(self, session_id):
        return self.container.get(session_id, set())

    def set_permission(self, request, filepath):
        session_id = request.session.session_key

        self.container[session_id]: set = self.get_container(session_id) | {(
            filepath,
            datetime.now(tz=timezone.utc) + timedelta(minutes=self.permission_lifetime_in_minute)
        )}

    def check_permission(self, request, filepath, _debug=False):
        session_id = request.session.session_key

        corr_container = self.get_container(session_id)
        corr_container = self._permission_expire_check(corr_container)
        self.container[session_id] = corr_container

        if _debug:
            print()
            print(f"  Searching for : `{filepath}`")
            print(f"  From Container: ID={id(self)}")
            print("\n".join( f"    <PermissionObject: {obj=}, {dt=}>" for obj, dt in corr_container))
            print()

        if filepath in ( obj for obj, dt in corr_container ):
            return True
        return False

    def _permission_expire_check(self, container:set):
        rm = []
        for obj_dt in container:
            _, dt = obj_dt
            if datetime.now(tz=timezone.utc) > dt:
                rm.append(obj_dt)
        for obj_dt in rm:
            container.remove(obj_dt)
        return container
