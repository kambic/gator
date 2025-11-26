Here’s how to **configure multiple Celery queues** in your existing Ansible `celery` role — **production-ready**, **idempotent**, and **fully integrated with systemd**.

---

## Goal
Run **multiple Celery workers**, each consuming from **specific queues**:

| Queue | Purpose | Priority |
|------|--------|----------|
| `default` | General tasks | Medium |
| `high_priority` | Critical tasks (e.g., video encoding start) | High |
| `low_priority` | Background cleanup, emails | Low |

Each queue runs in a **separate systemd service** → independent scaling, monitoring, and restarts.

---

## 1. Update `roles/celery/vars/main.yml`

```yaml
# ------------------------------------------------------------------
# Celery Queues Configuration
# ------------------------------------------------------------------
celery_queues:
  default:
    concurrency: 4
    loglevel: INFO
  high_priority:
    concurrency: 2
    loglevel: WARNING
  low_priority:
    concurrency: 6
    loglevel: INFO

celery_broker_url: "redis://{{ redis_host }}:{{ redis_port }}/0"
celery_result_backend: "redis://{{ redis_host }}:{{ redis_port }}/1"
celery_beat_schedule_file: "{{ app_path }}/celerybeat-schedule"
celery_log_level: "INFO"

redis_host: "127.0.0.1"
redis_port: 6379
```

---

## 2. Create Template: `roles/celery/templates/celery-worker@.service.j2`

This is a **systemd template unit** — allows multiple instances.

```ini
[Unit]
Description=Celery worker for CMS - queue {{ queue_name }}
After=network.target redis-server.service
PartOf=celery-cms.target

[Service]
Type=simple
User={{ deploy_user }}
Group={{ deploy_group }}
WorkingDirectory={{ app_path }}
Environment="PATH={{ app_path }}/venv/bin"
Environment="DJANGO_SETTINGS_MODULE={{ django_settings_module }}"
Environment="CELERY_BROKER_URL={{ celery_broker_url }}"
Environment="CELERY_RESULT_BACKEND={{ celery_result_backend }}"

ExecStart={{ app_path }}/venv/bin/celery \
  -A cms.celery.app worker \
  -Q {{ queue_name }} \
  --loglevel={{ queue_config.loglevel }} \
  --concurrency={{ queue_config.concurrency }} \
  --hostname=worker-{{ queue_name }}@%h

ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## 3. Add `celery-cms.target` (Optional but Clean)

`roles/celery/templates/celery-cms.target.j2`

```ini
[Unit]
Description=Celery CMS Workers Target
After=network.target

[Install]
WantedBy=multi-user.target
```

---

## 4. Update `tasks/main.yml`

```yaml
---
- name: Install Redis
  apt:
    name: redis-server
    state: present
  become: yes

- name: Ensure Redis is running
  service:
    name: redis-server
    state: started
    enabled: yes
  become: yes

- name: Install Celery in virtualenv
  pip:
    name:
      - celery[redis]
      - redis
    virtualenv: "{{ app_path }}/venv"
  become_user: "{{ deploy_user }}"

# --- Deploy per-queue workers ---
- name: Deploy Celery worker units (per queue)
  template:
    src: celery-worker@.service.j2
    dest: "/etc/systemd/system/celery-cms@{{ item.key }}.service"
    mode: "0644"
  loop: "{{ celery_queues | dict2items }}"
  loop_control:
    label: "{{ item.key }}"
  become: yes
  notify:
    - reload systemd
    - restart celery worker

- name: Deploy Celery target (groups all workers)
  template:
    src: celery-cms.target.j2
    dest: /etc/systemd/system/celery-cms.target
    mode: "0644"
  become: yes
  notify: reload systemd

# --- Celery Beat (Scheduler) ---
- name: Deploy Celery beat service
  template:
    src: celerybeat.service.j2
    dest: /etc/systemd/system/celerybeat-cms.service
    mode: "0644"
  become: yes
  notify:
    - reload systemd
    - restart celerybeat

# --- Enable & Start ---
- name: Enable Celery target
  systemd:
    name: celery-cms.target
    enabled: yes
  become: yes

