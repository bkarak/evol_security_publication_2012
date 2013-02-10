import os
import zipfile


def has_classes(filename):
    try:
        if zipfile.is_zipfile(filename):
            z = zipfile.ZipFile(filename)
            for f in z.namelist():
                if f.endswith('.class'):
                    print 'Valid JAR file: %s' % (filename,)
                    return True
        else:
            print '%s is not a zipfile (has_classes)' % (filename,)

        return False
    except Exception, e:
        return False


def get_jar_size(filename):
    size = 0

    if zipfile.is_zipfile(filename):
        try:
            z = zipfile.ZipFile(filename)
            for info in z.infolist():
                if info.filename.endswith('.class'):
                    size += info.file_size

            return size
        except Exception, e:
            return 0
    else:
        print '%s is not a zipfile (get_jar_size)' % (filename,)
        return 0


def get_metadata_from_url(url):
    url_arr = url.split('/')
    # -1: jar, -2: version, -3: artifact_id, remaining up to /maven2 -> groupId
    metadata = dict()
    metadata['jar_filename'] = url_arr[-1]
    metadata['version'] = url_arr[-2]
    metadata['artifact_id'] = url_arr[-3]
    metadata['group_id'] = reduce(lambda acc, x: acc + "." + x, url_arr[4:-3], "")[1:]
    return metadata


def convert_findbugs_xml(url, findbugs_xml):
    import xmldict
    import json

    result_json = json.loads(json.dumps(xmldict.parse(findbugs_xml)).replace('"@','"'))
    url_arr = get_metadata_from_url(url)

    # -1: jar, -2: version, -3: artifact_id, -4: group_id
    _jar_filename = metadata['jar_filename']
    _version = metadata['version']
    _artifact_id = metadata['artifact_id']
    _group_id = metadata['group_id']

    # get pom information
    _pom_url = url.replace('.jar', '.pom')
    _pom_filename = _jar_filename.replace('.jar', '.pom')

    log.info('Downloading POM: %s -> %s' % (_pom_url, _pom_filename))
    urllib.urlretrieve(_pom_url, _pom_filename)
    _dependencies = []

    if os.path.exists(_pom_filename):
        try:
            _pom_json = json.loads(json.dumps(xmldict.parse(open(_pom_filename, 'r').read())))
            _dependencies = _pom_json.get('project', {}).get('dependencies', {}).get('dependency', [])
        except Exception, e:
            log.warn('Could not download/parse data from %s' % (_pom_filename,))

        os.remove(_pom_filename)

    # get xml information
    _metadata_url = url.replace('%s/%s' % (_version, _jar_filename), 'maven-metadata.xml')
    _metadata_filename = '%s-metadata.xml' % (_jar_filename,)

    log.info('Downloading %s -> %s' % (_metadata_url, _metadata_filename))
    urllib.urlretrieve(_metadata_url, _metadata_filename)
    _version_order = 0

    if os.path.exists(_metadata_filename):
        try:
            _metadata_json = json.loads(json.dumps(xmldict.parse(open(_metadata_filename, 'r').read())))
            _versions = _metadata_json.get('metadata', {}).get('versioning', {}).get('versions', {}).get('version', [])

            if not isinstance(_versions, list):
                _versions = [_versions]

            _versions = [x.strip() for x in _versions]

            try:
                _version_order = _versions.index(_version.strip()) + 1
            except ValueError, ve:
                log.warn('Could not find version (%s): %s' % (_version, ve))
                _version_order = 0
        except Exception, e:
            log.warn('Could not parse data from %s: %s' % (_metadata_filename, e))

        os.remove(_metadata_filename)

    _jar_date = os.stat(file).st_mtime
    _jar_size = get_jar_size(file)
    result_json['JarMetadata'] = {'jar_filename':_jar_filename,
                                  'jar_last_modification_date':_jar_date,
                                  'jar_size':_jar_size,
                                  'version':_version,
                                  'version_list':_versions,
                                  'artifact_id':_artifact_id,
                                  'group_id':_group_id,
                                  'version_order' :_version_order,
                                  'dependencies':_dependencies}

    return result_json

def main():
    for (root, dirs, files) in os.walk('data/missing'):
        for f in files:
            pass


if __name__ == "__main__":
    main()

