import os
import re
import hashlib
import shutil
import json
import itertools


_DIRNAME, _FILENAME = os.path.split(os.path.abspath(__file__))
_TAR_DIR = os.path.join(_DIRNAME, "build")

_version_dict = {}
_target_files = []
_suffix_regex = re.compile("\.([\-_\w\d]+)$")
_version_file_regex = re.compile(
    "[\"\']([^\"\']+?\.[\-_\w\d]+)\?v=VERSION[\"\']"
)


def get_short_repr(path):
    return re.sub(r"[/\\\.]", "", path)


def get_config(config_file_path):
    conf_file = open(config_file_path, "r")
    conf_content = conf_file.read()
    conf = json.loads(conf_content)
    conf_file.close()
    return conf


def get_version_files(config):

    print "[INFO] Getting files needed to be set version ..."
    paths = config["include"] if "include" in config else ["."]
    suffix = config["suffix"] if "suffix" in config else [""]
    exclude = config["exclude"] if "exclude" in config else []
    entry = config["entry"] if "entry" in config else []

    for folder, dirs, files in \
            itertools.chain(*[os.walk(path) for path in paths]):

        is_in_exclude = reduce(
            lambda s, x: s or (get_short_repr(x) in get_short_repr(folder)),
            exclude,
            False
        )

        if is_in_exclude:
            continue

        for f in files:
            is_in_suffix = reduce(
                lambda s, x: s or f.endswith(x),
                suffix,
                False
            )
            _f_short_repr = get_short_repr(os.path.join(folder, f))
            is_in_entry = reduce(
                lambda s, x: s or (_f_short_repr == get_short_repr(x)),
                entry,
                False
            )
            if is_in_suffix and not is_in_entry:
                print "[INFO] Added file '%s' \
                        in folder '%s' into list" % (f, folder)

                print get_short_repr(os.path.join(folder, f))
                print folder, f
                print suffix
                yield os.path.join(folder, f)


def get_base64_encoded_md5(file_path):

    print "[INFO] Getting base64 of file '%s'" % file_path

    f = open(file_path, "rb")
    m = hashlib.md5()

    buff = f.read(1024)
    while (len(buff) > 0):
        m.update(buff)
        buff = f.read(1024)
    f.close()

    return m.hexdigest()[-10:]


def organize_files(config):

    if os.path.exists(_TAR_DIR):
        shutil.rmtree(_TAR_DIR)
    os.makedirs(_TAR_DIR)

    entry = config["entry"] if "entry" in config else []

    print "[INFO] Moving entry files into build folder ..."
    for f in entry:
        shutil.copy2(f, _TAR_DIR)
        _target_files.append(os.path.join(_TAR_DIR, f))

    print "[INFO] Organizing files ..."
    for f in get_version_files(config):

        b64_string = get_base64_encoded_md5(f)
        suffix = "." + _suffix_regex.search(f).group(1)
        target_dir = os.path.join(_TAR_DIR, f)
        _version_dict[get_short_repr(f)] = b64_string
        target_file = os.path.join(target_dir, b64_string + suffix)
        _target_files.append(target_file)

        if not os.path.exists(target_file):
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            shutil.copy2(f, target_file)


def copy_unchange_files(config):

    print "[INFO] Moving unchange files into build folder ..."
    unchange = config["unchange"] if "unchange" in config else []
    for folder in unchange:
        shutil.copytree(folder, os.path.join(_TAR_DIR, folder))


def replace_built_files():

    print "[INFO] Replacing 'VERSION' in source code ..."
    for f in _target_files:
        print "[INFO] Replacing 'VERSION' in file '%s' ..." % f
        _f = open(f, "r")
        _c = _f.read()
        _f.close()
        for i in _version_file_regex.finditer(_c):
            key = get_short_repr(i.group(1))
            base64 = _version_dict[key]
            origin = i.group()
            real = origin.replace("VERSION", base64)
            _c = _c.replace(origin, real)
        _f = open(f, "w")
        _f.write(_c)
        _f.close()


if __name__ == "__main__":
    print "[INFO] Running This Tool ..."
    config = get_config("ciconf.json")
    organize_files(config)
    replace_built_files()
    copy_unchange_files(config)
    print "[INFO] Finished"
