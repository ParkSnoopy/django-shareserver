from datetime import datetime, timedelta, timezone



class FilePermissionHandler:
    def __init__(self, permission_lifetime_in_minute=5):
        """
        Only when single FPH is running, works stable
        Replace `dict` into shared DB for multithreaded runner

        Dict[ session_id: Set{} ]
        """
        self.container = dict()
        self.permission_lifetime_in_minute = permission_lifetime_in_minute

    # Getter/Setter for Container
    def get_container(self, session_id):
        return self.container.get(session_id, set())
    def set_container(self, session_id, container:set):
        self.container[session_id] = container


    def update_permission(self, session_id):
        # Get session's old permission list
        container = self.get_container(session_id)

        # Remove expired permission
        to_remove = []
        for obj_dt in container:
            _, dt = obj_dt
            if datetime.now(tz=timezone.utc) > dt:
                to_remove.append(obj_dt)
        for obj_dt in to_remove:
            container.remove(obj_dt)

        # Replace session permission list to latest
        self.set_container(session_id, container)

    def set_permission(self, session_id, filename):
        self.container[session_id]: set = self.get_container(session_id) | {(
            filename,
            datetime.now(tz=timezone.utc) + timedelta(minutes=self.permission_lifetime_in_minute)
        )}

    def check_permission(self, session_id, filename, _debug=False) -> bool:
        self.update_permission(session_id)
        container = self.get_container(session_id)

        if _debug:
            print()
            print(f"  Searching for : `{filename}`")
            print(f"  From Container: ID={id(self)}")
            print("\n".join( f"    <PermissionObject: {obj=}, {dt=}>" for obj, dt in container))
            print()

        if filename in ( obj for obj, _ in container ):
            return True
        return False
