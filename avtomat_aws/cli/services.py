SERVICES = {
    "backup": ["create_backups", "delete_backups"],
    "cloudtrail": [
        "discover_user_events",
        "discover_resource_events",
        "discover_events",
    ],
    "ec2": [
        "copy_snapshots",
        "create_images",
        "create_snapshots",
        "delete_images",
        "delete_instances",
        "delete_security_groups",
        "delete_snapshots",
        "delete_volumes",
        "discover_active_regions",
        "discover_default_ebs_encryption",
        "discover_images",
        "discover_instances",
        "discover_no_ssm_instances",
        "discover_snapshots",
        "discover_tags",
        "discover_unused_security_groups",
        "discover_volumes",
        "encrypt_instance_volumes",
        "encrypt_volume",
        "modify_default_ebs_encryption",
        "modify_tags",
        "modify_volumes",
        "share_snapshots",
    ],
    "general": ["get_date"],
    "iam": [
        "discover_inactive_console_users",
        "discover_inactive_users",
        "discover_no_mfa_users",
        "discover_old_access_keys",
        "discover_old_password_users",
        "discover_unused_access_keys",
        "discover_unused_roles",
        "modify_access_keys",
        "modify_users_console_access",
        "quarantine_user",
    ],
    "sts": ["create_session", "whoami"],
    "s3": ["create_objects", "delete_objects", "discover_objects"],
}
