from datetime import datetime, timedelta, timezone



class PermissionHandler:
    def __init__(self, permission_lifetime_in_minute=30):
        self.containers = dict()
        self.permission_lifetime_in_minute = permission_lifetime_in_minute

    def set_perm(self, session_id, shared_object):
        self.containers[session_id]: set =         \
            self.containers.get(session_id, set()) \
            |                                      \
            {(
                shared_object,
                datetime.now(tz=timezone.utc) + timedelta(minutes=self.permission_lifetime_in_minute)
            )}

    def check_perm(self, session_id, target_object, _debug=False):
        corr_container = self.containers.get(session_id, set())
        corr_container = self._perm_expire_check(corr_container)
        self.containers[session_id] = corr_container

        if _debug:
            print()
            print(f"  Searching for : `{target_object}`")
            print("  From Container: ")
            print("\n".join( f"    <PermissionObject: {obj=}, {dt=}>" for obj, dt in corr_container))
            print()

        if target_object in tuple( obj for obj, dt in corr_container):
            return True
        return False

    def _perm_expire_check(self, container:set):
        # print(f"\n  running _perm_expire_check, target {container = }\n")
        rm = []
        for obj_dt in container:
            _, dt = obj_dt
            if datetime.now(tz=timezone.utc) > dt:
                # print(f"    remove {obj_dt}")
                rm.append(obj_dt)
        for obj_dt in rm:
            container.remove(obj_dt)
        # print(f"\n  returning {container = }\n")
        return container


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
            print("  From Container: ID={id(self)}")
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
