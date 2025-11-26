### SFTPGo Event Manager Placeholders

Here is the complete list of all available placeholders extracted from the official documentation:  
https://docs.sftpgo.com/enterprise/eventmanager/#placeholders

These placeholders can be used in **HTTP notifications**, **email notifications**, **command hooks**, and **event rules filters** using Go template syntax (e.g., `{{.VirtualPath}}`).

| Placeholder              | Description                                                                                                                      | Additional Notes / Format                                                                 |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `{{.Name}}`              | Username, virtual folder name, admin username for provider events, domain name for TLS certificate events.                       | string                                                                                    |
| `{{.ExtName}}`           | External username, set to the email address used for authenticating public shares configured with email authentication.         | string                                                                                    |
| `{{.Event}}`             | Event name, for example `upload`, `download` for filesystem events or `add`, `update` for provider events.                       | string                                                                                    |
| `{{.Status}}`            | Status for filesystem events. 1 = no error, 2 = generic error, 3 = quota exceeded error.                                         | integer                                                                                   |
| `{{.Errors}}`            | Error details.                                                                                                                   | list of strings                                                                           |
| `{{.VirtualPath}}`       | Path seen by SFTPGo users, e.g., `/adir/afile.txt`.                                                                              | string                                                                                    |
| `{{.FsPath}}`            | Full filesystem path, e.g., `/user/homedir/adir/afile.txt` (or Windows path).                                                    | string                                                                                    |
| `{{.VirtualTargetPath}}` | Virtual target path for rename and copy operations.                                                                              | string                                                                                    |
| `{{.FsTargetPath}}`      | Full filesystem target path for rename and copy operations.                                                                     | string                                                                                    |
| `{{.ObjectName}}`        | File/directory name (e.g., `afile.txt`), or provider object name. For data retention actions, this is the affected username.     | string                                                                                    |
| `{{.ObjectType}}`        | Object type for provider events: `user`, `group`, `admin`, etc.                                                                 | string                                                                                    |
| `{{.FileSize}}`          | File size in bytes.                                                                                                              | int64                                                                                     |
| `{{.Elapsed}}`           | Elapsed time in milliseconds for filesystem events.                                                                             | int64                                                                                     |
| `{{.Protocol}}`          | Used protocol (e.g., `SFTP`, `FTP`, `WebDAV`, `HTTPS`).                                                                          | string                                                                                    |
| `{{.IP}}`                | Client IP address.                                                                                                               | string                                                                                    |
| `{{.Role}}`              | User or admin role.                                                                                                              | string                                                                                    |
| `{{.Email}}`             | Email associated with the user/admin performing or affected by the action. Blank otherwise.                                       | string                                                                                    |
| `{{.Timestamp}}`         | Event timestamp. Supports methods like `.UTC`, `.Local`, `.Unix`, `.Year`, etc.                                                  | time object                                                                               |
| `{{.UID}}`               | Unique internal ID.                                                                                                              | string                                                                                    |
| `{{.Object}}`            | Provider object data (sensitive fields removed). Has `.JSON` method. Can access inner objects like `.Share`, `.User`, etc.       | object (use `{{.Object.JSON}}` or `{{.Object.JSON \| toJson}}`)                           |
| `{{.RetentionReports}}`  | Data retention reports as zip-compressed CSV files (for email attachments or HTTP multipart).                                   | string (usable as file path or attachment)                                                |
| `{{.IDPFields}}`         | Custom fields from the Identity Provider (depends on your IdP configuration).                                                   | object                                                                                    |
| `{{.Metadata}}`          | Cloud storage metadata as key/value string pairs (iterable with `range`).                                                        | object (map[string]string)                                                                |

These are **all** the placeholders available in the latest SFTPGo Enterprise version (as of November 2025). Use them freely in your HTTP body templates, headers, email subjects/bodies, or command arguments!

### SFTPGo Event Hooks Configuration Guide (Open-Source Edition)

SFTPGo's **Event Manager** is the modern, powerful way to configure hooks/actions for filesystem events (upload, download, delete, etc.), provider events (user add/update/delete), scheduled tasks, and more.

It fully replaces the older "custom actions" (global hooks in the main config file) introduced in earlier versions.