- name: Enable and start per-queue workers
  systemd:
    name: "celery-cms@{{ item.key }}.service"
    enabled: yes
    state: started
  loop: "{{ celery_queues | dict2items }}"
  loop_control:
    label: "{{ item.key }}"
  become: yes

- name: Enable and start Celery beat
  systemd:
    name: celerybeat-cms
    enabled: yes
    state: started
  become: yes
```

---

## 5. Keep `celerybeat.service.j2` (unchanged)

```ini
[Unit]
Description=Celery beat scheduler for CMS
After=network.target redis-server.service

[Service]
Type=simple
User={{ deploy_user }}
Group={{ deploy_group }}
WorkingDirectory={{ app_path }}
Environment="PATH={{ app_path }}/venv/bin"
Environment="DJANGO_SETTINGS_MODULE={{ django_settings_module }}"
Environment="CELERY_BROKER_URL={{ celery_broker_url }}"

ExecStart={{ app_path }}/venv/bin/celery \
  -A cms.celery.app beat \
  --loglevel={{ celery_log_level }} \
  --schedule={{ celery_beat_schedule_file }} \
  --pidfile={{ app_path }}/celerybeat.pid

ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## 6. Update `handlers/main.yml`

```yaml
---
- name: reload systemd
  systemd:
    daemon_reload: yes
  become: yes

- name: restart celery worker
  systemd:
    name: "celery-cms@{{ item.key }}.service"
    state: restarted
  loop: "{{ celery_queues | dict2items }}"
  loop_control:
    label: "{{ item.key }}"
  become: yes
  when: item.value is defined

- name: restart celerybeat
  systemd:
    name: celerybeat-cms
    state: restarted
  become: yes
```

> **Note**: Handlers run **once per play**, but we loop over queues to restart all.

---

## 7. How to Use in Code

In your tasks:

```python
# ping.py
from celery import shared_task

@shared_task(queue='high_priority')
def encode_video(video_id):
    ...

@shared_task(queue='low_priority')
def send_weekly_report():
    ...

@shared_task  # goes to 'default'
def cleanup_temp_files():
    ...
```

---

## 8. Management Commands

```bash
# Check status
sudo systemctl status celery-cms@default
sudo systemctl status celery-cms@high_priority

# Logs
journalctl -u celery-cms@high_priority -f

# Scale
sudo systemctl stop celery-cms@low_priority
sudo systemctl start celery-cms@low_priority
```

---

## 9. Scaling Example

Update `vars/main.yml`:

```yaml
celery_queues:
  default:
    concurrency: 4
  high_priority:
    concurrency: 2
  low_priority:
    concurrency: 10   # handle backlog
```

Re-run playbook → only changed workers restart.

---

## Result

| Service | Queue | Concurrency | Logs |
|--------|-------|-------------|------|
| `celery-cms@default.service` | `default` | 4 | `journalctl -u celery-cms@default` |
| `celery-cms@high_priority.service` | `high_priority` | 2 | `...` |
| `celery-cms@low_priority.service` | `low_priority` | 6 | `...` |
| `celerybeat-cms.service` | (scheduler) | — | `...` |

All managed under `celery-cms.target`:

```bash
sudo systemctl status celery-cms.target
```

---

**Done.**  
You now have **fine-grained queue control**, **independent scaling**, and **zero-downtime updates** via Ansible.

Run:

```bash
ansible-playbook ansible/playbook.yml -i ansible/inventory --ask-vault-pass
```

Let me know if you want:
- Prometheus metrics per queue
- Flower dashboard
- Auto-scaling based on queue length


## Ansible Deployment for Your Django CMS Project

Based on your project structure (with split settings in `cms/settings/`, Gunicorn config, PostgreSQL DB, and existing Ansible `inventory` + `playbook.yml`), I'll provide a **complete, production-ready Ansible playbook** to deploy to a server. This assumes:

- **Server**: Ubuntu 22.04 LTS (common for Django; adjust if needed).
- **Stack**: Git → Virtualenv → PostgreSQL → Django migrations → Gunicorn (systemd) → Nginx (reverse proxy) → Let's Encrypt SSL.
- **Repo**: Your project is in a Git repo (e.g., GitHub/GitLab). Update `git_repo` in vars.
- **User**: Deploys as a non-root user (e.g., `deploy`) with sudo privileges.
- **Database**: Creates a PostgreSQL DB/user.
- **Environment**: Sets `DJANGO_SETTINGS_MODULE=cms.settings.production`.
- **Secrets**: Use Ansible Vault for sensitive vars (e.g., DB password, Django SECRET_KEY).

