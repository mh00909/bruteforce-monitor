roles = {
    "admin": ["block_ip", "unblock_ip", "view_data"],
    "user": ["view_data"]
}

def has_permission(role, permission):
    return permission in roles.get(role, [])