#### Key Concepts
- **Rules** — Define **when** a hook triggers (e.g., on upload, on user creation, daily at 02:00).
- **Actions** — Define **what** to do (HTTP call, run command, send email, reset quotas, etc.).
- **Pre-hooks** — Run **before** an operation (e.g., `pre-upload`, `pre-delete`). Require at least one **synchronous** action; if it fails → operation denied.
- **Post-hooks** — Run **after** an operation (default asynchronous).
- Hooks can be global or filtered by user, folder, protocol, IP, etc.

#### Where to Configure
WebAdmin → **Event Manager**  
1. **Actions** → Create reusable actions (HTTP, command, email, etc.)  
2. **Rules** → Combine triggers + conditions + actions

#### Supported Action Types
| Type                  | Description                                      | Sync Support | Typical Use Case |
|-----------------------|--------------------------------------------------|--------------|------------------|
| HTTP notification     | POST/GET/PUT/DELETE to your webhook              | Yes          | Integrate with Slack, Discord, custom API |
| Command               | Execute external script/binary                   | Yes          | Virus scan, post-processing |
| Email                 | Send email via configured SMTP                   | Yes          | Alert admins |
| Backup                | Create full config/data backup                   | No           | Scheduled backups |
| Rotate log            | Force log rotation                               | No           | Daily maintenance |
| User/Folder/Transfer quota reset | Recalculate quotas                            | No           | Scheduled |
| Data retention check  | Apply per-folder retention policies              | No           | Scheduled cleanup |
| Password/User expiration check | Notify/disable expired users                 | No           | Scheduled |
| Filesystem actions    | rename, delete, mkdir, copy, compress, etc.     | Yes          | Auto-organize files |

#### Full Example: HTTP Webhook on Every Upload (Post-Hook)
**Step 1 – Create Action**
```json
{
  "name": "upload_webhook",
  "type": 1,  // 1 = HTTP
  "options": {
    "http_config": {
      "endpoint": "https://mydomain.com/sftpgo-webhook",
      "method": "POST",
      "timeout": 20,
      "headers": {
        "Authorization": "Bearer secret123",
        "Content-Type": "application/json"
      },
      "body_template": "{\n  \"event\": \"{{.Event}}\",\n  \"user\": \"{{.Name}}\",\n  \"path\": \"{{.VirtualPath}}\",\n  \"size\": {{.FileSize}},\n  \"ip\": \"{{.IP}}\",\n  \"timestamp\": \"{{.DateTime}}\"\n}"
    }
  }
}
```

**Step 2 – Create Rule**
- Trigger: **Filesystem events** → check all (upload, download, delete, etc.)
- Conditions: (optional) `Event is upload`
- Actions: select **upload_webhook**
- Execute sync: leave unchecked (asynchronous post-hook)

#### Example: Virus Scan Before Upload (Pre-Hook – Synchronous)
```json
{
  "name": "clamav_scan",
  "type": 2,  // 2 = Command
  "options": {
    "cmd_config": {
      "command": "/usr/bin/clamscan",
      "arguments": ["--no-summary", "{{.FsPath}}"],
      "env": {
        "VIRUS": "clean"
      }
    }
  }
}
```
Then create a rule with trigger **pre-upload** + this action + **Execute sync = checked**.  
If ClamAV returns non-zero → upload denied.

#### Example: Scheduled Daily Backup + Quota Reset
Rule trigger: **Scheduler** → Cron `0 3 * * *` (daily at 03:00 UTC)  
Actions: `backup` + `user_quota_reset` + `transfer_quota_reset`

#### Important Settings
- **Synchronous execution** — Critical for pre-hooks. Long-running sync hooks can cause client timeouts.
- **Stop on failure** — In a rule, stop executing remaining actions if one fails.
- **Placeholders** — Use Go templates `{{.Event}}`, `{{.VirtualPath}}`, `{{.FileSize}}`, etc. (full list in previous message).
- **Command execution disabled by default** — Enable globally in `sftpgo.json` if needed:
  ```json
  "common": {
    "external_commands": {
      "enabled": true
    }
  }
  ```

#### Legacy Global Hooks (Old Method – Still Works but Deprecated)
In older versions (< v2.4) or for very simple cases, you can define global hooks directly in `sftpgo.json` under `common` → `hooks` (for filesystem/SSH events) or `external_auth_hook`, `pre_login_hook`, etc.  
The Event Manager is far more flexible and recommended for all new setups.

You now have everything needed to build simple notifications or complex automation workflows!  
If you need a specific example (e.g., Slack notification, auto-zip after upload), just ask. 🚀