This builds on popular patterns from established playbooks like [jcalazan/ansible-django-stack](https://github.com/jcalazan/ansible-django-stack) and [myarik/django-ansible-setup](https://github.com/myarik/django-ansible-setup), adapted for your split settings and systemd (modern replacement for Supervisor).

---

### Step 1: Prerequisites

1. **Install Ansible** (if not already):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install ansible

   # Or via pip
   pip install ansible
   ```

2. **Setup SSH Access**:
   - Generate an SSH keypair if needed: `ssh-keygen -t ed25519 -C "your-email@example.com"`.
   - Add your public key to the server: `ssh-copy-id deploy@your-server-ip`.
   - Test: `ssh deploy@your-server-ip` (passwordless login).

3. **Git Repo**: Ensure your project is pushed to a repo. Add `.gitignore` for `venv/`, `.env`, etc.

4. **Ansible Vault for Secrets**:
   - Create `group_vars/vault.yml` (encrypted):
     ```bash
     ansible-vault create group_vars/vault.yml
     ```
   - Inside (edit with `ansible-vault edit`):
     ```yaml
     db_password: "your-secure-db-password"
     django_secret_key: "your-secure-django-secret-key"  # Generate with django.core.management.utils.get_random_secret_key()
     ```

---

### Step 2: Update Your Ansible Structure

Your existing `ansible/` dir looks good. Expand it like this:

```
ansible/
├── inventory          # Your hosts file (e.g., [production] your-server-ip ansible_user=deploy)
├── playbook.yml       # Main playbook (update below)
├── roles/             # Create these dirs
│   ├── common/        # Base setup (packages, user, firewall)
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── handlers/
│   │       └── main.yml
│   ├── postgresql/    # DB setup
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── vars/
│   │       └── main.yml
│   ├── django/        # App deployment
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── templates/
│   │       ├── gunicorn.service.j2
│   │       └── nginx.conf.j2
│   └── certbot/       # SSL (optional)
│       └── tasks/
│           └── main.yml
└── group_vars/
    ├── all.yml        # Common vars
    └── vault.yml       # Secrets (encrypted)
```

---

### Step 3: Inventory File (`ansible/inventory`)

Example for a single production server:

```ini
[production]
your-server-ip ansible_user=deploy ansible_ssh_private_key_file=~/.ssh/id_ed25519

[production:vars]
ansible_python_interpreter=/usr/bin/python3
deploy_user=deploy
deploy_group=deploy
app_path=/home/{{ deploy_user }}/sites/cms
git_repo=https://github.com/yourusername/mediacms.git  # Update to your repo
db_name=cms_production
db_user=cms_user
```

---

### Step 4: Group Vars

`ansible/group_vars/all.yml` (non-sensitive):

```yaml
# App config
django_settings_module: cms.settings.production
gunicorn_port: 8000
gunicorn_workers: 4
gunicorn_threads: 2
nginx_port: 80
ssl_email: your-email@example.com  # For Let's Encrypt

# Django-specific
allowed_hosts: ["your-domain.com", "your-server-ip"]  # Update
```

`ansible/group_vars/vault.yml` (encrypted, as above).

---

### Step 5: Roles Implementation

#### Role: common (`roles/common/tasks/main.yml`)

Base system setup.

```yaml
---
- name: Update apt cache
  apt:
    update_cache: yes
    cache_valid_time: 3600

- name: Install base packages
  apt:
    name:
      - software-properties-common
      - python3
      - python3-pip
      - python3-venv
      - git
      - curl
      - ufw
      - fail2ban
    state: present

- name: Create deploy user
  user:
    name: "{{ deploy_user }}"
    groups: sudo
    shell: /bin/bash
    create_home: yes
    state: present

- name: Allow SSH for deploy user
  lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^AllowUsers'
    line: "AllowUsers {{ deploy_user }} root"
  notify: restart ssh

- name: Setup firewall (UFW)
  ufw:
    state: enabled
    policy: deny
  notify: ufw allow ssh

- name: Enable UFW
  ufw:
    state: enabled

handlers:
- name: restart ssh
  service:
    name: ssh
    state: restarted

- name: ufw allow ssh
  ufw:
    rule: allow
    port: 22
    proto: tcp
```

#### Role: postgresql (`roles/postgresql/tasks/main.yml`)

DB setup.

```yaml
---
- name: Add PostgreSQL repo
  apt_repository:
    repo: "deb http://apt.postgresql.org/pub/repos/apt/ {{ ansible_distribution_release }}-pgdg main"
    state: present
    filename: pgdg

- name: Add PostgreSQL GPG key
  apt_key:
    url: https://www.postgresql.org/media/keys/ACCC4CF8.asc
    state: present

- name: Install PostgreSQL
  apt:
    name:
      - postgresql
      - postgresql-contrib
      - libpq-dev
    state: present
    update_cache: yes

- name: Ensure PostgreSQL is running
  service:
    name: postgresql
    state: started
    enabled: yes

- name: Create DB user
  become: yes
  become_user: postgres
  postgresql_user:
    name: "{{ db_user }}"
    password: "{{ db_password }}"
    role_attr_flags: CREATEDB

- name: Create DB
  become: yes
  become_user: postgres
  postgresql_db:
    name: "{{ db_name }}"
    owner: "{{ db_user }}"

- name: Update Django DATABASES in settings/production.py
  lineinfile:
    path: "{{ app_path }}/cms/settings/production.py"
    regexp: '^DATABASES'
    line: |
      DATABASES = {
          'default': {
              'ENGINE': 'django.db.backends.postgresql',
              'NAME': '{{ db_name }}',
              'USER': '{{ db_user }}',
              'PASSWORD': '{{ db_password }}',
              'HOST': 'localhost',
              'PORT': '5432',
          }
      }
  # This runs after deployment; use template if preferred
```

#### Role: django (`roles/django/tasks/main.yml`)

Deploy app, setup Gunicorn/systemd.

```yaml
---
- name: Clone repo
  git:
    repo: "{{ git_repo }}"
    dest: "{{ app_path }}"
    version: main  # Or tag/branch
    force: yes
  become_user: "{{ deploy_user }}"

- name: Create virtualenv
  pip:
    name: "."
    virtualenv: "{{ app_path }}/venv"
    virtualenv_command: python3 -m venv
    requirements: "{{ app_path }}/requirements.txt"  # Or pyproject.toml if using that
  become_user: "{{ deploy_user }}"

- name: Install Gunicorn in venv
  pip:
    name: gunicorn
    virtualenv: "{{ app_path }}/venv"
  become_user: "{{ deploy_user }}"

- name: Run Django migrations
  django_manage:
    command: migrate
    app_path: "{{ app_path }}"
    virtualenv: "{{ app_path }}/venv"
    settings: "{{ django_settings_module }}"
  environment:
    DJANGO_SETTINGS_MODULE: "{{ django_settings_module }}"
    DJANGO_SECRET_KEY: "{{ django_secret_key }}"
    DJANGO_ALLOWED_HOSTS: "{{ allowed_hosts | join(',') }}"
  become_user: "{{ deploy_user }}"

- name: Collect static files
  django_manage:
    command: collectstatic --noinput
    app_path: "{{ app_path }}"
    virtualenv: "{{ app_path }}/venv"
    settings: "{{ django_settings_module }}"
  environment:
    DJANGO_SETTINGS_MODULE: "{{ django_settings_module }}"
  become_user: "{{ deploy_user }}"

- name: Create Gunicorn systemd service
  template:
    src: gunicorn.service.j2
    dest: /etc/systemd/system/gunicorn-cms.service
  notify: restart gunicorn

- name: Enable and start Gunicorn
  systemd:
    name: gunicorn-cms
    enabled: yes
    state: started
    daemon_reload: yes

- name: Create media/static dirs
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ deploy_user }}"
    group: "{{ deploy_group }}"
    mode: '0755'
  loop:
    - "{{ app_path }}/staticfiles"
    - "{{ app_path }}/media"

