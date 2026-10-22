#!/usr/bin/env python3
"""Locate or explicitly initialize a local named learner profile, using stdlib only.

Default root: ~/Study. --root explicitly selects another host-data root; the
reported absolute root is authoritative, not a promise of cross-device sync.
Profiles: <root>/learners/<slug>/learner-profile.json. Names contain only ASCII
letters, spaces, apostrophes, hyphens and periods (1–80 characters, with a letter).
Separators collapse to hyphens; case is ignored. Windows device names receive
'learner-' prefix. Existing identity collisions fail rather than merge learners.
Initialization publishes complete JSON through an exclusive hard link, never an
overwriting rename. Filesystems without hard links fail safely. No account,
provider integration, mastery estimate, or sync is created.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from study_check import Report, check_profile, read_json


def default_root():
    return Path.home() / 'Study'


def learner_identity(name):
    if not isinstance(name, str) or not 1 <= len(name) <= 80:
        raise ValueError('Name must be 1–80 ASCII characters.')
    if not re.fullmatch(r"[A-Za-z '.-]+", name) or not re.search('[A-Za-z]', name):
        raise ValueError('Use English ASCII letters, spaces, hyphens, apostrophes or periods; include a letter.')
    display = ' '.join(name.split())
    slug = re.sub('[^a-z]+', '-', display.lower()).strip('-')
    if re.fullmatch(r'con|prn|aux|nul|com[1-9]|lpt[1-9]', slug):
        slug = 'learner-' + slug
    return display, slug


def inspect_path(root, slug):
    path = root / 'learners' / slug / 'learner-profile.json'
    for part in (root / 'learners', path.parent, path):
        if part.is_symlink():
            raise ValueError('Refusing a symlink in learner profile path: ' + str(part))
    if path.exists() and not path.is_file():
        raise ValueError('Profile path is not a regular file.')
    return path


def validate_profile(path, name, slug):
    data = read_json(path)
    report = Report('profile')
    check_profile(data, path.parent, report)
    if report.data['errors']:
        raise ValueError('Existing profile is invalid; left unchanged: ' + '; '.join(x['message'] for x in report.data['errors']))
    stored_name = data.get('learner_name')
    stored_slug = data.get('learner_slug')
    if not isinstance(stored_name, str) or stored_name.casefold() != name.casefold() or stored_slug != slug:
        raise ValueError('Existing learner identity does not match; left unchanged.')
    return data


def initialize(root, path, name, slug):
    if path.exists():
        validate_profile(path, name, slug)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    inspect_path(root, slug)
    profile = {'schema_version': '1.0', 'learner_name': name, 'learner_slug': slug,
               'updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
               'goals': [], 'courses': [],
               'background': {key: [] for key in ('domains', 'coding', 'mathematics', 'language')},
               'preferences': [], 'teaching_observations': []}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.profile-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(profile, stream, ensure_ascii=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        inspect_path(root, slug)
        try:
            os.link(temporary, path)
            created = True
        except FileExistsError:
            created = False
        inspect_path(root, slug)
        validate_profile(path, name, slug)
        return created
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class JsonParser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({'success': False, 'error': message}))
        self.exit(2)


def main(argv=None):
    parser = JsonParser(description=__doc__)
    parser.add_argument('command', choices=('locate', 'init'))
    parser.add_argument('--name', required=True)
    parser.add_argument('--root', help='Explicit local host-data root (default: ~/Study)')
    args = parser.parse_args(argv)
    try:
        name, slug = learner_identity(args.name)
        if args.root is not None and not args.root.strip():
            raise ValueError('--root must be an explicit nonempty path.')
        root = (Path(args.root).expanduser() if args.root is not None else default_root()).resolve()
        path = inspect_path(root, slug)
        result = {'success': True, 'command': args.command, 'root': str(root),
                  'profile_path': str(path), 'learner_name': name, 'learner_slug': slug,
                  'exists': path.exists()}
        if args.command == 'init':
            created = initialize(root, path, name, slug)
            result.update(created=created, retained=not created, exists=True)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    sys.exit(main())