handlers:
- name: restart gunicorn
  systemd:
    name: gunicorn-cms
    state: restarted
```

**Template: `roles/django/templates/gunicorn.service.j2`**

```ini
[Unit]
Description=Gunicorn instance for CMS
After=network.target

[Service]
User={{ deploy_user }}
Group=www-data
WorkingDirectory={{ app_path }}
Environment="PATH={{ app_path }}/venv/bin"
Environment="DJANGO_SETTINGS_MODULE={{ django_settings_module }}"
Environment="DJANGO_SECRET_KEY={{ django_secret_key }}"
Environment="DJANGO_ALLOWED_HOSTS={{ allowed_hosts | join(',') }}"

ExecStart=/bin/bash -c '{{ app_path }}/venv/bin/gunicorn --config {{ app_path }}/gunicorn.py cms.wsgi:application'
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Role: certbot (`roles/certbot/tasks/main.yml`) – Optional SSL

```yaml
---
- name: Install Certbot
  apt:
    name:
      - certbot
      - python3-certbot-nginx
    state: present

- name: Generate Nginx config (before Certbot)
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/cms
  notify: restart nginx

- name: Enable site
  file:
    src: /etc/nginx/sites-available/cms
    dest: /etc/nginx/sites-enabled/cms
    state: link

- name: Run Certbot
  certbot:
    name: "{{ allowed_hosts[0] }}"  # Domain
    email: "{{ ssl_email }}"
    webroot: yes
    webroot_path: "{{ app_path }}/staticfiles"
  notify: restart nginx
```

**Template: `roles/django/templates/nginx.conf.j2`** (Basic; Certbot will enhance for HTTPS)

```nginx
server {
    listen 80;
    server_name {{ allowed_hosts[0] }};

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root {{ app_path }};
    }

    location /media/ {
        root {{ app_path }};
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/gunicorn.sock;  # Or http://127.0.0.1:{{ gunicorn_port }}
    }
}
```

Add Nginx install to `common/tasks/main.yml`:

```yaml
- name: Install Nginx
  apt:
    name: nginx
    state: present

- name: Start Nginx
  service:
    name: nginx
    state: started
    enabled: yes
```

---

### Step 6: Main Playbook (`ansible/playbook.yml`)

Update your existing `playbook.yml`:

```yaml
---
- name: Deploy CMS Production Stack
  hosts: production
  become: yes
  vars_files:
    - group_vars/all.yml
    - group_vars/vault.yml
  roles:
    - common
    - postgresql
    - django
    - certbot  # Optional
  post_tasks:
    - name: Test Django
      uri:
        url: "http://{{ allowed_hosts[0] }}"
        status_code: 200
      register: django_test
    - debug:
        msg: "Deployment successful! Status: {{ django_test.status }}"
```

---

### Step 7: Deploy!

From your project root:

```bash
# Dry run (idempotent check)
ansible-playbook ansible/playbook.yml -i ansible/inventory --ask-vault-pass --check

# Full deploy
ansible-playbook ansible/playbook.yml -i ansible/inventory --ask-vault-pass

# For updates: Just re-run (it pulls latest Git, migrates, restarts services)
```

- **First run**: ~10-15 mins (installs everything).
- **Updates**: ~1-2 mins (git pull, pip install, migrate, restart).
- **Logs**: Check `/var/log/gunicorn/` or `journalctl -u gunicorn-cms`.
- **Domain**: Point DNS A record to `your-server-ip`.

---

### Customization Notes

| Component | Customization |
|-----------|---------------|
| **Git Repo** | Update `git_repo` in inventory. For private: Use SSH key deploy (add `ansible_ssh_private_key_file`). |
| **Requirements** | If using `pyproject.toml` + `uv` (from your structure), update pip task to `uv pip install -r requirements.txt` (install `uv` in common role). |
| **Celery** | Your project has Celery (`celery.py`); add a role like `celery` with systemd unit (similar to Gunicorn). |
| **Split Settings** | The env var ensures `production.py` loads. Add more env vars (e.g., `ALLOWED_HOSTS`) via `lineinfile` or templates. |
| **Scaling** | For multiple servers: Add to inventory `[production:children] web:children db`. |
| **Troubleshooting** | Use `-vvv` for verbose: `ansible-playbook ... -vvv`. Common issues: Firewall (ufw status), DB connection (psql -U cms_user). |

This deploys a secure, auto-restarting stack. Test on a staging server first! If you share your `playbook.yml` or errors, I can refine.
